import re
from typing import Dict, List, Union

def extract_metadata(text: str) -> Dict[str, Union[str, List[str]]]:
    """
    Extrae metadatos clave de una sentencia, incluyendo CUI, número interno,
    referencias, fecha de la sentencia, magistrado ponente, y corporación/sala.

    Args:
        text: El texto completo de la sentencia.

    Returns:
        Un diccionario con los metadatos extraídos. Los valores pueden ser strings
        o listas de strings (para múltiples referencias, por ejemplo).
    """
    metadata: Dict[str, Union[str, List[str]]] = {}

    # 1. CUI (Código Único de Identificación)
    cui_match = re.search(r"C(?:U\.?|u)\s*I[:\s]*([0-9\s]{10,25})", text, re.IGNORECASE)
    if cui_match:
        cui_normalized = re.sub(r"\s+", "", cui_match.group(1)).strip()
        metadata["cui"] = cui_normalized

    # 2. Número interno del expediente
    interno_match = re.search(r"N[ÚU]MERO\s*INTERNO[:\s]*(\d+)", text, re.IGNORECASE)
    if interno_match:
        metadata["numero_interno"] = interno_match.group(1).strip()
    else:
        radicacion_match = re.search(r"Radicación\s*N°\s*(\d+)", text, re.IGNORECASE)
        if radicacion_match:
            metadata["numero_interno"] = radicacion_match.group(1).strip()

    # 3. Referencias tipo (AP, SP, TP, CP, SL, SC, SU, etc.) con número y posible año
    referencias_match = re.findall(
        r"\b(?:AP|SP|TP|CP|SL|SC|SU|STL|SCC|SCL|SJR|SLR)\d{3,6}(?:[\-\s/]\d{2,4})?\b",
        text, re.IGNORECASE
    )
    if referencias_match:
        metadata["referencias"] = list(dict.fromkeys([r.strip().upper() for r in referencias_match]))

    # 4. Fecha de la sentencia
    fecha_match = re.search(
        r"(?:(?:[A-Z][a-záéíóúñ]+\s+D\.?C\.?|Bogotá\s+D\.?C\.?),\s*)?(?:uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|quince|dieciséis|diecisiete|dieciocho|diecinueve|veinte|veintiuno|veintidós|veintitrés|veinticuatro|veinticinco|veintiséis|veintisiete|veintiocho|veintinueve|treinta|treinta\s+y\s+uno|\d{1,2})\s*(?:\([\d]{1,2}\))?\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+(?:dos\s+mil\s+\d{2}|mil\s+novecient[ao]s\s+\d{2,3}|\d{4})",
        text, re.IGNORECASE | re.DOTALL
    )
    if fecha_match:
        metadata["fecha_sentencia"] = re.sub(r"\s+", " ", fecha_match.group(0).strip())
    else:
        fecha_simple_match = re.search(
            r"\b(\d{1,2}\s+de\s+[a-z]+\s+de\s+\d{4})\b", text, re.IGNORECASE
        )
        if fecha_simple_match:
            metadata["fecha_sentencia"] = fecha_simple_match.group(0).strip()


    # 5. Magistrado Ponente - Lógica de extracción mejorada
    ponente_match = re.search(
        r"(?:Magistrad[ao]\s+Ponente|Ponente)[:\s]*(.*?)(?=\n)",
        text,
        re.IGNORECASE
    )
    if ponente_match:
        ponente_candidato = ponente_match.group(1).strip()
        
        # Validar si el texto extraído es un nombre de persona válido y no un radicado.
        if (
            re.search(r"^[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$", ponente_candidato) and
            not re.search(r'\d', ponente_candidato) and
            not any(term in ponente_candidato.lower() for term in ["honorables", "sala", "corte"])
        ):
            metadata["magistrado_ponente"] = ponente_candidato
        else:
            metadata["magistrado_ponente"] = None
    else:
        metadata["magistrado_ponente"] = None


    # 6. Sala o Corporación (Ej: "Sala de Casación Penal", "Corte Suprema de Justicia")
    sala_match = re.search(r"(?:Sala\s+de\s+Casación\s+(?:Penal|Civil|Laboral|Agraria|Única)|Tribunal\s+Superior\s+de\s+[A-Z][a-záéíóúñ]+\s+de\s+[A-Z][a-záéíóúñ]+|Corte\s+Suprema\s+de\s+Justicia|Consejo\s+de\s+Estado)", text, re.IGNORECASE)
    if sala_match:
        metadata["corporacion_sala"] = sala_match.group(0).strip()
    else:
        sala_generica_match = re.search(r"Sala\s+(?:Especial\s+de\s+Primera\s+Instancia|Penal|Civil|Laboral|de\s+Familia|Única)", text, re.IGNORECASE)
        if sala_generica_match:
            metadata["corporacion_sala"] = sala_generica_match.group(0).strip()

    return metadata