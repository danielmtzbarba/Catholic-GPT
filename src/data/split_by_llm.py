import os
import ast
import json
import json5
import re
from langchain_openai import ChatOpenAI
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(
    model="gpt-4o-mini", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY")
)


def split_text_by_llm(text: str, model, doc_id: str = "doc") -> List[Dict[str, str]]:
    """
    Divide un texto largo en secciones temáticas usando un LLM.
    Devuelve una lista de diccionarios con campos: title, content.
    """
    system_prompt = (
        "Eres un asistente experto en organizar documentos. "
        "Divide el texto en secciones temáticas autocontenidas. "
        "Para cada sección, genera un título breve representativo. "
        "El contenido debe ser tal cual el del documento, no lo sintetices ni modifiques, solo dividelo."
        "Devuelve una lista de diccionarios con objetos de la forma: "
        '{"title": "Título de la sección", "content": "Contenido de la sección", "source": id para citar Referencia}\n\n'
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text[:12000]},  # cortar si es muy largo
    ]

    try:
        response = model.invoke(messages)
        raw = (
            response["messages"][-1]["content"]
            if isinstance(response, dict)
            else response.content
        )

        try:
            sections = extract_llm_sections(raw)

        except json.JSONDecodeError as e:
            print("❌ Error al decodificar el JSON:", e)

        return sections

    except Exception as e:
        print("❌ Error procesando el texto con el modelo:", e)
        return []


