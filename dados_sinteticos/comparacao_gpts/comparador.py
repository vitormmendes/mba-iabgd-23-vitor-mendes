import pandas as pd
import json

# Carregar os dois arquivos JSON
file_gpt_35 = 'dados_sinteticos/comparacao_gpts/gpt-3.5-turbo_1727623088.json'
file_gpt_4 = 'dados_sinteticos/comparacao_gpts/gpt-4-turbo_1727752792.json'

# Abrir e ler os arquivos JSON
with open(file_gpt_35, 'r') as f:
    data_gpt_35 = json.load(f)

with open(file_gpt_4, 'r') as f:
    data_gpt_4 = json.load(f)

# Converter os dados JSON em DataFrames
df_gpt_35 = pd.json_normalize(data_gpt_35)
df_gpt_4 = pd.json_normalize(data_gpt_4)

# Função para contar pratos (ajuste prévio)
def contar_pratos(pratos):
    try:
        return len(pratos)
    except Exception:
        print(pratos)
        return 0

# Função para calcular a média dos preços dos pratos
def calcular_media_preco(pratos):
    try:
        precos = [prato['preco'] for prato in pratos]
        if precos:
            return sum(precos) / len(precos)
        return 0
    except Exception:
        return 0

# Calcular a média correta da quantidade de pratos por restaurante (usando o comprimento da lista de pratos)
media_pratos_gpt_35 = df_gpt_35['pratos'].apply(contar_pratos).mean()
media_pratos_gpt_4 = df_gpt_4['pratos'].apply(contar_pratos).mean()

# Calcular a média do preço dos pratos por restaurante
media_preco_gpt_35 = df_gpt_35['pratos'].apply(calcular_media_preco).mean()
media_preco_gpt_4 = df_gpt_4['pratos'].apply(calcular_media_preco).mean()

# Distribuição das categorias de restaurantes
distribuicao_categorias_gpt_35 = df_gpt_35['categoria'].value_counts(normalize=True).to_dict()
distribuicao_categorias_gpt_4 = df_gpt_4['categoria'].value_counts(normalize=True).to_dict()

# Nota média dos restaurantes
media_notas_gpt_35 = df_gpt_35['nota_media'].mean()
media_notas_gpt_4 = df_gpt_4['nota_media'].mean()

# Média de avaliações por restaurante
media_avaliacoes_gpt_35 = df_gpt_35['avaliacoes'].mean()
media_avaliacoes_gpt_4 = df_gpt_4['avaliacoes'].mean()

# Calcular a distribuição percentual de 'perfil_preco' para ambos os modelos
distribuicao_preco_gpt_35 = df_gpt_35['perfil_preco'].value_counts(normalize=True).mul(100).to_dict()
distribuicao_preco_gpt_4 = df_gpt_4['perfil_preco'].value_counts(normalize=True).mul(100).to_dict()

# Converter a distribuição do perfil de preço para um formato legível
preco_gpt_35 = ", ".join([f"{key}: {value:.2f}%" for key, value in distribuicao_preco_gpt_35.items()])
preco_gpt_4 = ", ".join([f"{key}: {value:.2f}%" for key, value in distribuicao_preco_gpt_4.items()])

# Compilar os resultados em um DataFrame
metrica_comparacao = {
    "Métrica": [
        "Número total de restaurantes", 
        "Restaurantes únicos por nome", 
        "Restaurantes únicos por identificador", 
        "Média da quantidade de pratos por restaurante", 
        "Média do preço dos pratos por restaurante", 
        "Nota média dos restaurantes", 
        "Média de avaliações por restaurante",
        "Percentual de perfil de preço"
    ],
    "GPT-3.5-Turbo": [
        len(df_gpt_35), 
        df_gpt_35['nome'].nunique(), 
        df_gpt_35['identificador'].nunique(), 
        media_pratos_gpt_35, 
        media_preco_gpt_35, 
        media_notas_gpt_35, 
        media_avaliacoes_gpt_35,
        preco_gpt_35
    ],
    "GPT-4-Turbo": [
        len(df_gpt_4), 
        df_gpt_4['nome'].nunique(), 
        df_gpt_4['identificador'].nunique(), 
        media_pratos_gpt_4, 
        media_preco_gpt_4, 
        media_notas_gpt_4, 
        media_avaliacoes_gpt_4,
        preco_gpt_4
    ]
}

# Criar um DataFrame para a comparação
df_metrica_comparacao = pd.DataFrame(metrica_comparacao)

# Exibir o resultado
print(df_metrica_comparacao)
