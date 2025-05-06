import argparse
# from dataclasses import dataclass
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import openai
from dotenv import load_dotenv
import os
# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Responde la siguiente pregunta basándote en el contexto proporcionado.
Si no puedes encontrar la respuesta, responde "No sé".
No uses información adicional que no esté en el contexto.

{context}

---

Responde la pregunta utilizando el contexto: {question}
"""


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text

    # Prepare the DB.
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    response_metadata = model.invoke(prompt)
    response = response_metadata.content
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    print(f"Respuesta: {response}")
    print(f"\nFuentes:")
    for s in sources:
        print(f"- {s}")


if __name__ == "__main__":
    main()
