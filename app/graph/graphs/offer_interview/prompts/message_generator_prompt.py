MESSAGE_GENERATOR_PROMPT = """{role}

## Contexto

Pregunta actual: {question}
Preguntas disponibles para continuar: {next_questions}
Flujo siguiente: {next_node}
---

## Instrucciones
Tienes que generar un mensaje para el usuario dependiendo del flujo que toque seguir:
- Si el flujo es `not_in_context_edge`:
    - `output`: El mensaje tiene que indicar que la respuesta no esta en el contexto de la oferta y se ha alcanzado el máximo de intentos para esta pregunta y procedes a elegir una nueva pregunta.
    
- Si el flujo es `not_complete_and_coherent_edge`:
    - `output`: El mensaje tiene que indicar que la respuesta no esta completa respecto al criterio de evaluación y se ha alcanzado el máximo de intentos para esta pregunta y procedes a elegir una nueva pregunta.

- `question`: La pregunta elegida para continua, exactamente igual al valor de la clave de la lista 'next_questions'.
"""
