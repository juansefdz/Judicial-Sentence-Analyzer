import re
from typing import str

def clean_text(text: str) -> str:
    """
    Realiza una serie de operaciones de limpieza en el texto de entrada
    para estandarizar su formato y eliminar ruido común.

    Los pasos de limpieza incluyen:
    1. Unificar múltiples espacios en un solo espacio.
    2. Normalizar múltiples saltos de línea a un solo salto de línea.
    3. Reemplazar espacios no divisibles (non-breaking spaces, \u00a0) por espacios normales.
    4. Normalizar diferentes tipos de guiones (en dash, em dash) a un guion estándar.
    5. Eliminar saltos de página y marcadores comunes de encabezado/pie de página (si persisten).
    6. Eliminar cualquier espacio al inicio y al final del texto.

    Args:
        text: La cadena de texto a limpiar.

    Returns:
        La cadena de texto limpia y normalizada.
    """
    # 1. Unificar múltiples espacios en un solo espacio
    text = re.sub(r'\s+', ' ', text)

    # 2. Normalizar múltiples saltos de línea a un solo salto de línea
    #    Primero, nos aseguramos de que los saltos de línea no estén precedidos/seguidos por espacios extras,
    #    y luego normalizamos a un solo \n.
    text = re.sub(r'\s*\n\s*', '\n', text)

    # 3. Reemplazar espacios no divisibles (non-breaking spaces) por espacios normales
    text = text.replace('\u00a0', ' ')
    text = text.replace('\xa0', ' ') # También es común \xa0

    # 4. Normalizar diferentes tipos de guiones (en dash, em dash) a un guion estándar
    text = re.sub(r'–|—|―', '-', text)

    # 5. Eliminar posibles marcadores de página o líneas de separación de PDF
    #    Esto es más específico de PDFs, puede que no sea necesario si tu extracción ya es limpia.
    #    Ej. "[Image X]", "--- PAGE X ---"
    text = re.sub(r'\[Image\s+\d+\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'---\s*PAGE\s+\d+\s*---', '', text, flags=re.IGNORECASE)
    
    # 6. Eliminar cualquier espacio al inicio y al final del texto.
    text = text.strip()

    return text