import sys
import os
import json
import logging
from typing import Dict, Any

# Configurar el logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Lógica para cargar el archivo de configuración ---
def load_config() -> Dict[str, Any]:
    """
    Carga la configuración desde el archivo 'config.json' en la raíz del proyecto.
    
    Returns:
        Un diccionario con la configuración cargada.
    """
    # Obtener el directorio raíz del proyecto de forma segura.
    # El archivo main.py está en 'backend/', por lo que retrocedemos un nivel.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(project_root, "config.json")
    
    if not os.path.exists(config_path):
        logger.error(f"❌ Archivo de configuración no encontrado en: {config_path}")
        sys.exit(1)
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        logger.info("⚙️ Configuración cargada correctamente.")
        return config
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error al decodificar el archivo JSON de configuración. Asegúrate de que el formato es correcto. Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado al leer la configuración: {e}")
        sys.exit(1)

# Cargar la configuración al inicio del script
CONFIG = load_config()
OUTPUT_DIR = CONFIG.get("output_dir", "outputs") # Usar un valor predeterminado si no se encuentra


# NOTA: Se asume que analyzer.extractor existe y contiene las funciones extract_text_from_pdf
# y build_analysis. 
try:
    from analyzer.extractor import extract_text_from_pdf
    from analyzer.extractor import build_analysis
except ImportError as e:
    logger.error(f"Error al importar módulos de análisis. Asegúrate de que 'analyzer/extractor.py' existe y contiene las funciones 'extract_text_from_pdf' y 'build_analysis'. Error: {e}")
    sys.exit(1)


def save_result(result: Dict[str, Any], filename: str):
    """
    Guarda el diccionario de resultados en un archivo JSON en el directorio de salida.

    Args:
        result: El diccionario que contiene los resultados del análisis.
        filename: El nombre del archivo JSON de salida.
    """
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Resultado guardado en: {output_path}")
    except IOError as e:
        logger.error(f"❌ Error al guardar el resultado en {output_path}: {e}")
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado al guardar el resultado: {e}")


def main():
    """
    Función principal para analizar un archivo PDF desde la línea de comandos.
    Extrae texto, realiza un análisis y guarda el resultado en un archivo JSON.
    """
    if len(sys.argv) < 2:
        logger.info("Uso: python main.py <archivo.pdf>")
        sys.exit(1)

    filepath = sys.argv[1]

    if not os.path.exists(filepath):
        logger.error(f"❌ Archivo no encontrado: {filepath}")
        sys.exit(1)

    if not filepath.lower().endswith(".pdf"):
        logger.error(f"❌ El archivo debe ser un PDF. Extensión proporcionada: {os.path.splitext(filepath)[1]}")
        sys.exit(1)

    logger.info(f"📄 Analizando: {filepath}")

    texto_documento = ""
    try:
        texto_documento = extract_text_from_pdf(filepath)
        if not texto_documento.strip():
            logger.warning("El archivo PDF parece estar vacío o no se pudo extraer texto significativo.")
            # Puedes optar por sys.exit(1) aquí si un PDF vacío es un error crítico
            # O continuar con un resultado de análisis vacío
            resultado_analisis = {} # Resultado vacío si no hay texto
        else:
            resultado_analisis = build_analysis(texto_documento)
    except Exception as e:
        logger.error(f"❌ Error durante la extracción o el análisis del PDF: {e}")
        sys.exit(1)

    # Generar nombre de archivo de salida
    base_filename = os.path.basename(filepath).split(".")[0]
    output_filename = f"{base_filename}_analisis.json"

    # Guardar el resultado del análisis
    save_result(resultado_analisis, output_filename)


if __name__ == "__main__":
    main()