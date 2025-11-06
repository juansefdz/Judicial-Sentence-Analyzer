from typing import Dict, List, Union
from models.section_analyzer import extract_normas, analyze_hechos, analyze_fallo
from models.nlp_analyzer import extract_entities # Usamos extract_entities para ser consistentes
from utils.sentence_parser import segment_sections, SECTION_PATTERNS # Importamos SECTION_PATTERNS

def analyze(text: str) -> Dict[str, Union[Dict, List, str]]:
    """
    Realiza un análisis detallado de un texto de sentencia, dividiéndolo en secciones
    y aplicando análisis específicos (entidades, hechos, normas, fallo) a cada una.

    Args:
        text: El texto completo de la sentencia a analizar.

    Returns:
        Un diccionario con las secciones segmentadas y su análisis correspondiente.
    """
    secciones = segment_sections(text)

    for key in SECTION_PATTERNS.keys():
        if key not in secciones:
            secciones[key] = ""

    resultado = {
        "secciones": secciones,
        "analisis": {}
    }

    # Iterar sobre las secciones y aplicar el análisis correspondiente
    for clave, contenido in secciones.items():
        analisis_seccion = {} # Diccionario para almacenar el análisis de la sección actual

        # Todas las secciones tendrán extracción de entidades
        # Usamos 'extract_entities' para ser consistentes con la función de entidades refactorizada.
        analisis_seccion["entidades"] = extract_entities(contenido)

        # Análisis específicos para ciertas secciones
        if clave == "hechos" or clave == "actuacion_procesal_relevante":
            # Si 'actuacion_procesal_relevante' también puede contener hechos.
            analisis_seccion["hechos_relevantes"] = analyze_hechos(contenido)
        elif clave == "consideraciones":
            analisis_seccion["normas_detectadas"] = extract_normas(contenido)
        elif clave == "fallo":
            analisis_seccion["resumen_fallo"] = analyze_fallo(contenido)

        # Asignar el análisis de la sección al resultado final
        resultado["analisis"][clave] = analisis_seccion

    return resultado