raw_text = """json
[
    {
        "title": "Introducción",
        "content": "La preocupación misionera del Papa\n1. El Príncipe de los Pastores (1Pe 5, 4) nos confió los «corderos» y las «ovejas», esto es, toda la grey de Dios (cf. Jn 21, 15-57) doquier que more en el mundo, para apacentarla y regirla, y, por ello, Nos respondimos a su dulce llamamiento de amor, tan conscientes de nuestra humildad como confiados en su potentísimo auxilio; y desde aquel mismo momento siempre tuvimos ante nuestro pensamiento la grandeza, hermosura y gravedad de las Misiones católicas [1]; por lo cual nunca dejamos de consagrarles nuestra máxima preocupación y cuidado. Al cumplirse el primer aniversario de nuestra coronación, en la homilía, señalamos como uno de los más gozosos acontecimientos de nuestro Pontificado el día aquél, cuando, el 11 de octubre, se reunieron en la sacrosanta Basílica Vaticana más de cuatrocientos misioneros, para recibir de nuestras manos el Crucifijo antes de dirigirse a las más lejanas tierras a fin de iluminarlas con la luz de la fe cristiana. Y ciertamente que, en sus arcanos y amables designios, la Providencia divina ya desde los primeros tiempos de nuestro ministerio sacerdotal lo quiso enderezar al campo misional. Porque, apenas terminada la primera guerra mundial, nuestro predecesor, de venerable memoria, Benedicto XV nos llamó desde nuestra nativa diócesis a Roma, para colaborar en la «Obra de la Propagación de la Fe», a la que de buen grado consagramos cuatro muy felices años de nuestra vida sacerdotal. Todavía recordamos gratamente la memorable Pentecostés del año 1922, cuando tuvimos la alegría de participar aquí, en Roma, en la celebración del tercer centenario de la Fundación de la Sagrada Congregación «de Propaganda Fide», que precisamente tiene cual propio cometido el de hacer que la verdad y la gracia del Evangelio brillen hasta los últimos confines de la tierra. Años aquéllos, en los que también nuestro predecesor, de venerable memoria, Pío XI, nos animó con su ejemplo y con su palabra en el apostolado misional. Y, en vísperas del Cónclave, en el que había de resultar elegido Sumo Pontífice, pudimos escuchar de sus propios labios que «nada mayor podría esperarse de un Vicario de Cristo, quienquiera fuese el elegido, que cuanto en este doble ideal se contiene: irradiación extraordinaria de la doctrina evangélica por todo el mundo; procurar y consolidar entre todos los pueblos una paz verdadera [2].",
        "source": "Documento y Subseccion"
    },
    {
        "title": "Cuadragésimo aniversario de «Maximum illud»",
        "content": "2. Llena la mente de estos y otros dulces recuerdos, consciente nuestro ánimo de los grandes deberes que atañen al Supremo Pastor de la grey de Dios, deseamos, venerables hermanos —con ocasión del cuadragésimo aniversario de la memorable carta apostólica Maximum illud (cf. AAS 11 [1919] 440ss.) con la que nuestro predecesor, de piadosa memoria, Benedicto XV, dio nuevo y decisivo impulso a la acción misionera de la Iglesia—, hablaros sobre la necesidad y las esperanzas de la dilatación del Reino de Dios en aquella considerable parte del mundo, donde se desarrolla la preciosa labor de los Misioneros, que trabajan infatigablemente para que surjan nuevas comunidades cristianas exuberantes en saludables frutos. Materia ésta sobre la que nuestros predecesores, Pío XI y Pío XII, de feliz recordación, han dado normas y exhortaciones muy oportunas por medio de encíclicas [3], que Nos mismo hemos querido «confirmar con nuestra autoridad y con igual caridad» en nuestra primera encíclica [4]. Mas nunca se hará bastante para lograr que se realice plenamente el deseo del Divino Redentor, de que todas las ovejas formen parte de una sola grey bajo la guía de un solo Pastor (cf. Jn 10,16).",
        "source": "Documento y Subseccion"
    },
    {
        "title": "Visión misionera de conjunto",
        "content": "3. Cuando convertimos singularmente nuestra atención a los sobrenaturales intereses de la Iglesia en las tierras de Misión, donde todavía no ha llegado la luz del Evangelio, también se nos presentan regiones exuberantes en mieses, y otras en las que el trabajo de la viña del Señor resulta arduo en extremo, mientras no faltan las que conocen la violencia, porque la persecución y regímenes hostiles al nombre de Dios y de Cristo se afanan por ahogar la semilla de la palabra del Señor (cf. Mt 13,19). Doquier nos apremia la urgente necesidad de procurar la salud de las almas en la mejor forma posible; doquier surge la llamada ¡Ayudadnos! (Hch 16,9) que llega a nuestros oídos. Así, pues, a todas estas innumerables regiones, fecundadas por la sangre y el sudor apostólico de los heroicos heraldos del Evangelio procedentes «de todas las naciones que hay bajo el cielo» (Ibíd., 2,5)), y en las que ya germinan ahora como floración y fruto de gracia apóstoles nativos, deseamos que les llegue nuestra afectuosa palabra, tanto de alabanza y de ánimo como de adoctrinamiento, alimentada por una gran esperanza que no teme ser confundida, porque está cimentada en la promesa infalible del Divino Maestro: «Mirad que yo estoy con vosotros todos los días hasta la consumación de los siglos» (Mt 28,20). «Tened confianza; yo he vencido al mundo» (Jn 16,33).",
        "source": "Documento y Subseccion"
    },
    {
        "title": "La jerarquía y el clero local",
        "content": "I. LA JERARQUÍA Y EL CLERO LOCAL\nLlamamiento de Benedicto XV\n4. Luego de terminar la tremenda guerra mundial primera, que a una gran parte de la humanidad causó tantas muertes, destrucciones y tristezas, la carta apostólica, que ya hemos recordado, de nuestro predecesor Benedicto XV, Maximum illud (cf. AAS 11 [1919] 440ss.), resonó cual desgarradora llamada paterna que quería despertar a todos los católicos para lograr doquier las nuevas y pacíficas conquistas del Reino de Dios; del Reino de Dios —decimos—, único que puede dar y asegurar a todos los hombres, hijos del Padre celestial, una paz duradera y una genuina prosperidad. Y desde entonces, durante cuarenta años de actividad misionera, tan intensos como fecundos, un hecho de la máxima importancia ha coronado los ya felices progresos de las Misiones: el desarrollo de la Jerarquía y del clero local. Conforme al «fin último» del trabajo misional que es, según Pío XII, «el de constituir establemente la Iglesia entre otros pueblos y confiarla a una Jerarquía propia, escogida de entre los cristianos de allí nacidos»[5], esta Sede Apostólica siempre oportuna y eficazmente ha provisto, y en estos últimos tiempos con expresiva largueza, el establecer o restablecer la Jerarquía eclesiástica en aquellas regiones donde las circunstancias permitían y aconsejaban la constitución de sedes episcopales, confiándolas siempre que era posible a prelados nativos de cada lugar. Por lo demás, nadie ignora cómo éste ha sido siempre el programa de acción de la S. Congregación «de Propaganda Fide». Mas fue precisamente la epístola Maximum illud la que puso bien de manifiesto, como nunca hasta entonces, toda la importancia y urgencia del problema, recordando una vez más, con tiernos y apremiantes acentos, el urgente deber —por parte de los responsables de las Misiones— de procurar vocaciones y la educación de aquel que entonces se llamaba «clero indígena», sin que este calificativo haya significado jamás discriminación o peyoración, que siempre han de excluirse del lenguaje de los Romanos Pontífices y de los documentos eclesiásticos.",
        "source": "Documento y Subseccion"
    },
    {
        "title": "Nuevo llamamiento del Papa",
        "content": "5. Llamamiento éste de Benedicto XV, renovado por sus sucesores Pío XI y Pío XII, de venerable memoria, que ya ha tenido sus providenciales y visibles frutos, y por ello os invitamos a dar gracias con Nos al Señor, que ha suscitado en las tierras de Misión una numerosa y selecta pléyade de obispos y de sacerdotes, dilectísimos hermanos e hijos nuestros, abriendo así nuestro corazón a las más dulces esperanzas. Pues una rápida ojeada aun tan solo a las estadísticas de los territorios confiados a la Sagrada Congregación de Propaganda Fide, sin contar los actualmente sometidos a la persecución, nos dice que el primer obispo de raza asiática y los primeros vicarios apostólicos de estirpe africana fueron nombrados en el 1939. Y, hasta el 1959, se cuentan ya 68 obispos de estirpe asiática y 25 de estirpe africana. El clero nativo ha pasado de 919 miembros, en el 1918, a 5.553, en 1957, para Asia, y de 90 miembros a 1.811, en el mismo espacio de tiempo, para África. Así es como «el Señor de la mies» (cf. Mt 9,58) ha querido premiar las fatigas y méritos de todos cuantos, con la acción directa y con la múltiple colaboración, se han consagrado al trabajo de las Misiones según las repetidas enseñanzas de la Sede Apostólica. No sin razón, pues, podía afirmar así, con legítima satisfacción, nuestro predecesor Pío XII, de venerable memoria: «Tiempo hubo en que la vida eclesiástica, en cuanto es visible, se desarrollaba preferentemente en los países de la vieja Europa, de donde se difundía, cual río majestuoso, a lo que podría llamarse la periferia del mundo; hoy aparece, por lo contrario, como un intercambio de vida y energía entre todos los miembros del Cuerpo Místico de Cristo en la tierra. No pocas regiones de otros continentes han sobrepasado hace ya mucho tiempo el periodo de la forma misionera de su organización eclesiástica, siendo regidos ya por una propia jerarquía y dando a toda la Iglesia bienes espirituales y materiales, mientras que antes solamente los recibían» [6].",
        "source": "Documento y Subseccion"
    },
    {
        "title": "Colaboración entre nativos y misioneros",
        "content": "6. Las Iglesias locales de los territorios de Misión, aun las fundadas y establecidas con su propia Jerarquía, ya sea por la extensión del territorio, ya por el creciente número de los fieles y la ingente multitud de los que esperan la luz del Evangelio, aún continúan teniendo necesidad de la colaboración de los misioneros venidos de otros países. De ellos, por lo demás, puede muy bien decirse, con las mismas palabras de nuestro predecesor: «En realidad ellos no son extranjeros, puesto que todo sacerdote católico en el cumplimiento de sus propias misiones se encuentra como en su patria, doquier que el reino de Dios florezca o se encuentre en sus principios» [7]. Luego trabajen todos juntos, en la armonía de una fraternal, sincera y delicada caridad, firme reflejo del amor que ellos tienen al Señor y a su Iglesia, en perfecta, gozosa y filial obediencia a los obispos «que el Espíritu Santo ha puesto para regir la Iglesia de Dios» (Hch 20,28), agradeciendo cada uno al otro por la colaboración ofrecida, «cor unum et anima una» (Ibíd., 4,32), para que del modo como ellos se aman brille a los ojos de todos como son verdaderamente discípulos de Aquel que ha dado a los hombres como primero y máximo precepto «nuevo» y suyo, el del mutuo amor (cf. Jn 13,34; 15,12).",
        "source": "Documento y Subseccion"
    },
    {
        "title": "La formación del clero local",
        "content": "II. LA FORMACIÓN DEL CLERO LOCAL\nPrimacía de la formación espiritual\n7. Nuestro recordado predecesor, Benedicto XV, en la Maximum illud insistió en inculcar a los directores de Misión que su más asidua preocupación había de ser dirigida a la «completa y perfecta» (AAS 11 [1919] 445) formación del clero local ya que, «al tener comunes con sus connacionales el origen, la índole, la mentalidad y las aspiraciones, se halla maravillosamente preparado para introducir en sus corazones la Fe, porque conoce mejor que ningún otro las vías de la persuasión» (Ibíd.).",
        "source": "Documento y Subseccion"
        }
]
"""


