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
