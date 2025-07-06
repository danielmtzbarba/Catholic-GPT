prompt_template = """
Responde la siguiente pregunta "{question}" utilizando el contexto "{context}". Utiliza las siguientes instrucciones para formular la respuesta:

*Instrucciones:*  
Al responder, analiza la consulta bajo estos *3 criterios* y genera una respuesta estructurada en párrafos numerados. Si algún criterio no aplica, indícalo.  
1. *Confiabilidad Doctrinal*  
   - Responde citando el Catecismo de la Iglesia Católica (CIC) con su número de párrafo (ej. CIC 123).  
   - Si no hay referencia válida, escribe: "No se encontraron fuentes doctrinales en el Catecismo para este tema".  
2. *Fundamentación Bíblica y Magisterial*  
   - Incluye citas bíblicas (libro, capítulo, versículo) y/o documentos magisteriales (ej. encíclicas, concilios).  
   - Si no hay apoyo explícito, escribe: "No se identificaron referencias bíblicas o magisteriales directas".  
3. *Recomendación Pedagógica*  
   - Propone métodos didácticos (ejemplos, analogías, actividades) para enseñar el tema. Sé práctico.  
   - Si no hay sugerencias, escribe: "No se incluyeron recomendaciones pedagógicas para este contenido".  
*Formato de salida:*  
- Párrafos separados, claros y autocontenidos (máx. 150 palabras cada uno).  
- Lenguaje sencillo pero preciso.  
---  
### *Ejemplo de respuesta esperada (para el tema "Bautismo")*:  
1. *Confiabilidad Doctrinal*:  
   El sacramento del Bautismo está definido en el Catecismo de la Iglesia Católica (CIC 1213-1284) como "el fundamento de toda la vida cristiana". Destaca su necesidad para la salvación (CIC 1257) y su carácter de regeneración por el Espíritu Santo.  
2. *Fundamentación Bíblica y Magisterial*:  
   - Biblia: Jesús instituye el Bautismo en Mateo 28:19: "Id y haced discípulos... bautizándolos".  
   - Magisterio: El Concilio de Trento (sesión VII) reafirma su naturaleza sacramental.  
3. *Recomendación Pedagógica*:  
   - Usar analogías como "nacer de nuevo" (Juan 3:5) para explicar su efecto.  
   - Actividad: Simular un bautismo con agua bendita en clase para visualizar el símbolo de purificación. 
"""
