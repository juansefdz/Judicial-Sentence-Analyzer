import os

# === Rutas base ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "..", "docs")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "outputs")

# === Modelo de spaCy ===
SPACY_MODEL = "es_core_news_md"

# === Configuraciones NLP ===
MIN_ENT_LEN = 4  # Longitud mínima para entidades válidas
BLACKLIST_ENTITIES = ["ley", "artículo", "norma", "sentencia"]

# === Parámetros de análisis ===
MAX_RESUMEN_FALLO = 5

# === Otras opciones globales ===
DEBUG = True
