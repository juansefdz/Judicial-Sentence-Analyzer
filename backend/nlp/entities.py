import spacy
import re
from typing import Dict, List, Union

# --- Cargar el modelo de SpaCy una sola vez y de forma robusta ---
try:
    nlp = spacy.load("es_core_news_md")
except OSError:
    print("Descargando el modelo 'es_core_news_md' de SpaCy. Esto solo sucederá una vez.")
    spacy.cli.download("es_core_news_md")
    nlp = spacy.load("es_core_news_md")

# --- Términos a Ignorar (Lista Consolidada y Ampliada) ---
IGNORED_ENTITY_TERMS = {
    "cui", "ley", "sentencia", "norma", "artículo", "folio", "número interno",
    "segunda instancia", "registro", "sala", "instancia", "providencia",
    "documento", "magistrado", "magistrada", "corte", "tribunal", "fiscalía",
    "departamento", "gobernación", "ministro", "ministerio", "proceso",
    "código", "general", "penal", "justicia", "administración", "república",
    "colombia", "judicial", "actuación", "derecho", "principios", "artículos",
    "incisos", "parágrafo", "ley estatutaria", "parte", "sentencias", "casación",
    "jurisdiccional", "recurso", "apelación", "expediente", "radicación", "número",
    "presidente", "doctor", "doctora", "señor", "señora", "hijo", "hija", "parte procesal"
}

# --- Funciones de Utilidad ---
def normalize_entity_text(text: str) -> str:
    """
    Normaliza el texto de una entidad:
    1. Elimina múltiples espacios y espacios al inicio/final.
    2. Convierte a minúsculas para comparaciones consistentes.
    3. Elimina caracteres especiales que no sean alfanuméricos, espacios, o signos de puntuación clave.
    """
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"[^\w\sÁÉÍÓÚáéíóúñÑ.,-]", "", text)
    return text

def is_valid_entity(ent_text: str) -> bool:
    """
    Valida si una entidad extraída es relevante y no debe ser ignorada.
    Se basa en longitud mínima, si es solo dígitos, una lista de términos a ignorar
    y patrones de códigos/IDs.
    """
    norm = normalize_entity_text(ent_text).lower()

    if len(norm) < 3 or norm.isdigit():
        return False

    if norm in IGNORED_ENTITY_TERMS:
        return False

    if any(norm.startswith(term) for term in IGNORED_ENTITY_TERMS):
        return False

    if re.match(r"^(ap\d{4,6}|[a-z]{2,4}\d{5,}|[a-z]{2,4}\-\d{4,8}|cui:\s*\d+)$", norm):
        return False

    return True

# --- Función Principal de Extracción de Entidades ---

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extrae entidades nombradas de un texto utilizando SpaCy,
    aplicando normalización y filtrado para mejorar la calidad.

    Args:
        text: El texto de donde se extraerán las entidades.

    Returns:
        Un diccionario donde las claves son las categorías de entidades
        (PERSONAS, ORGANIZACIONES, LUGARES, FECHAS) y los valores son
        listas de strings de entidades únicas, válidas y ordenadas alfabéticamente.
    """
    doc = nlp(text)

    entidades = {
        "PERSONAS": [],
        "ORGANIZACIONES": [],
        "LUGARES": [],
        "FECHAS": [],
    }

    for ent in doc.ents:
        normalized_text = normalize_entity_text(ent.text)

        if not is_valid_entity(normalized_text):
            continue

        if ent.label_ == "PER":
            entidades["PERSONAS"].append(normalized_text)
        elif ent.label_ in {"ORG", "NORP"}:
            entidades["ORGANIZACIONES"].append(normalized_text)
        elif ent.label_ in {"LOC", "GPE"}:
            entidades["LUGARES"].append(normalized_text)
        elif ent.label_ == "DATE":
            entidades["FECHAS"].append(normalized_text)

    for tipo in entidades:
        entidades[tipo] = sorted(list(set(entidades[tipo])))

    return entidades