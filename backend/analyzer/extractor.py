import pdfplumber
import re # Necesario para normalize_text y otros patrones si se usan internamente
import spacy # Necesario si analyze_text usa spacy y se carga aquí
from typing import List, Dict, Union

# --- Cargar el modelo de SpaCy una sola vez (si analyze_text depende de él y no se carga globalmente) ---
# Si nlp_analyzer.py carga y expone el modelo, esta parte no sería necesaria aquí.
try:
    nlp = spacy.load("es_core_news_md")
except OSError:
    print("Descargando el modelo 'es_core_news_md' de SpaCy. Esto solo sucederá una vez.")
    spacy.cli.download("es_core_news_md")
    nlp = spacy.load("es_core_news_md")

from utils.sentence_parser import segment_sections, SECTION_PATTERNS 
from models.nlp_analyzer import extract_entities as analyze_text
from models.section_analyzer import extract_normas, analyze_hechos, analyze_fallo
from nlp.metadata import extract_metadata


def normalize_text(text: str) -> str:
    """Normaliza el texto: espacios, elimina caracteres no deseados."""
    text = re.sub(r"\s+", " ", text.strip())
    text = re.sub(r"[^\w\sÁÉÍÓÚáéíóúñÑ.,-]", "", text)
    return text

# Necesaria para filtrar entidades en extract_entities/analyze_text
IGNORED_ENTITY_TERMS = {
    "cui", "ley", "sentencia", "norma", "artículo", "folio", "número interno",
    "segunda instancia", "registro", "sala", "instancia", "providencia",
    "documento", "magistrado", "magistrada", "corte", "tribunal", "fiscalía",
    "departamento", "gobernación", "ministro", "ministerio", "proceso",
    "código", "general", "penal", "justicia", "administración", "república",
    "colombia", "judicial", "actuación", "derecho", "principios", "artículos",
    "incisos", "parágrafo", "ley estatutaria", "parte"
}
def is_valid_entity(ent_text: str) -> bool:
    """Valida si una entidad extraída es relevante o debe ser ignorada."""
    norm = normalize_text(ent_text).lower()
    if len(norm) < 4 or norm.isdigit():
        return False
    if norm in IGNORED_ENTITY_TERMS:
        return False
    if re.match(r"^(ap\d{4,6}|[a-z]{2,4}\d{5,})$", norm):
        return False
    return True


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extrae texto de un archivo PDF de manera robusta.
    Maneja excepciones para archivos no encontrados o corruptos.
    """
    full_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
    except FileNotFoundError:
        print(f"Error: El archivo PDF no fue encontrado en la ruta: {file_path}")
        return ""
    except pdfplumber.PDFSyntaxError as e:
        print(f"Error de sintaxis en el PDF: {e}. El archivo podría estar corrupto o no ser un PDF válido.")
        return ""
    except Exception as e:
        print(f"Ocurrió un error inesperado al extraer texto del PDF: {e}")
        return ""
    return full_text.strip()


def build_analysis(text: str) -> dict:
    """
    Construye el análisis completo de la sentencia dividiéndola en secciones
    y aplicando análisis específicos a cada una.
    """
    secciones = segment_sections(text)
    
    for key in SECTION_PATTERNS.keys(): # SECTION_PATTERNS define las secciones esperadas
        if key not in secciones:
            secciones[key] = ""

    resultado = {
        "secciones": secciones,
        "analisis": {},
        "metadatos": extract_metadata(text) # Viene de nlp.metadata
    }

    # Analizar cada sección
    for clave, contenido in secciones.items():
        analisis_seccion = {}
        
        
        analisis_seccion["entidades"] = analyze_text(contenido)

        # Aplicar análisis específicos por sección
        if clave == "hechos" or clave == "actuacion_procesal_relevante":
            analisis_seccion["hechos_relevantes"] = analyze_hechos(contenido) # Viene de models.section_analyzer
        elif clave == "consideraciones":
            analisis_seccion["normas_detectadas"] = extract_normas(contenido) # Viene de models.section_analyzer
        elif clave == "fallo":
            analisis_seccion["resumen_fallo"] = analyze_fallo(contenido) # Viene de models.section_analyzer
        
        resultado["analisis"][clave] = analisis_seccion

    return resultado