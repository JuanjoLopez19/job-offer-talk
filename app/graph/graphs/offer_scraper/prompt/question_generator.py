QUESTION_GENERATOR_PROMPT = """## Tarea
Tu objetivo principal es generar {question_numbers} preguntas sobre la oferta de trabajo que se te proporciona.
Para que al usuario le sirva como preparación para la entrevista.
Redacta todos los campos narrativos en español de España, independientemente del idioma de la oferta.
Conserva únicamente en su idioma original los nombres propios y los nombres de tecnologías.

### Instrucciones
- Analiza la oferta de trabajo y todos sus detalles antes de generar las preguntas.
- Extrae las keywords más importantes de la oferta de trabajo en `keywords`
- Genera preguntas que sean relevantes y útiles para la entrevista en `questions`
- Genera un resumen de la oferta de trabajo en `summary`

## Oferta de trabajo
{job_offer}
"""
