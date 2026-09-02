MESSAGE_GENERATOR_PROMPT = """{role}

## Contexto

Pregunta actual: {question}
Preguntas disponibles para continuar: {next_questions}
Flujo siguiente: {next_node}
---

## Instrucciones
Tienes que generar un mensaje para el usuario dependiendo del flujo que toque seguir:
- Si el flujo es `not_in_context_edge`:
    - `output`: Agradece brevemente la respuesta. Explica con tacto que no has podido relacionarla suficientemente con la pregunta o la oferta. Indica que, para mantener el ritmo de la entrevista, vais a continuar con otra pregunta. No culpes ni reprendas al candidato.
    
- Si el flujo es `not_complete_and_coherent_edge`:
    - `output`: Agradece brevemente la respuesta. Explica de forma amable que faltan detalles concretos para poder valorarla por completo. Indica que, para mantener el ritmo de la entrevista, vais a continuar con otra pregunta. No menciones criterios internos de evaluación ni el máximo de intentos.

- `question`: La pregunta elegida para continua, exactamente igual al valor de la clave de la lista 'next_questions'.
"""
