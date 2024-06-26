import sqlite3
import pandas as pd
import os

con = sqlite3.connect('dados_alunos.db')

df = pd.read_sql_query("SELECT * FROM alunos", con)

con.close()

diretorio_saida = 'dados_extraidos'
os.makedirs(diretorio_saida, exist_ok=True)

df.to_json(os.path.join(diretorio_saida, 'dados_alunos.json'), orient='records', force_ascii=False, indent=4)
print("Dados convertidos e salvos em dados_alunos.json")

df.to_csv(os.path.join(diretorio_saida, 'dados_alunos.csv'), index=False, encoding='utf-8')
print("Dados convertidos e salvos em dados_alunos.csv")

df.to_excel(os.path.join(diretorio_saida, 'dados_alunos.xlsx'), index=False, engine='openpyxl')
print("Dados convertidos e salvos em dados_alunos.xlsx")