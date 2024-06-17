import json
import tkinter as tk
from PIL import Image, ImageTk
from pynput import keyboard
from threading import Timer
import os

# Carrega os dados dos alunos do arquivo JSON
with open('alunos.json', 'r', encoding='utf-8') as file:
    students_data = json.load(file)['students']

class BarcodeScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.configure(background='white')

        # Cria um frame para as informações
        self.info_frame = tk.Frame(self.root, bg="white")
        self.info_frame.pack(expand=True, fill="both")

        # Configure a grade do info_frame
        self.info_frame.grid_rowconfigure(0, weight=1)
        self.info_frame.grid_rowconfigure(1, weight=1)
        self.info_frame.grid_rowconfigure(2, weight=1)
        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_columnconfigure(1, weight=1)
        self.info_frame.grid_columnconfigure(2, weight=1)

        # Cria labels para exibir a foto do aluno
        self.photo_label = tk.Label(self.info_frame, bg="white")
        self.photo_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="nsew")

        # Cria um frame para centralizar as informações
        self.text_frame = tk.Frame(self.info_frame, bg="white")
        self.text_frame.grid(row=1, column=1, columnspan=2, sticky="nsew")

        self.text_frame.grid_rowconfigure(0, weight=1)
        self.text_frame.grid_rowconfigure(1, weight=1)
        self.text_frame.grid_rowconfigure(2, weight=1)
        self.text_frame.grid_columnconfigure(0, weight=1)
        self.text_frame.grid_columnconfigure(1, weight=1)

        # Cria labels para exibir as informações do aluno
        self.Nome_label = tk.Label(self.text_frame, text="", font=("Arial", 50), bg="green", fg="white")
        self.Nome_label.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=20, pady=5)
        self.Serie_label = tk.Label(self.text_frame, text="", font=("Arial", 40), bg="green", fg="white")
        self.Serie_label.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")
        self.turma_label = tk.Label(self.text_frame, text="", font=("Arial", 40), bg="green", fg="white")
        self.turma_label.grid(row=1, column=1, padx=20, pady=5, sticky="nsew")

        self.barcode_buffer = []
        self.buffer_timer = None

        # Inicia o listener de teclado
        self.listener = keyboard.Listener(on_press=self.on_key_event)
        self.listener.start()


    def exit_program(self, event=None):
        self.listener.stop()
        self.root.quit()

    def reset_buffer(self):
        if self.barcode_buffer:
            barcode = ''.join(self.barcode_buffer)
            self.root.after(0, self.update_labels, barcode)
            self.barcode_buffer = []

    def update_labels(self, barcode):
        student = next((student for student in students_data if student['Matricula'] == barcode), None)
        if student:
            self.Nome_label.config(text=f"{student['Nome']}")
            self.Serie_label.config(text=f"{student['Serie']}")
            self.turma_label.config(text=f"{student['turma']}")
            photo_path = os.path.join('images', f"{barcode}.jpg")
            if os.path.exists(photo_path):
                image = Image.open(photo_path)
                image = image.resize((600, 800), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.photo_label.config(image=photo)
                self.photo_label.image = photo  # Armazena a referência da imagem para evitar garbage collection
            else:
                self.photo_label.config(image='', text="Foto não encontrada")
        else:
            self.Nome_label.config(text="Aluno não encontrado")
            self.Serie_label.config(text="")
            self.turma_label.config(text="")
            self.photo_label.config(image='', text="")

    def on_key_event(self, key):
        try:
            if key.char and key.char.isdigit():
                self.barcode_buffer.append(key.char)
                if self.buffer_timer:
                    self.buffer_timer.cancel()
                self.buffer_timer = Timer(0.1, self.reset_buffer)
                self.buffer_timer.start()
            elif key == keyboard.Key.enter:
                self.reset_buffer()
        except AttributeError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = BarcodeScannerApp(root)
    root.mainloop()