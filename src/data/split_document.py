import os
import re
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from split_by_llm import split_text_by_llm

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
dataset_path = os.environ["DATASET_PATH"]

# === CONFIG ===
PDF_FOLDER = os.path.join(dataset_path, "documents/documents-2")
SOURCE_FOLDER = os.path.join(dataset_path, "sources/")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# === 1. Listar PDFs ===
def list_pdfs(folder):
    return [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]


# === 2. Cargar PDF ===
def load_pdf(file_path):
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    return docs


# === 3. Separar por subtítulos o numeración ===
def split_by_llm(text, model, docid):
    sections = split_text_by_llm(text, model, docid)

    print(f"\n📎 Secciones generadas: {len(sections)}\n")
    for sec in sections:
        print(
            f"{sec['source']} | {sec['title']} ({len(sec['content'].split())} palabras)"
        )
        print(f"   {sec['content'][:100]}...\n")
        print(f"\n📎 Texto dividido en {len(sections)} secciones:\n")

    return sections


# === 4. Contar tokens y palabras ===
def count_tokens(text, model="gpt-3.5-turbo"):
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


# === 5. Hacer chunks ===
def chunk_text(text, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)


# === MAIN ===
def main():
    print("📚 Archivos PDF encontrados:")
    pdfs = list_pdfs(PDF_FOLDER)
    for i, name in enumerate(pdfs):
        print(f"[{i}] {name}")

    idx = int(input("\nSelecciona el índice del PDF que quieres procesar: "))
    selected = os.path.join(PDF_FOLDER, pdfs[idx])
    print(f"\n📄 Cargando: {pdfs[idx]}")

    documents = load_pdf(selected)
    full_text = "\n".join([doc.page_content for doc in documents])

    model = ChatOpenAI(
        model="gpt-4o-mini", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    sections = split_text_by_llm(full_text, model, pdfs[idx])

    print(f"\n🔍 Se detectaron {len(sections)} subdivisiones.\n")

    for i, secdict in enumerate(sections):
        title = secdict["source"] = f"{pdfs[idx]}-{secdict["title"]}"
        content = secdict["content"]
        word_count = len(content.split())
        token_count = count_tokens(content)
        save_section(title, content, SOURCE_FOLDER)
        print(f"🔹 {secdict["source"]}: {word_count} palabras, {token_count} tokens")

        # chunks = chunk_text(content)
        # print(f"    ➤ {len(chunks)} chunks generados (∼{CHUNK_SIZE} tokens cada uno)\n")


def save_section(title, content, outdir=""):
    """
    Guarda el campo 'content' de cada sección en un archivo .txt
    con nombre basado en el título.
    """
    # Crear carpeta si no existe
    os.makedirs(outdir, exist_ok=True)

    # Limpiar título para usarlo como nombre de archivo válido
    clean_title = re.sub(r'[\\/*?:"<>|]', "", title)
    clean_title = clean_title.strip().replace(" ", "_")

    # Nombre de archivo
    filename = f"{clean_title}.txt"
    filepath = os.path.join(outdir, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✔️ Guardado: {filename}")
    except Exception as e:
        print(f"❌ Error al guardar {filename}: {e}")


if __name__ == "__main__":
    main()
