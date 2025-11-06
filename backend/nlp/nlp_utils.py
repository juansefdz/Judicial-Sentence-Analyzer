import spacy
from typing import Optional

# Usamos una variable global privada para almacenar la instancia del modelo NLP.
# Optional[spacy.Language] indica que puede ser un objeto SpaCy.Language o None.
_nlp_model: Optional[spacy.Language] = None

def get_nlp_model() -> spacy.Language:
    """
    Retorna una única instancia del modelo de SpaCy 'es_core_news_md'.
    Si el modelo no ha sido cargado previamente, lo carga.
    Si el modelo no está instalado, intenta descargarlo automáticamente.

    Returns:
        Una instancia del objeto spacy.Language (el modelo NLP cargado).
    """
    global _nlp_model

    if _nlp_model is None:
        try:
            # Intenta cargar el modelo
            _nlp_model = spacy.load("es_core_news_md")
        except OSError:
            # Si el modelo no se encuentra, intenta descargarlo.
            print("El modelo 'es_core_news_md' de SpaCy no está instalado.")
            print("Intentando descargar el modelo. Esto solo sucederá una vez.")
            try:
                spacy.cli.download("es_core_news_md")
                _nlp_model = spacy.load("es_core_news_md")
                print("Modelo 'es_core_news_md' descargado y cargado exitosamente.")
            except Exception as e:
                print(f"Error al descargar o cargar el modelo de SpaCy: {e}")
                # Podrías querer levantar una excepción o manejar este error de forma más robusta
                raise RuntimeError(f"No se pudo cargar el modelo de SpaCy: {e}")
        except Exception as e:
            # Captura cualquier otra excepción durante la carga
            print(f"Ocurrió un error inesperado al cargar el modelo de SpaCy: {e}")
            raise RuntimeError(f"Error al inicializar el modelo de SpaCy: {e}")

    return _nlp_model