from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

import openai
import os
import nltk
import shutil

from utils import list_pdfs, load_pdf, clean_document, split_text_token, save_chunks

from dotenv import load_dotenv


# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]
dataset_path = os.environ["DATASET_PATH"]


def generate_data_store(docdir, sourcedir, chromadir):
    print("📚 Archivos PDF encontrados:")
    pdfs = list_pdfs(docdir)
    for i, name in enumerate(pdfs):
        print(f"[{i}] {name}")

    all_chunks = []

    for idx, docname in enumerate(pdfs):
        print(f"\n📄 Cargando: {pdfs[idx]}")
        selected = os.path.join(docdir, pdfs[idx])
        document = load_pdf(selected)
        text = clean_document(document)
        chunks = split_text_token(text, pdfs[idx][:-4])
        all_chunks.extend(chunks)

    save_chunks(all_chunks, sourcedir)
    save_to_chroma(chromadir, all_chunks)


def save_to_chroma(chroma_path, chunks):
    # Clear out the database first.
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)

    #
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(persist_directory=chroma_path, embedding_function=embeddings)

    documents = [
        Document(page_content=chunk["content"], metadata={"chunk_id": chunk["id"]})
        for chunk in chunks
    ]

    # Split in safe batches
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch = documents[i : i + batch_size]
        vectorstore.add_documents(batch)


datadir_id = 2

document_path = os.path.join(dataset_path, f"documents/documents-{datadir_id}")
source_path = os.path.join(dataset_path, f"sources/sources-{datadir_id}")
chroma_path = os.path.join(dataset_path, f"chroma/chroma-{datadir_id}")


def main():
    generate_data_store(document_path, source_path, chroma_path)


if __name__ == "__main__":
    main()
