📚 Judicial Sentence Analyzer
Un sistema automatizado desarrollado con n8n y Python para analizar sentencias judiciales en formato de documento. Extrae los asuntos más relevantes, identifica los hechos jurídicos importantes y diferencia entre la justificación y el fallo, ofreciendo una herramienta de estudio y análisis jurídico especialmente útil para estudiantes, abogados y jueces.

🚀 Objetivo del Proyecto
Crear una aplicación que:

Permita cargar sentencias judiciales (PDF, Word).

Analice el contenido con modelos de NLP personalizados.

Clasifique partes clave del texto: asuntos tratados, hechos relevantes, fundamentación, decisión.

Automatice el flujo de trabajo mediante n8n para facilitar integración con otros servicios o aplicaciones.

🧠 Tecnologías utilizadas
⚙️ n8n: herramienta de automatización para orquestar los flujos de carga y análisis.

🐍 Python: procesamiento de lenguaje natural y extracción de información.

📄 OCR (Tesseract o similar): para convertir imágenes escaneadas en texto (si aplica).

🤖 NLP: modelos de lenguaje entrenados o preentrenados (SpaCy, transformers, etc.).

🧪 FastAPI (opcional): si se quiere convertir el backend en una API.

📊 Frontend simple o dashboard (opcional) para visualizar resultados.

📁 Estructura del Repositorio
bash
Copiar
Editar
judicial-sentence-analyzer/
│
├── workflows/
│   └── analyze-sentence.n8n.json      # Flujo de trabajo n8n para cargar y procesar documentos
│
├── backend/
│   ├── extractor.py                   # Código principal de extracción y análisis en Python
│   ├── models/                        # Modelos de NLP y lógica de segmentación
│   └── utils/                         # Utilidades para parsing, OCR, limpieza de texto, etc.
│
├── docs/
│   └── ejemplo_sentencia.pdf         # Ejemplos de sentencias y resultados procesados
│
├── README.md                         # Documentación del proyecto
└── requirements.txt                  # Dependencias de Python
🧩 Cómo funciona
Carga de sentencia: el usuario carga una sentencia judicial (PDF o Word) a través de una interfaz, API o carpeta compartida.

n8n Workflow: se activa el flujo que llama a un script de Python.

Análisis en Python:

Limpieza del texto.

Identificación de secciones clave.

Clasificación del contenido (asuntos, hechos, justificación, fallo).

Resultado: se almacena como JSON o se envía por correo, API o interfaz web.

✅ Casos de uso
Preparación para exámenes orales de derecho.

Estudio jurisprudencial automatizado.

Apoyo a jueces, defensores o litigantes.

Análisis comparativo entre sentencias.

🛠 Instalación
bash
Copiar
Editar
# Clona el repositorio
git clone https://github.com/tu-usuario/judicial-sentence-analyzer.git

# Instala dependencias
cd judicial-sentence-analyzer/backend
pip install -r requirements.txt

# Ejecuta análisis local (ejemplo)
python extractor.py docs/ejemplo_sentencia.pdf
🔄 Automatización con n8n
Instala n8n (docker o local): https://docs.n8n.io

Importa el flujo analyze-sentence.n8n.json.

Configura el trigger (Webhook, watch folder, etc.).

Integra con tu script Python o API.

📌 Futuras mejoras
Entrenamiento de modelos propios con sentencias colombianas.

Integración con bases de datos legales.

Sistema de autenticación para usuarios.

Visualización web con filtros por temas o jurisdicción.

🧑‍⚖️ Enfoque jurídico colombiano
El sistema está pensado inicialmente para procesar sentencias judiciales de Colombia, respetando la estructura típica de las decisiones en ese país (hechos, consideraciones, fundamentos jurídicos y decisión).

🧑‍💻 Autor
Desarrollado por Juan Sebastián Fernández Montoya — Abogado y Desarrollador Backend con enfoque en LegalTech, automatización y análisis de datos jurídicos.