def extract_llm_sections(text: str):
    """
    Extrae solo el bloque de lista JSON desde un texto LLM que puede tener basura antes o después.
    """
    try:
        # Limpiar comillas especiales (muy común en español)
        text = (
            text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        )

        # Extraer primer bloque que parece una lista JSON de dicts
        start = text.find("[")
        end = text.rfind("]") + 1

        if start == -1 or end == -1:
            raise ValueError(
                "No se encontró un bloque tipo lista JSON en la respuesta."
            )

        json_block = text[start:end]

        # Limpieza de saltos, espacios redundantes, etc.
        json_block = json_block.replace("\n", " ").replace("\r", " ")
        json_block = re.sub(r"\s+", " ", json_block).strip()

        # Reparar comillas curvas
        raw = (
            json_block.replace("“", '"')
            .replace("”", '"')
            .replace("‘", "'")
            .replace("’", "'")
        )

        # Reparar backslashes y espacios
        raw = raw.replace("\\", "\\\\")  # dobles backslash
        raw = re.sub(r"\s+", " ", raw)

        text = raw.replace("'", '"')  # simple a doble
        text = re.sub(r"}\s*{", "}, {", text)  # separa dicts mal pegados

        text = text.replace('"', "'")
        data = parse_dicts_separately(json_block)

        return data

    except Exception as e:
        print("❌ Error al extraer o decodificar JSON5:", e)
        return []


def parse_dicts_separately(text):
    """
    Recibe un string con formato "[{...}, {...}, {...}]" problemático.
    Lo divide en dicts individuales y los parsea uno a uno.
    """
    # Limpiar espacios y saltos
    text = text.strip()

    # Quitar [ ] si existen
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1].strip()
    # Dividir por '},{' pero hay que conservar las llaves en cada dict
    raw_dicts = text.split("}, {")

    dicts = []
    for i, rd in enumerate(raw_dicts):
        # Añadir llaves que quedaron cortadas
        if not rd.startswith("{"):
            rd = "{" + rd
        if not rd.endswith("}"):
            rd = rd + "}"

        # Intentar parsear
        try:
            d = json.loads(rd)
        except json.JSONDecodeError:
            try:
                d = json5.loads(rd)
            except Exception as e:
                print(f"❌ No se pudo parsear dict #{i}: {e}")
                continue
        dicts.append(d)

    return dicts
