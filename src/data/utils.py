import fitz  # PyMuPDF
import os
import re
from langchain_community.document_loaders import PyMuPDFLoader

from langchain.schema import Document
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import TokenTextSplitter


# === 1. Listar PDFs ===
def list_pdfs(folder):
    return [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]


# === 2. Cargar PDF ===
def load_pdf(file_path):
    loader = PyMuPDFLoader(file_path)
    doc = loader.load()
    return doc


def clean_document(document):
    """
    Carga texto desde un PDF con PyMuPDF y limpia saltos de línea innecesarios.
    """

    text = "\n".join([doc.page_content for doc in document])

    # 🔧 Limpieza básica:
    # - Reemplaza saltos de línea intermedios por espacios (preserva párrafos dobles)
    # - Elimina espacios duplicados
    cleaned_text = re.sub(
        r"(?<!\n)\n(?!\n)", " ", text
    )  # solo saltos simples → espacio
    cleaned_text = re.sub(r"\n{2,}", "\n\n", cleaned_text)  # mantén doble salto
    cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)  # espacios múltiples → 1
    cleaned_text = cleaned_text.strip()
    return cleaned_text


def split_text_token(texto, source, chunk_size=800, chunk_overlap=100):
    """
    Divide el texto en chunks usando token splitting con solapamiento.
    """
    splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(texto)

    # Opcional: guardar con IDs o metadata
    chunks = [{"id": f"{source}_{i+1}", "content": c} for i, c in enumerate(chunks)]

    return chunks


def save_chunks(chunks, carpeta_salida):
    """
    Guarda una lista de chunks en archivos .md individuales.
    """
    os.makedirs(carpeta_salida, exist_ok=True)
    c = 0
    for i, chunk in enumerate(chunks, start=1):
        chunk_id = chunk["id"]
        content = chunk["content"]

        # Sanitize filename
        filename = f"{chunk_id}.md"
        filepath = os.path.join(carpeta_salida, filename)

        # Build markdown content
        md_text = f"# {chunk_id}\n\n{content.strip()}"

        # Save to .md file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_text)
            c += 1
        except Exception as e:
            print(f"❌ Error al guardar {filename}: {e}")

    print(f"✅ Guardado {c} chunks")


# === 2. Cargar MD Doc ===
def load_documents(document_path, ext="*.md"):
    loader = DirectoryLoader(document_path, glob=ext)
    documents = loader.load()
    return documents


def split_text_char(documents: list[Document]):
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
