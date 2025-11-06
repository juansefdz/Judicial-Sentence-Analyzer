import re
from typing import List, Dict, Union
from models.nlp_analyzer import extract_entities # Usamos extract_entities para consistencia
from nlp.normas import extract_normas # Asegúrate de que esta función está actualizada con el refactor

def extract_tema_procesal(text: str) -> List[str]:
    """
    Extrae los posibles motivos principales del recurso o temas procesales del texto.
    Busca patrones más amplios y retorna una lista de todos los temas encontrados.
    """
    patrones = [
        r"recurso de (?:apelación|casación|súplica|revisión)\s*(?:interpuesto|propuesto)?\s*(?:contra|por)?\s*.*?(?:sentencia|decisión|auto|providencia)?",
        r"apelación\s*(?:(?:del)?\s*recurso)?\s*(?:presentado|propuesta|interpuesto)?\s*(?:por|contra)?\s*.*?",
        r"(?:(?:cuestión|problema)\s*jurídic(?:a|o)|tema\s*central)\s*(?:a\s*resolver)?\s*(?:es)?\s*.*?",
        r"(virtualidad|nulidad|práctica probatoria|competencia|prescripción|caducidad|prueba ilícita|debido proceso|derecho de defensa|doble conformidad|sentencia anticipada)\s*(?:de|del|en)?\s*(?:la|el)?\s*(?:decisión|auto|providencia|actuación|proceso)\s*.*?",
        r"(?:incidente de)?\s*(?:nulidad|recusación|desacato)\s*(?:presentado|propuesto)?\s*.*?"
    ]

    temas_encontrados = []
    # Usamos re.DOTALL para que '.' coincida con saltos de línea
    for patron in patrones:
        matches = re.findall(patron, text, flags=re.IGNORECASE | re.DOTALL)
        for m in matches:
            # Limpiar y normalizar el texto encontrado para evitar duplicados por espacios/capitalización
            cleaned_match = re.sub(r"\s+", " ", m).strip()
            # Opcional: Filtrar coincidencias muy cortas o no significativas
            if len(cleaned_match) > 15 and cleaned_match.lower() not in ["motivo no identificado", "apelación"]:
                temas_encontrados.append(cleaned_match)
    
    # Eliminar duplicados y retornar una lista
    if temas_encontrados:
        return list(dict.fromkeys(temas_encontrados)) # Mantiene el orden de aparición
    else:
        return ["Motivo procesal no identificado"] # Retorna una lista incluso si no hay coincidencias

def analyze(text: str) -> Dict[str, Union[str, List[str], Dict[str, List[str]]]]:
    """
    Realiza un análisis específico del texto para extraer el tema procesal,
    normas detectadas y entidades. Esta función está diseñada para ser llamada
    sobre el texto completo o una sección relevante (ej. 'asunto' o 'consideraciones').

    Args:
        text: El texto de la sentencia o una sección relevante a analizar.

    Returns:
        Un diccionario con el tema procesal, las normas detectadas y las entidades.
    """
    return {
        "tema_procesal": extract_tema_procesal(text),
        "normas_detectadas": extract_normas(text),
        "entidades": extract_entities(text)
    }