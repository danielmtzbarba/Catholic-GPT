prompt_template = """
Responde la siguiente pregunta basándote en el Catecismo de la Iglesia.
Realiza un comentario general sobre la pregunta y luego responde a la pregunta.
Para responder remitete a citar la biblia o el catecismo.
Recomienda como enseñar a los niños la respuesta según los documentos educativos proporcionados.

Si no puedes encontrar la respuesta, responde amable y brevemente que no conoces la respuesta.
No uses información adicional que no esté en el contexto.

{context}

---

Responde la pregunta utilizando el contexto: {question}
"""