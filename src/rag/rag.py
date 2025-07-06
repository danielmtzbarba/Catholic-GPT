import argparse
from dataclasses import dataclass
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import openai
from dotenv import load_dotenv
import os

from src.rag.prompt import prompt_template

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]
dataset_path = os.environ["DATASET_PATH"]


@dataclass
class Query:
    content: str


class Database(object):
    def __init__(self, db_path):
        self._embedding_function = OpenAIEmbeddings()
        self._db = Chroma(
            persist_directory=db_path, embedding_function=self._embedding_function
        )

    def _search_db(self, query):
        results = self._db.similarity_search_with_relevance_scores(query.content, k=3)
        return results


class RAG(Database):
    """
    Query class to handle the query text and create a prompt.
    """

    def __init__(self, dbdir, prompt_template=None):
        super().__init__(dbdir)
        self._query = Query(content="")
        self._prompt_template = prompt_template
        self._prompt = None

    def _create_prompt(self, results):
        self._prompt = None

        if len(results) == 0 or results[0][1] < 0.7:
            print(f"Unable to find matching results.")
        else:
            context_text = "\n\n---\n\n".join(
                [doc.page_content for doc, _score in results]
            )
            prompt_template = ChatPromptTemplate.from_template(self._prompt_template)
            self._prompt = prompt_template.format(
                context=context_text, question=self._query.content
            )
        return self._prompt

    def _generate_response(self, prompt, results):
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        response_metadata = model.invoke(prompt)
        response = response_metadata.content
        sources = [doc.metadata.get("source", None) for doc, _score in results]
        return response, sources

    def _print_response(self, response, sources):
        print(f"\nPregunta: {self._query.content}")
        print(f"{response}")
        # print(f"\nFuentes:")
        # for s in sources:
        #    print(f"- {s}")
        return

    def __call__(self, query_text):
        self._query.content = query_text
        results = self._search_db(self._query)
        prompt = self._create_prompt(results)
        response, sources = self._generate_response(prompt, results)
        self._print_response(response, sources)
        return response, sources

    @property
    def message(self):
        return self._query.content


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    database_path = os.path.join(dataset_path, "chroma-1")
    rag = RAG(database_path, prompt_template)
    rag(query_text)


def test_rag(query_text):
    database_path = os.path.join(dataset_path, "chroma-1")
    rag = RAG(database_path, prompt_template)
    response = rag(query_text)


query_text = "¿A Dios le gustan las hamburguesas?"

if __name__ == "__main__":
    # main()
    test_rag(query_text)
