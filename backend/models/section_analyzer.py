from typing import List, Dict, Union
import re
from nlp.hechos import extract_hechos 


def normalize_string(s: str) -> str:
    """Normaliza una cadena: elimina espacios extra y convierte a minúsculas para comparación."""
    return re.sub(r'\s+', ' ', s).strip().lower()



def analyze_hechos(text: str) -> List[str]:
    """
    Delega la extracción de hechos relevantes a la función extract_hechos del módulo nlp.hechos.

    Args:
        text: El texto de la sección de hechos o de la sentencia completa.

    Returns:
        Una lista de strings, cada uno representando un hecho relevante.
    """
    # Esta función actúa como un passthrough. La lógica de extracción detallada
    # debe residir en nlp.hechos.extract_hechos y ser robusta.
    return extract_hechos(text)

def extract_normas(text: str) -> List[str]:
    """
    Extrae menciones de normas legales (leyes, artículos, códigos, decretos, etc.) del texto.
    Mejora los patrones para ser más comprensivos y precisos.
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

def analyze_fallo(text: str) -> Dict[str, Union[List[str], str]]:
    """
    Analiza la sección del fallo para extraer un resumen y clasificar el tipo de decisión.
    """
    resumen_fallo_lista = []

    # 1. Capturar bloques principales de la decisión (RESUELVE, etc.)
    # Buscamos secciones que típicamente contienen la parte resolutiva.
    # Mejorado para capturar desde "RESUELVE:" hasta el final o una nueva sección.
    patrones_bloques = [
        r"RESUELVE:?[\s\S]*?(?=(?:COMUNÍQUESE|CÚMPLASE|NOTIFÍQUESE|FIRMA|ATENTAMENTE|\Z))", # \Z para fin de cadena
        r"(?:LA CORTE|EL JUZGADO|EL TRIBUNAL)\s+RESUELVE:?[\s\S]*?(?=(?:COMUNÍQUESE|CÚMPLASE|NOTIFÍQUESE|FIRMA|ATENTAMENTE|\Z))",
        r"(?:DECLARA|ORDENA|DECIDE):?[\s\S]*?(?=(?:COMUNÍQUESE|CÚMPLASE|NOTIFÍQUESE|FIRMA|ATENTAMENTE|\Z))",
        r"POR TANTO,\s*[\s\S]*?(?=(?:COMUNÍQUESE|CÚMPLASE|NOTIFÍQUESE|FIRMA|ATENTAMENTE|\Z))"
    ]

    for patron in patrones_bloques:
        matches = re.findall(patron, text, flags=re.IGNORECASE | re.DOTALL)
        for match_group in matches:
            # Si findall devuelve tuplas (por grupos de captura), unimos los elementos.
            bloque = match_group if isinstance(match_group, str) else " ".join(match_group)
            bloque_limpio = re.sub(r"\s+", " ", bloque).strip()
            if len(bloque_limpio) > 50: # Filtramos bloques muy cortos
                resumen_fallo_lista.append(bloque_limpio)

    # 2. Identificar el tipo de fallo principal usando verbos clave
    decisiones_keywords = {
        "REVOCA": r"\b(?:revoca|revocar|revocó|deja\s+sin\s+efecto)\b",
        "CONFIRMA": r"\b(?:confirma|confirmar|confirmó|mantiene)\b",
        "NIEGA": r"\b(?:niega|negar|negó|desestima|improcedente)\b",
        "ACOGE": r"\b(?:acoge|acoger|acogió|concede|declara\s+fundado)\b",
        "MODIFICA": r"\b(?:modifica|modificar|modificó)\b",
        "ANULA": r"\b(?:anula|anular|anuló|declara\s+la\s+nulidad)\b",
        "ABSTIENE": r"\b(?:abstiene|abstenerse|abstendrá|se\s+abstiene)\b",
        "CONDENA": r"\b(?:condena|condenar|condenó)\b",
        "ABSUELVE": r"\b(?:absuelve|absolver|absolvió)\b",
        "ORDENA": r"\b(?:ordena|ordenar|ordenó|dispone)\b", # Más general, útil si no hay una más específica
    }

    tipo_fallo_clasificado = "DESCONOCIDO"
    for clave, patron_regex in decisiones_keywords.items():
        if re.search(patron_regex, text, re.IGNORECASE):
            tipo_fallo_clasificado = clave
            break 

    # 3. Extraer oraciones clave que contienen verbos de decisión
    # Esto es para complementar el resumen si los bloques principales no son suficientes.
    # Podríamos usar SpaCy para extraer oraciones completas aquí, pero por simplicidad,
    # continuamos con regex sobre líneas o fragmentos.
    doc_for_sentences = text.split('.') # Dividimos por punto para simular oraciones

    for sentence_part in doc_for_sentences:
        for clave_decision, patron_decision in decisiones_keywords.items():
            if re.search(patron_decision, sentence_part, re.IGNORECASE):
                # Añadir la oración (o parte) si es lo suficientemente significativa
                cleaned_sentence_part = re.sub(r"\s+", " ", sentence_part).strip()
                if len(cleaned_sentence_part) > 30 and cleaned_sentence_part not in resumen_fallo_lista:
                    resumen_fallo_lista.append(cleaned_sentence_part)
                break # Solo añadimos una vez por oración si contiene alguna palabra clave

    # Eliminar duplicados finales y limitar a un número razonable de entradas para el resumen
    resumen_fallo_lista_final = list(dict.fromkeys(resumen_fallo_lista))[:7] # Limitar a 7 elementos para concisión

    return {
        "fallo_resumido": resumen_fallo_lista_final,
        "tipo_fallo": tipo_fallo_clasificado
    }