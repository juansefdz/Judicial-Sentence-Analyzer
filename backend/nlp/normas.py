import re
from typing import List, Dict, Set, Union # Aseguramos Union para tipos complejos si fuera necesario

# --- Funciones de Utilidad (podrían ir en un utils/text_processing.py si son generales) ---
def normalize_string(s: str) -> str:
    """Normaliza una cadena: elimina espacios extra y convierte a minúsculas para comparación."""
    return re.sub(r'\s+', ' ', s).strip().lower()

# --- Función de Extracción de Normas Refactorizada ---
def extract_normas(text: str) -> List[str]:
    """
    Extrae menciones de normas legales (leyes, artículos, códigos, decretos, sentencias, etc.) del texto.
    Mejora los patrones para ser más comprensivos y precisos.

    Args:
        text: El texto de donde se extraerán las normas.

    Returns:
        Una lista de strings, cada uno representando una norma detectada,
        normalizados y sin duplicados.
    """
    patrones = [
        # Leyes: "Ley 1234", "Ley 1234 de 2023", "Ley 906", "Ley 600"
        r"(?:ley|leí)\s+\d+(?:\s+de\s+\d{4})?",
        # Artículos: "Artículo 123", "Art. 123", "artículo 1o", "artículos 23 y 45"
        r"art(?:[íi]culo)?s?\s+(?:\d+(?:[a-z])?(?:\s+y\s+\d+(?:[a-z])?)*)",
        # Decretos: "Decreto 1234", "Decreto 1234 de 2023"
        r"decreto\s+\d+(?:\s+de\s+\d{4})?",
        # Códigos: "Código Penal", "C.P.", "Código Civil", "C.P.C."
        r"c[óo]digo\s+(?:penal|civil|general\s+del\s+proceso|sustantivo\s+del\s+trabajo|disciplinario\s+único)|c\.p\.c\.|c\.p\.|c\.s\.t\.|c\.g\.p\.",
        # Sentencias de la Corte (Ej: "sentencia T-123 de 2020", "sentencia C-456/19")
        r"sentencia\s+[a-z]{1,2}\-?\d{1,4}(?:(?:\s+de|\/)\s*\d{2,4})?",
        # Acuerdos y Resoluciones (Ej: "Acuerdo 001 de 2023", "Resolución 1234")
        r"(?:acuerdo|resoluci[óo]n)\s+\d+(?:\s+de\s+\d{4})?",
    ]

    coincidencias_raw = []
    # Usamos re.IGNORECASE para hacer la búsqueda insensible a mayúsculas/minúsculas
    # y re.DOTALL para que '.' coincida con saltos de línea, útil en patrones complejos.
    for patron in patrones:
        found = re.findall(patron, text, flags=re.IGNORECASE | re.DOTALL)
        coincidencias_raw.extend(found)

    # Normalizar y eliminar duplicados.
    # Convertimos a string en caso de que re.findall devuelva tuplas por grupos.
    coincidencias_limpias = [
        normalize_string(item if isinstance(item, str) else ''.join(item))
        for item in coincidencias_raw if item
    ]

    # Filtrar elementos muy cortos que podrían ser falsos positivos
    coincidencias_filtradas = [
        c for c in coincidencias_limpias if len(c) > 5 or 'código' in c or 'ley' in c
    ]

    return list(dict.fromkeys(coincidencias_filtradas)) # Elimina duplicados manteniendo el orden