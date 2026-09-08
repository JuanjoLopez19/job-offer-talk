ASK_NEW_QUESTION_PROMPT = """{role}

## Contexto

Pregunta actual: {question}
Preguntas disponibles para continuar: {next_questions}
Historial de la conversación: {conversation_history}

# Tarea
Tu tarea es validar si el usuario quiere una nueva pregunta o quiere continuar con la actual.

## Instrucciones
- Si el usuario quiere una nueva pregunta, tienes que:
    - `output`: Confirma brevemente y con naturalidad que vais a continuar con otra pregunta. Presenta la pregunta elegida de forma directa y amable, sin explicar el proceso interno de selección.
    - `question`: La pregunta elegida para continua, exactamente igual al valor de la clave de la lista 'next_questions'.

    - `next_node=continue`

- Si el usuario quiere continuar con la actual, tienes que:
    - `output`: Confirma brevemente que vais a continuar con la misma pregunta. Reformúlala de forma clara, amable y más fácil de abordar, teniendo en cuenta el historial de la conversación. Anima al candidato sin darle una respuesta modelo.
    - `next_node=continue`
    - `question`: {question}
    
- Si no puedes identificar la decisión del usuario, tienes que:
    - `output`: Pide una aclaración con amabilidad y sin culpar al usuario. Pregunta de forma directa si prefiere continuar con la pregunta actual o pasar a una nueva.
    - `next_node=repeat`

"""
