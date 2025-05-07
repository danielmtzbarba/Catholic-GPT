import tkinter as tk
from src.ui.gui import ChatBotUI
from src.rag.rag import RAG
from src.rag.prompt import prompt_template

# Run the app
if __name__ == "__main__":
    # Initialize the RAG model
    rag = RAG(prompt_template=prompt_template)
    # Initialize the GUI
    root = tk.Tk()
    app = ChatBotUI(root, rag)
    #
    root.mainloop()