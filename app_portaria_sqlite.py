import sqlite3
import tkinter as tk
from PIL import Image, ImageTk
from pynput import keyboard
from threading import Timer
import os
from datetime import datetime

# Função para carregar dados dos alunos do banco de dados SQLite
def load_students_data():
    conn = sqlite3.connect('dados_alunos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Matricula, Nome, Serie, turma FROM alunos")
    rows = cursor.fetchall()
    conn.close()
    
    students = []
    for row in rows:
        students.append({
            'Matricula': str(row[0]),
            'Nome': row[1],
            'Serie': row[2],
            'turma': row[3]
        })
    
    return students

students_data = load_students_data()

class BarcodeScannerApp:

    def registrar_presenca(matricula):
        # Conexão com o banco de dados SQLite
        conn = sqlite3.connect('dados_alunos.db')
        cursor = conn.cursor()
            
        # Obter a data atual no formato 'YYYY-MM-DD'
        data_atual = datetime.now().strftime('%d-%m-%y')
        coluna_entrada = f'{data_atual}-entrada'
        coluna_saida = f'{data_atual}-saida'
        horario_atual = datetime.now().strftime('%H:%M:%S')
            
        # Verificar se as colunas de entrada e saída existem, caso contrário, criar
        cursor.execute(f"PRAGMA table_info(alunos)")
        colunas = [info[1] for info in cursor.fetchall()]
            
        if coluna_entrada not in colunas:
            cursor.execute(f"ALTER TABLE alunos ADD COLUMN '{coluna_entrada}' TEXT")
            cursor.execute(f"UPDATE alunos SET '{coluna_entrada}' = 'F'")
            conn.commit()
            
        if coluna_saida not in colunas:
            cursor.execute(f"ALTER TABLE alunos ADD COLUMN '{coluna_saida}' TEXT")
            cursor.execute(f"UPDATE alunos SET '{coluna_saida}' = 'F'")
            conn.commit()
            
        # Registrar o horário de entrada ou saída
        query = f"""SELECT "{coluna_entrada}" FROM alunos WHERE Matricula = '{matricula}'"""
        cursor.execute(query)
        entrada = cursor.fetchone()
            
        if entrada[0] == 'F':
            cursor.execute(f"UPDATE alunos SET '{coluna_entrada}' = ? WHERE Matricula = ?", (horario_atual, matricula))
        else:
            cursor.execute(f"""SELECT "{coluna_saida}" FROM alunos WHERE Matricula = ?""", (matricula,))
            saida = cursor.fetchone()
                
            if saida[0] == 'F':
                cursor.execute(f"UPDATE alunos SET '{coluna_saida}' = ? WHERE Matricula = ?", (horario_atual, matricula))
            
        # Confirmar as mudanças e fechar a conexão
        conn.commit()
        conn.close()
    
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
            numero_matricula = student['Matricula']
            BarcodeScannerApp.registrar_presenca(numero_matricula)
            self.Nome_label.config(text=f"{student['Nome']}")
            self.Serie_label.config(text=f"{student['Serie']}")
            self.turma_label.config(text=f"{student['turma']}")
            photo_path = os.path.join('images', f"{barcode}.jpg")
            if os.path.exists(photo_path):
                image = Image.open(photo_path)
                image = image.resize((600, 800), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.photo_label.config(image=photo)
                self.photo_label.image = photo
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



