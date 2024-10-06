# exemplo de execução
# python analisado.py --gpt35 "sucesso_gpt-3.5-turbo/gpt-3.5-turbo_1727996455.json" --gpt4 "sucesso_gpt-4-turbo/gpt-3.5-turbo_1727996455.json"

import pandas as pd
import argparse
import json
import os
from scipy.stats import ks_2samp
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

# Caminho relativo ao diretório onde o script está localizado
script_dir = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(description='Comparando modelos')
parser.add_argument('--gpt35', type=str, help='Caminho do arquivo gpt-3.5-turbo', required=True)
parser.add_argument('--gpt4', type=str, help='Caminho do arquivo gpt-4-turbo', required=True)

args = parser.parse_args()

arquivo_gpt35 = os.path.join(script_dir, args.gpt35)
arquivo_gpt4 = os.path.join(script_dir, args.gpt35)

# arquivo_gpt35 = os.path.join(script_dir, "sucesso_gpt-3.5-turbo/gpt-3.5-turbo_1727996455.json") 
# arquivo_gpt4 = os.path.join(script_dir, "sucesso_gpt-4-turbo/gpt-3.5-turbo_1727996455.json")

# Carregar os dados em DataFrames
with open(arquivo_gpt35, 'r') as f:
    dados_gpt35 = json.load(f)

with open(arquivo_gpt4, 'r') as f:
    dados_gpt4 = json.load(f)

df_gpt35 = pd.json_normalize(dados_gpt35)
df_gpt4 = pd.json_normalize(dados_gpt4)

estatisticas_gpt35 = df_gpt35.describe(include='all')
estatisticas_gpt4 = df_gpt4.describe(include='all')

print("\nResumo GPT-3.5 Turbo")
print(estatisticas_gpt35)

print("\nResumo GPT-4 Turbo")
print(estatisticas_gpt4)

resultados_teste_ks = {}
colunas_numericas = ['nota_media', 'avaliacoes', 'taxa_1000_metros', 'taxa_2000_metros', 'taxa_3000_metros', 'taxa_4000_metros']

for coluna in colunas_numericas:
    resultados_teste_ks[coluna] = ks_2samp(df_gpt35[coluna], df_gpt4[coluna])

# Similaridade de coseno para colunas de texto (nome e pratos.descricao)
vetorizador = TfidfVectorizer()

# Para a coluna 'nome'
nome_gpt35 = vetorizador.fit_transform(df_gpt35['nome'])
nome_gpt4 = vetorizador.transform(df_gpt4['nome'])
similaridade_coseno_nome = cosine_similarity(nome_gpt35, nome_gpt4).mean()

# Exibir os resultados
print("Resultados do Teste KS para Colunas Numéricas:")
print(resultados_teste_ks)

print("Similaridade de Coseno para a coluna 'nome':")
print(similaridade_coseno_nome)

# Estes custos abaixo eu preenchi manualmente olhando o console da OpenAPI 
#   durante o executar de 400 restaurante com gpt-3.5-turbo e depois 400 restaurantes para gpt-4.turbo
#   - https://platform.openai.com/settings/organization/billing/overview
# Custo (valores fornecidos manualmente)
custo_gpt35 = 0.77
custo_gpt4 = 5.25

# Os valores abaixo são preenchidos com base nos logs executado pelo script gerador.py
# Exemplos de execução
#       python synthetic_data_generator.py --restaurantes 400 --modelo "gpt-3.5-turbo"
#       python synthetic_data_generator.py --restaurantes 400 --modelo "gpt-4-turbo"
estatisticas_gpt35 = {
    "tempo_total": 1014.76,
    "tempo_medio_por_chamada": 23.81,
    "p50": 22.43,
    "p90": 40.36,
    "p95": 43.73,
    "p99": 58.89,
    "erros": 3,
    "chamadas_totais": 40
}

estatisticas_gpt4 = {
    "tempo_total": 7342.06,
    "tempo_medio_por_chamada": 85.33,
    "p50": 79.64,
    "p90": 149.85,
    "p95": 182.57,
    "p99": 214.91,
    "erros": 40,
    "chamadas_totais": 76
}

# Comparação de tempo e custo
print("Comparação de Custo:")
print(f"Custo GPT-3.5-turbo: {custo_gpt35} USD")
print(f"Custo GPT-4-turbo: {custo_gpt4} USD")

print("\nComparação de Execução de Tempo:")
print(f"Tempo total GPT-3.5-turbo: {estatisticas_gpt35['tempo_total']}s, tempo médio por chamada: {estatisticas_gpt35['tempo_medio_por_chamada']}s")
print(f"Tempo total GPT-4-turbo: {estatisticas_gpt4['tempo_total']}s, tempo médio por chamada: {estatisticas_gpt4['tempo_medio_por_chamada']}s")

# Exibir os resultados completos do teste KS e da similaridade de coseno
resultados_teste_ks, similaridade_coseno_nome
