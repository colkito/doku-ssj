# 𓆰𓆪 doku-ssj

Ey, ey, bienvenidos a doku-ssj, el chatbot que la rompe con tus docus locales. Directo desde el under de la IA, con el flow del trap argento. 🔥📚

## ¿Qué onda con este proyecto?

Doku-ssj es como ese pibe del barrio que se las sabe todas. Usando [LlamaIndex](https://github.com/run-llama/llama_index), [Chroma](https://github.com/chroma-core/chroma) y [Ollama](https://github.com/ollama/ollama), este bot procesa tus docs y te tira la posta como si fuera freestyle. No más buscar como un gil, ahora tenés la data al toque.

¿Por qué armé este proyecto? Porque soy un cabrón, papá. Me cansé de ver a la gente perdiendo tiempo buscando info en sus propios archivos. Acá les traigo la solución, local, directo y sin vueltas. Esto es "inteligencia artificial pa' que me copien", pero con tu propia data.

### Características que la rompen:

- 🧠 Modelos locales con Ollama (porque acá no dependemos de nadie, ¿tá claro?)
- 💾 Guardamos los embeddings con Chroma (más veloz que Messi esquivando rivales)
- 🦙 LlamaIndex integrado (armando flows más enredados que los auriculares en tu bolsillo)
- 📄 Soporte actual para PDF, HTML y Markdown (y vienen más en camino, ¡aguante!)

## Cómo bajártelo

1. Cloná el repo, así:

```sh
git clone https://github.com/colkito/doku-ssj.git
cd doku-ssj
```

2. Instalá todo, metele:

```sh
pip install -r requirements.txt
```

3. Asegurate de tener Ollama instalado y corriendo en tu máquina. Si no lo tenés, bajalo de [acá](https://ollama.com/).

4. Configurá tu movida:

   El archivo `.env` en la raíz del proyecto ya viene con la justa, pero si te pinta cambiar algo, dale:

- `OLLAMA_BASE_URL`: La dirección donde Ollama está haciendo la magia. Por defecto: `http://localhost:11434`.
- `OLLAMA_CHAT_MODEL`: El modelo que usa para chatear. Viene con `llama3:latest`, pero si tenés otro con más flow, mandate.
- `OLLAMA_EMBEDDING_MODEL`: El que convierte las palabras en números. Arranca con `nomic-embed-text:latest`.
- `CHROMA_PATH`: Donde guarda toda la data procesada. Por defecto: `./chroma_db`.
- `CHROMA_COLLECTION_NAME`: El nombre de la colección en Chroma. Arranca como `doku`.
- `CHROMA_ANONYMIZED_TELEMETRY`: Si querés mandar data anónima pa' mejorar Chroma. Viene en `False` porque acá no buchoneamos.
- `DATA_PATH`: Donde tiras tus docs para que Doku los mastique. Arranca en `./data`.

## Cómo usarlo

Es fácil, bro:

1. Metele tus docs en la carpeta `./data`. El bot lee archivos PDF, HTML y Markdown (próximamente más formatos, estate atento).

2. Corré el bot:

```sh
python doku_cli.py
```

3. Chateá con el bot como si fuera tu dealer de conocimiento. Tirá tus preguntas y el bot te va a responder con la data de tus docs.

4. Cuando te pinte cortar, tirate un 'chau' y listo. (Si sos más del palo old school, 'quit' también va)

## Próximamente

- 📚 Soporte para más tipos de archivos (doc, docx, txt, y lo que se te ocurra)
- 🚀 Mejoras en la velocidad y precisión
- 🎤 Personalización del flow de la respuesta

## Metele mano si te la bancás

¿Te pintó mejorar doku-ssj? Demostrá lo que sabés. Tirá un issue o mandá un pull request. Mientras no la cagues, todo piola. Acá respetamos a los que le meten ganas y código.

## Solución de problemas

Si algo no funca:

1. Fijate que Ollama esté corriendo
2. Chequeá que los modelos estén bajados (`llama3` y `nomic-embed-text` van de fábrica)
3. Si seguís en el horno, abrí un issue y lo vemos juntos

## La gilada legal

Bajo la Licencia MIT. Usalo, hacelo mierda, regalalo, vendelo, lo que se te cante. El conocimiento es free, como el Wi-Fi del vecino.

---

Hecho con 🖤 y mucho Fernet en la tierra del Diego.
Inspirado en el flow de los que la rompen, pero sin giladas. Código puro, como trago sin hielo.
