import os
import subprocess
import threading
import tkinter as tk
from tkinter import scrolledtext
import openai

# --- CONFIG ---
OPENAI_API_KEY = "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"
MODEL = "gpt-3.5-turbo"

openai.api_key = "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"

def run_background(cmd):
    def target():
        subprocess.run(cmd, shell=True)
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()

def run_foreground(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        return result
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}"

def ask_ai(prompt, history):
    # Build conversation for context
    messages = [{"role": "system", "content": "You are an AI assistant that translates user requests into safe and direct system actions. Output only the shell command or python code to execute, or say 'ASK' if you need clarification. For background tasks, prefix with [BG]: "}]

    for h in history:
        messages.append({"role": "user", "content": h['user']})
        messages.append({"role": "assistant", "content": h['ai']})

    messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        max_tokens=100,
        temperature=0
    )
    return response.choices[0].message.content.strip()

class ChatbotUI:
    def __init__(self, root):
        self.root = root
        root.title("AI Automator Chatbot")

        self.chat_area = scrolledtext.ScrolledText(root, state='disabled', width=70, height=24, wrap='word')
        self.chat_area.pack(padx=10, pady=10)

        self.entry = tk.Entry(root, width=60)
        self.entry.pack(side='left', padx=(10, 0), pady=(0, 10), fill='x', expand=True)
        self.entry.bind('<Return>', self.send_message)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(side='left', padx=(5, 10), pady=(0, 10))

        self.history = []

    def send_message(self, event=None):
        user_input = self.entry.get()
        if not user_input.strip():
            return

        self.append_message("You", user_input)
        self.entry.delete(0, tk.END)
        threading.Thread(target=self.handle_ai, args=(user_input,), daemon=True).start()

    def append_message(self, sender, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{sender}: {message}\n")
        self.chat_area.yview(tk.END)
        self.chat_area.config(state='disabled')

    def handle_ai(self, user_input):
        ai_reply = ask_ai(user_input, self.history)
        self.append_message("AI", ai_reply)
        self.history.append({'user': user_input, 'ai': ai_reply})

        # Command executor
        if ai_reply.startswith("[BG]:"):
            cmd = ai_reply.replace("[BG]:", "").strip()
            run_background(cmd)
            self.append_message("System", f"Started in background: {cmd}")
        elif ai_reply.startswith("ASK"):
            self.append_message("System", "AI needs clarification.")
        elif ai_reply.startswith("python "):
            try:
                exec(ai_reply[len("python "):])
                self.append_message("System", "Python code executed.")
            except Exception as e:
                self.append_message("System", f"Python error: {e}")
        else:
            result = run_foreground(ai_reply)
            self.append_message("System", result)

if __name__ == '__main__':
    root = tk.Tk()
    app = ChatbotUI(root)
    root.mainloop()
