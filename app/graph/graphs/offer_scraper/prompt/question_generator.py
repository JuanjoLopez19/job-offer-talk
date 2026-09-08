QUESTION_GENERATOR_PROMPT = """{role}

## Tarea
Tu objetivo principal es generar {question_numbers} preguntas sobre la oferta de trabajo que se te proporciona.
Para que al usuario le sirva como preparación para la entrevista.
Siempre en español y en texto plano, independientemente del idioma en que este la oferta de trabajo.

### Instrucciones
- Analiza la oferta de trabajo y todos sus detalles antes de generar las preguntas.
- Extrae las keywords más importantes de la oferta de trabajo en `keywords`
- Genera preguntas que sean relevantes y útiles para la entrevista en `questions`
- Genera un resumen de la oferta de trabajo en `summary`

## Oferta de trabajo
{job_offer}

"""
