import spacy
import re
from typing import List, Dict, Set

# Cargar el modelo en español una sola vez
try:
    nlp = spacy.load("es_core_news_md")
except OSError:
    print("Descargando el modelo 'es_core_news_md' de SpaCy. Esto solo sucederá una vez.")
    spacy.cli.download("es_core_news_md")
    nlp = spacy.load("es_core_news_md")

def extract_hechos(text: str) -> List[str]:
    """
    Extrae los hechos relevantes de un texto, priorizando oraciones que describen
    acciones, eventos, imputaciones o situaciones fácticas clave.

    Args:
        text: El texto de la sección de hechos o de la sentencia completa.

    Returns:
        Una lista de strings, cada uno representando un hecho relevante,
        ordenados por relevancia (hasta un máximo de 10).
    """
    doc = nlp(text)
    candidatos_hechos: Dict[str, int] = {} # Usaremos un diccionario para almacenar la oración y su puntaje

    # Palabras clave mejoradas y más específicas para identificar hechos.
    # Incluyen verbos de acción y términos relacionados con eventos o situaciones.
    palabras_clave_fuertes = {
        "imputación", "acusación", "procesado", "formuló", "sucedió", "ocurrió",
        "delito", "falsedad", "hurto", "homicidio", "captura", "investigación",
        "interpuso", "presentó", "declaró", "testificó", "evidenció", "demostró",
        "condenó", "absolvió", "hallazgo", "se constató", "se comprobó", "se determinó"
    }

    palabras_clave_medias = {
        "hecho", "evento", "incidente", "actuación", "trámite", "judicial",
        "denuncia", "victima", "agresor", "sentencia", "decisión", "providencia"
    }

    # Términos que, si están presentes, reducen la relevancia factual (suelen ser procesales o genéricos)
    palabras_clave_ruido = {
        "resolución", "consideración", "jurisdiccional", "recurso", "apelación",
        "criterio", "fundamento", "conclusiones", "resuelve", "declara", "firma"
    }

    for sent in doc.sents:
        sent_text_original = sent.text.strip()
        sent_text_lower = sent_text_original.lower()
        score = 0

        # Reglas de puntuación para identificar la relevancia de un hecho:
        # 1. Puntuar por palabras clave fuertes
        for palabra in palabras_clave_fuertes:
            if palabra in sent_text_lower:
                score += 3 # Mayor peso para palabras clave muy indicativas

        # 2. Puntuar por palabras clave medias
        for palabra in palabras_clave_medias:
            if palabra in sent_text_lower:
                score += 1

        # 3. Restar puntos por palabras clave de ruido
        for palabra in palabras_clave_ruido:
            if palabra in sent_text_lower:
                score -= 2 # Reducir peso si aparecen términos no factuales

        # 4. Puntuar por presencia de entidades nombradas (personas, organizaciones, lugares, fechas)
        # Los hechos suelen involucrar actores, lugares y tiempos.
        entidades_en_sent = [ent.label_ for ent in sent.ents]
        if "PER" in entidades_en_sent:
            score += 2
        if "ORG" in entidades_en_sent:
            score += 1
        if "LOC" in entidades_en_sent:
            score += 1
        if "DATE" in entidades_en_sent: # Fechas son muy importantes para hechos
            score += 3

        # 5. Filtrar oraciones que son puramente procesales o introductorias/conclusivas
        if "se pronuncia la sala respecto" in sent_text_lower:
            score = 0 # Ignorar completamente estas oraciones introductorias
        if sent_text_lower.startswith(("en mérito de lo expuesto", "comuníquese y cúmplase")):
            score = 0

        # Solo añadir oraciones con un puntaje positivo y que no sean demasiado cortas
        if score > 0 and len(sent_text_original) > 20: # Un umbral mínimo para evitar frases triviales
            # Usamos el texto original para evitar la pérdida de mayúsculas/minúsculas o formato
            candidatos_hechos[sent_text_original] = score

    # Ordenar los hechos por puntaje de mayor a menor
    # Usamos dict.items() para obtener pares (oración, puntaje)
    hechos_ordenados = sorted(candidatos_hechos.items(), key=lambda item: item[1], reverse=True)

    # Extraer solo las oraciones, asegurando que no haya duplicados si el mismo hecho
    # fue capturado con diferentes puntuaciones o por otros motivos.
    # Usamos un set para el resultado final para garantizar la unicidad
    hechos_finales_unicos: List[str] = []
    seen_hechos: Set[str] = set()

    for hecho_text, _ in hechos_ordenados:
        normalized_hecho = normalize_string_for_comparison(hecho_text)
        if normalized_hecho not in seen_hechos:
            hechos_finales_unicos.append(hecho_text)
            seen_hechos.add(normalized_hecho)
            if len(hechos_finales_unicos) >= 10: # Limitar a un máximo de 10 hechos
                break

    return hechos_finales_unicos

# --- Función auxiliar para normalizar hechos para comparación/deduplicación ---
def normalize_string_for_comparison(text: str) -> str:
    """Normaliza un string para propósitos de comparación y deduplicación (lower case, espacios)."""
    text = re.sub(r"\s+", " ", text).strip().lower()
    # Podrías ser más agresivo en la limpieza de puntuación si los duplicados
    # son un problema por diferencias de comas/puntos.
    # text = re.sub(r"[^\w\sÁÉÍÓÚáéíóúñÑ]", "", text)
    return text