import re
from typing import Dict, List, Tuple

# Diccionario de patrones para identificar las secciones clave por sus encabezados específicos.
# Se usarán números romanos exactos para asegurar la segmentación correcta de las principales secciones.
SECTION_PATTERNS = {
    # Coincide con "I. ASUNTO"
    "asunto": r"\bI\.\s*asunto\b",
    # Coincide con "II. ACTUACIÓN PROCESAL RELEVANTE" (considerado el antecedente principal)
    "actuacion_procesal_relevante": r"\bII\.\s*actuación\s+procesal\s+relevante\b",
    # Coincide con "III. DECISIÓN IMPUGNADA"
    "decision_impugnada": r"\bIII\.\s*decisión\s+impugnada\b",
    # Coincide con "IV. SUSTENTACIÓN DEL RECURSO"
    "sustentacion_recurso": r"\bIV\.\s*sustentación\s+del\s+recurso\b",
    # Coincide con "V. PRONUNCIAMIENTO DE NO RECURRENTES"
    "pronunciamiento_no_recurrentes": r"\bV\.\s*pronunciamiento\s+de\s+no\s+recurrentes\b",
    # Coincide con "VI. CONSIDERACIONES DE LA CORTE"
    "consideraciones": r"\bVI\.\s*consideraciones\s+de\s+la\s+corte\b",
    # El "fallo" real en este documento es la sección que comienza con "RESUELVE:",
    # la cual aparece al final del documento.
    "fallo": r"\bresuelve:\b"
}

def segment_sections(text: str) -> Dict[str, str]:
    """
    Intenta dividir el texto completo de una sentencia en secciones clave
    basándose en patrones comunes de encabezados, incluyendo numeración romana.

    Si no se encuentran secciones definidas, el texto completo se devuelve
    bajo la clave 'full_text'. Las secciones se extraen incluyendo su encabezado.

    Args:
        text: El texto completo de la sentencia.

    Returns:
        Un diccionario donde las claves son los nombres de las secciones
        (ej., 'asunto', 'hechos', 'fallo') y los valores son el contenido
        de esas secciones como strings.
    """
    # Convertimos todo el texto a minúsculas para realizar la búsqueda de patrones
    # y usamos re.IGNORECASE para que los patrones definidos aquí coincidan
    # sin importar las mayúsculas/minúsculas en el texto original.
    text_lower = text.lower() 

    sections: Dict[str, str] = {}
    
    # Lista para almacenar las secciones encontradas junto con su índice de inicio
    found_sections: List[Tuple[str, int]] = []
    
    # Iterar sobre cada patrón de sección definido
    for section_name, pattern_str in SECTION_PATTERNS.items():
        # Buscar la primera ocurrencia del patrón en el texto en minúsculas
        match = re.search(pattern_str, text_lower, re.IGNORECASE)
        if match:
            # Si se encuentra una coincidencia, añadir el nombre de la sección
            # y su índice de inicio a la lista.
            found_sections.append((section_name, match.start()))

    # Si no se encontró ninguna de las secciones definidas, devolver el texto completo
    if not found_sections:
        return {"full_text": text}

    # Ordenar las secciones encontradas por su índice de aparición en el texto.
    # Esto es crucial para que la segmentación se haga en el orden correcto del documento.
    sorted_sections = sorted(found_sections, key=lambda x: x[1])

    # Extraer el contenido de cada sección
    for i, (section_name, start_idx) in enumerate(sorted_sections):
        # Determinar el índice final de la sección actual.
        # Si es la última sección en la lista ordenada, su contenido va hasta el final del texto.
        # De lo contrario, termina donde comienza la siguiente sección.
        end_idx = sorted_sections[i + 1][1] if i + 1 < len(sorted_sections) else len(text)
        
        # Extraer el segmento de texto correspondiente a la sección.
        # Utilizamos el texto original (no `text_lower`) para mantener la capitalización.
        # `.strip()` elimina cualquier espacio en blanco extra al inicio y al final.
        content = text[start_idx:end_idx].strip()
        sections[section_name] = content

    return sections