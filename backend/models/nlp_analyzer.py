import spacy
import re
from typing import List, Dict

# --- Cargar el modelo de SpaCy una sola vez y de forma robusta ---
# Este bloque asegura que el modelo se cargue o se descargue si no está presente.
try:
    nlp = spacy.load("es_core_news_md")
except OSError:
    print("Descargando el modelo 'es_core_news_md' de SpaCy. Esto solo sucederá una vez.")
    spacy.cli.download("es_core_news_md")
    nlp = spacy.load("es_core_news_md")

# --- Funciones de Utilidad para normalización y validación (ideales para un módulo 'utils') ---
# Estas funciones son fundamentales para la limpieza de entidades.
def normalize_text(text: str) -> str:
    """Normaliza el texto: elimina espacios extra, puntuación no esencial y convierte a minúsculas para comparación."""
    text = re.sub(r"\s+", " ", text).strip() # Elimina múltiples espacios y espacios al inicio/final
    # Opcional: Podrías querer eliminar más puntuación o caracteres especiales
    # text = re.sub(r"[^\w\sÁÉÍÓÚáéíóúñÑ]", "", text) # Elimina todo lo que no sea alfanumérico o espacio
    return text

# Términos comunes que suelen ser entidades genéricas o ruido y que queremos ignorar.
# Se pueden ampliar según se identifiquen más términos no deseados.
IGNORED_ENTITY_TERMS = {
    "cui", "ley", "sentencia", "norma", "artículo", "folio", "número interno",
    "segunda instancia", "registro", "sala", "instancia", "providencia",
    "documento", "magistrado", "magistrada", "corte", "tribunal", "fiscalía",
    "departamento", "gobernación", "ministro", "ministerio", "proceso",
    "código", "general", "penal", "justicia", "administración", "república",
    "colombia", "judicial", "actuación", "derecho", "principios", "artículos",
    "incisos", "parágrafo", "ley estatutaria", "parte", "sentencias", "casación",
    "penal", "jurisdiccional", "sentencia", "judicial", "recurso", "apelación",
    "expediente", "radicación", "número"
}

def is_valid_entity(ent_text: str) -> bool:
    """
    Valida si una entidad extraída es relevante y no debe ser ignorada.
    Se basa en longitud mínima, si es solo dígitos y una lista de términos a ignorar.
    """
    norm = normalize_text(ent_text).lower()
    
    # Ignorar entidades muy cortas o que son solo números
    if len(norm) < 3 or norm.isdigit(): # Reducido a 3 para capturar nombres cortos si son relevantes
        return False
    
    # Ignorar términos genéricos o de ruido
    if norm in IGNORED_ENTITY_TERMS:
        return False
    
    # Ignorar patrones específicos como códigos o números de radicación (ej. AP4465, CUI: 11001)
    if re.match(r"^(ap\d{4,6}|[a-z]{2,4}\d{5,}|[a-z]{2,4}\-\d{4})$", norm):
        return False
        
    return True

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extrae entidades nombradas (personas, organizaciones, fechas, lugares) de un texto
    utilizando SpaCy, normaliza y filtra las entidades irrelevantes.

    Args:
        text: El texto de donde se extraerán las entidades.

    Returns:
        Un diccionario donde las claves son las categorías de entidades y los valores
        son listas de strings de entidades únicas y válidas.
    """
    doc = nlp(text)

    entidades = {
        "PERSONAS": [],
        "ORGANIZACIONES": [],
        "FECHAS": [],
        "LUGARES": [],
        "LAW": [] 
        # Podrías añadir otras categorías si el modelo de SpaCy las reconoce y son relevantes:
        # "MISC": [], # Varios
        # "NORP": [], # Nacionalidades, Grupos Políticos o Religiosos
        # "EVENT": [], # Eventos
        # Leyes (a veces SpaCy las etiqueta, pero extract_normas es más específico)
    }

    for ent in doc.ents:
        # Aplicar la validación y normalización antes de añadir la entidad
        if is_valid_entity(ent.text):
            normalized_ent_text = normalize_text(ent.text) # Normalizar para consistencia y eliminación de duplicados

            if ent.label_ == "PER":
                entidades["PERSONAS"].append(normalized_ent_text)
            elif ent.label_ == "ORG":
                entidades["ORGANIZACIONES"].append(normalized_ent_text)
            elif ent.label_ == "LOC":
                entidades["LUGARES"].append(normalized_ent_text)
            elif ent.label_ == "DATE":
                entidades["FECHAS"].append(normalized_ent_text)
            # Puedes añadir más condiciones para otros ent.label_ si los necesitas
            # elif ent.label_ == "MISC":
            #    entidades["MISC"].append(normalized_ent_text)

    # Eliminar duplicados después de la normalización
    for key in entidades:
        entidades[key] = list(set(entidades[key]))

    return entidades