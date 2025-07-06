# from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai
from dotenv import load_dotenv
import os
import shutil

import nltk

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]
dataset_path = os.environ["DATASET_PATH"]


def generate_data_store(document_path, chromadir):
    documents = load_documents(document_path)
    chunks = split_text(documents)
    save_to_chroma(chromadir, chunks)


def load_documents(document_path):
    loader = DirectoryLoader(document_path, glob="*.md")
    documents = loader.load()
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks


def save_to_chroma(chroma_path, chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(), persist_directory=chroma_path
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {chroma_path}.")


def main():
    datadir = os.path.join(dataset_path, "documents-1")
    chromadir = os.path.joint(dataset_path, "chroma-1")
    generate_data_store(datadir, chromadir)


if __name__ == "__main__":
    main()
