import tkinter as tk
from tkinter import font

class ChatBotUI:
    def __init__(self, root, model):
        self.root = root
        self.root.title("ChatBot")
        self.root.geometry("520x500")
        self.root.configure(bg="#ffffff")
        self.model = model

        # Fonts
        self.bold_font = font.Font(family="Helvetica", size=20, weight="bold")
        self.normal_font = font.Font(family="Helvetica", size=16)

        self.create_widgets()
        self.bind_events()

    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="Simple ChatBot", font=("Helvetica", 16, "bold"), bg="#ffffff")
        title_label.pack(pady=10)

        # Chat Frame with Scroll
        self.chat_frame = tk.Frame(self.root, bg="#ffffff")
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        self.chat_canvas = tk.Canvas(self.chat_frame, bg="#ffffff", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.chat_frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_container = tk.Frame(self.chat_canvas, bg="#ffffff")

        self.chat_container.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))

        self.chat_canvas.create_window((0, 0), window=self.chat_container, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.chat_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Input area
        self.input_box = tk.Text(self.root, height=3, font=self.normal_font, bd=1, relief="solid", wrap=tk.WORD)
        self.input_box.pack(fill=tk.X, padx=10, pady=(10, 0))
        self.input_box.focus()

        # Submit Button
        self.submit_button = tk.Button(self.root, text="Send", command=self.on_submit,
                                       font=self.bold_font, bg="#4CAF50", fg="white")
        self.submit_button.pack(pady=10)

    def bind_events(self):
        self.root.bind("<Return>", self.on_enter_key)
        self.chat_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.input_box.bind("<Shift-Return>", lambda e: None)  # allow newline

    def on_enter_key(self, event):
        if event.state & 0x0001:  # Shift is held
            return
        self.on_submit()
        return "break"  # prevent newline in Text

    def on_mouse_wheel(self, event):
        self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_submit(self):
        user_text = self.input_box.get("1.0", tk.END).strip()
        if not user_text:
            return

        self.input_box.config(state='disabled')
        self.submit_button.config(state='disabled')

        # Show user message
        self.add_message("You", user_text, user=True)

        # Simulate bot response
        response = self.chatbot_callback(user_text)
        self.add_message("Bot", response, user=False)

        # Re-enable input
        self.input_box.config(state='normal')
        self.input_box.delete("1.0", tk.END)
        self.submit_button.config(state='normal')
        self.input_box.focus()

    def add_message(self, sender, message, user=True):
        card = tk.Frame(self.chat_container, bg="#f0f0f0", bd=0, highlightbackground="#ccc", highlightthickness=1)
        card.pack(fill=tk.X, padx=10, pady=5, anchor='e' if user else 'w', ipadx=5, ipady=5)

        # Add inner padding to simulate "rounded" look
        card.configure(highlightthickness=1)

        sender_label = tk.Label(card, text=f"{sender}:", font=self.bold_font, bg="#f0f0f0")
        sender_label.pack(anchor='w', padx=10, pady=(5, 0))

        message_label = tk.Label(card, text=message, font=self.normal_font, wraplength=1000,
                                 justify="left", bg="#f0f0f0")
        message_label.pack(anchor='w', padx=10, pady=(0, 5))

        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def chatbot_callback(self, user_input):
        response, sources = self.model(user_input)
        # Replace with your actual model call
        return f"{response}\n\nSources: {', '.join(sources)}"


