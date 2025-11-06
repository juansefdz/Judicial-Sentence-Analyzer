from analyzer import parser_factual, parser_procesal
from utils.sentence_parser import segment_sections
from nlp.metadata import extract_metadata


import spacy

def detect_sentence_type(text: str) -> str:
    """
    Retorna 'factual' si detecta hechos delictivos o imputaciones penales,
    o 'procesal' si predominan términos de trámite o aspectos formales.
    """
    text_lower = text.lower()

    # Indicadores factuales
    indicadores_factuales = [
        "delito", "delitos", "falsedad", "hurto", "homicidio", "imputación",
        "acusación", "sentencia condenatoria", "pena", "condena", "captura",
        "investigación penal", "punible", "víctimas", "sancionar", "crimen",
        "condenado", "absuelto", "investigación preliminar"
    ]

    # Indicadores procesales
    indicadores_procesales = [
        "nulidad", "recurso", "apelación", "actuación procesal", "auto",
        "providencia", "pruebas", "audiencia preparatoria", "trámite",
        "traslado", "prescripción", "jurisdicción", "procedimiento",
        "modificación", "decisión", "impugnada", "apelante", "resolución",
        "solicitudes", "audiencia", "intervención", "competencia"
    ]

    # Usamos .count() para dar más peso a palabras que aparecen múltiples veces
    puntaje_factual = sum(text_lower.count(palabra) for palabra in indicadores_factuales)
    puntaje_procesal = sum(text_lower.count(palabra) for palabra in indicadores_procesales)
    # Decidimos el tipo de sentencia basado en los puntajes
    if puntaje_factual >= puntaje_procesal:
        return "factual"
    else:
        return "procesal"

def analyze_sentence(text: str) -> dict:
    """
    Función principal que orquesta el análisis de una sentencia.
    Determina el tipo de sentencia y luego realiza un análisis más detallado.

    Nota: En el refactor anterior, sugerí una función 'build_analysis'
    que encapsula la lógica de llamar a 'segment_sections', 'extract_metadata'
    y los análisis específicos por sección (entidades, hechos, normas, fallo).
    Si 'parser_factual' y 'parser_procesal' no son módulos de análisis de secciones
    más complejos, sería más eficiente integrar su lógica en un único flujo de 'build_analysis'.
    Por ahora, mantengo la estructura original pero con la lógica mejorada.
    """
    tipo = detect_sentence_type(text)
    secciones = segment_sections(text) 
    metadatos = extract_metadata(text)

    analisis_detallado = {} # Este diccionario contendrá los resultados de los parsers


    from models.nlp_analyzer import extract_entities # Asumiendo esta ruta
    from models.section_analyzer import extract_normas, analyze_hechos, analyze_fallo # Asumiendo estas rutas

    for clave, contenido in secciones.items():
        analisis_seccion = {
            "entidades": extract_entities(contenido)
        }
        if clave == "hechos":
            analisis_seccion["hechos_relevantes"] = analyze_hechos(contenido)
        elif clave == "consideraciones":
            analisis_seccion["normas_detectadas"] = extract_normas(contenido)
        elif clave == "fallo":
             analisis_seccion["resumen_fallo"] = analyze_fallo(contenido)
             analisis_detallado[clave] = analisis_seccion

    # Si usas parser_factual y parser_procesal tal cual:
    if tipo == "factual":
        analisis_detallado = parser_factual.analyze(secciones)
    else:
        # Asegúrate de que parser_procesal.analyze haga lo mismo
        analisis_detallado = parser_procesal.analyze(secciones)


    return {
        "tipo_sentencia": tipo,
        "resultado": {
            "secciones": secciones,
            "analisis": analisis_detallado, # Aquí se integran los resultados de parser_factual/procesal
            "metadatos": metadatos
        }
    }