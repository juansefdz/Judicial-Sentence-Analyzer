
from typing import Dict, Any

from utils.text_cleaning import clean_text
from utils.sentence_parser import segment_sections
from nlp.metadata import extract_metadata

def build_analysis(full_text: str) -> Dict[str, Any]:
    """
    Orquesta el pipeline de análisis de una sentencia, incluyendo:
    1. Limpieza de texto.
    2. Segmentación en secciones.
    3. Extracción de metadatos clave.
    
    Args:
        full_text: El texto completo de la sentencia.
        
    Returns:
        Un diccionario que contiene el análisis estructurado.
    """
    # 1. Limpieza inicial del texto
    cleaned_text = clean_text(full_text)
    
    # 2. Segmentación de secciones del documento
    sections = segment_sections(cleaned_text)
    
    # 3. Extracción de metadatos de las secciones
    # Se extraen los metadatos de la sección de "consideraciones"
    # y de la sección de "actuacion_procesal_relevante" ya que pueden contener información
    # relevante para los metadatos.
    all_metadata = {}
    for section_name, section_text in sections.items():
        extracted_metadata = extract_metadata(section_text)
        all_metadata.update(extracted_metadata)
    
    # 4. Complementar la segmentación con los metadatos
    result = {
        "metadata": all_metadata,
        "secciones": sections
    }
    
    return result