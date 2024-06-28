"""
Doku CLI Module

Este es el cerebro de Doku, el chatbot más picante del barrio tech.
Carga una base de conocimientos custom de páginas web, PDFs y archivos Markdown,
los mete en Chroma DB y los usa para tirar respuestas con toda la onda a tus preguntas.
Es como tener un MC de la información en tu terminal, ¿tá?
"""

import os
import sys
import logging
from typing import Generator, List
import httpx
from dotenv import load_dotenv

from ollama import Client as OllamaClient, ResponseError
import chromadb
from chromadb.config import Settings as ChromaSettings

from llama_index.core import (
    Document,
    PromptTemplate,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

# Carga de variables de ambiente, para no mandarnos cagadas
load_dotenv()

# Constantes, como el flow que no cambia
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3:latest")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text:latest")

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "doku")
CHROMA_ANONYMIZED_TELEMETRY = os.getenv("ANONYMIZED_TELEMETRY", "False")

DATA_PATH = os.getenv("DATA_PATH", "./data")

ALLOWED_EXTENSIONS = [".pdf", ".html", ".md"]

# Setup de logs, pa' saber qué onda si algo se va a la mierda
logging.basicConfig(level=logging.ERROR, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_and_process_documents() -> List[Document]:
    """
    Carga y procesa los documentos del barrio de datos.

    Returns:
        List[Document]: Una lista de documentos listos para el freestyle.
    """
    documents = []
    total_files = sum(
        len(
            [
                f
                for f in files
                if any(f.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)
            ]
        )
        for _, _, files in os.walk(DATA_PATH)
    )
    processed_files = 0

    print(f"Cargando data de {total_files} archivos, aguantá un toque...")

    for root, _, paths in os.walk(DATA_PATH):
        for path in paths:
            if any(path.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
                file_path = os.path.join(root, path)
                reader = SimpleDirectoryReader(
                    input_files=[file_path], filename_as_id=True
                )
                docs = reader.load_data()
                for doc in docs:
                    doc.metadata.update({"source": file_path})
                documents.extend(docs)
                processed_files += 1
                print(f"Ya van {processed_files}/{total_files} archivos", end="\r")

    print(f"\nListo, pá. Tenemos {total_files} archivos cargados")
    return documents


def create_or_load_index() -> VectorStoreIndex:
    """
    Arma un índice nuevo o carga uno que ya existe.
    Es como preparar la base para el freestyle.

    Returns:
        VectorStoreIndex: El índice listo para rockear.
    """
    Settings.llm = Ollama(model=OLLAMA_CHAT_MODEL, base_url=OLLAMA_BASE_URL)
    Settings.embed_model = OllamaEmbedding(
        model_name=OLLAMA_EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL
    )
    Settings.chunk_size = 512
    Settings.chunk_overlap = 50

    db = chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=ChromaSettings(anonymized_telemetry=CHROMA_ANONYMIZED_TELEMETRY),
    )

    try:
        chroma_collection = db.get_collection(CHROMA_COLLECTION_NAME)
        print("Cargando la base de conocimientos, un segundo...")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store, storage_context=storage_context
        )
        print("Base de conocimientos cargada, estamos ready")

    except Exception:
        print("Creando una base de conocimientos nueva, dame un toque...")
        documents = load_and_process_documents()
        chroma_collection = db.get_or_create_collection(CHROMA_COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context, show_progress=True
        )
        print("Base de conocimientos creada, ahora sí estamos")

    return index


def model_response_generator(
    query: str, index: VectorStoreIndex
) -> Generator[str, None, None]:
    """
    Genera una respuesta a la pregunta del usuario usando el índice.
    Es como improvisar con tus propios samples.

    Args:
        query (str): La pregunta del usuario, su beat.
        index (VectorStoreIndex): El índice para buscar la data relevante.

    Yields:
        str: Pedazos de la respuesta generada, como versos en el aire.
    """
    try:
        prompt_template_str = """
Context information is below.
----------------------
{context_str}
----------------------
Given the provided context excerpts from documentation files, and not prior knowledge, create a final answer to the question asked. ONLY use information from the excerpts as references in your response and respond ALWAYS in Spanish.

Instructions:
1. Provide a direct answer to the question using ONLY the information from the provided excerpts.
2. ONLY if there is enough information, include at the bottom a "FUENTES" section listing the minimal set of sources files needed to answer the question. Use this format for PDF sources: "- <file_path> (pages numbers or lines numbers)" and use this format for non-PDF sources: "- <file_path>".
3. If there is not enough information in the excerpts to answer the question, respond with the statement "I do not have enough information to answer this question." and suggest to refine the question. Do not include "FUENTES", and NEVER provide any additional details, examples, or current context if there is not enough information.
4. If the question or answer involves steps or procedures, include them in a numbered or bulleted list within the answer for clarity.

Query: {query_str}
Answer: 
        """

        qa_template = PromptTemplate(prompt_template_str)

        query_engine = index.as_query_engine(
            text_qa_template=qa_template,
            streaming=True,
            similarity_top_k=3,
        )
        streaming_response = query_engine.query(query)

        for chunk in streaming_response.response_gen:
            yield chunk

    except httpx.HTTPError as e:
        error_msg = f"Se pudrió todo procesando tu pregunta: {str(e)}"
        logger.error(error_msg)
        yield error_msg
    except Exception as e:
        error_msg = f"Pasó algo que ni yo me la esperaba: {str(e)}"
        logger.error(error_msg, exc_info=True)
        yield "Perdona, wacho, pero se me trabó el cassette. Probá de nuevo en un toque."


def initialize_models() -> None:
    """
    Inicializa los modelos de chat y embedding.
    Es como afinar los instrumentos antes del show.
    """
    ollama = OllamaClient(host=OLLAMA_BASE_URL)

    for model in [OLLAMA_CHAT_MODEL, OLLAMA_EMBEDDING_MODEL]:
        try:
            ollama.show(model)
            print(f"El modelo {model} ya está cargado y listo")
        except ResponseError as e:
            if e.status_code == 404:
                print(f"Bajando el modelo {model}, aguantá...")
                ollama.pull(model)
                print(f"Modelo {model} bajado y cargado, una joya")
        except httpx.ConnectError:
            error_msg = "No puedo conectarme: Fijate si Ollama está corriendo en %s"
            logger.error(error_msg, OLLAMA_BASE_URL)
            sys.exit(1)


def main():
    """
    Función principal para correr la app CLI.
    Acá es donde Doku se pone los auriculares y empieza a tirar flow.
    """
    print("Doku se está preparando para el show...")
    initialize_models()
    index = create_or_load_index()

    print("\n¡Doku está listo para romperla! Tirate un 'quit' cuando quieras cortar.")

    while True:
        query = input("\nVos: ")
        if query.lower() == "quit":
            print("¡Nos vemos en la próxima, wacho!")
            break

        print("\nDoku: ", end="")
        for chunk in model_response_generator(query, index):
            print(chunk, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    main()
