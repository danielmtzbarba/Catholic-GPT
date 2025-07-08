import tkinter as tk
from src.ui.gui import ChatBotUI
from src.rag.rag import RAG

# from src.rag.prompt import prompt_template
from src.rag.prompt_v2 import prompt_template

from dotenv import load_dotenv
import os

load_dotenv()
dataset_path = os.environ["DATASET_PATH"]
database = "chroma/chroma-2"

# Run the app
if __name__ == "__main__":
    datadir = os.path.join(dataset_path, database)  # Initialize the RAG model
    rag = RAG(dbdir=datadir, prompt_template=prompt_template)
    # Initialize the GUI
    root = tk.Tk()
    app = ChatBotUI(root, rag)
    #
    root.mainloop()
