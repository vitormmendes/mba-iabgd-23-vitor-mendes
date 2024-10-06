import os
import pandas as pd
import numpy as np
from glob import glob
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
from geopy.distance import geodesic, distance
from shapely.geometry import Point
import math
import random
import argparse
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

# Coordenadas do centro de São Paulo
CENTROID_LATITUDE = -23.5505
CENTROID_LONGITUDE = -46.6333
centro_sao_paulo = (CENTROID_LATITUDE, CENTROID_LONGITUDE)

def carregar_arquivos_json(diretorio):
    arquivos = glob(os.path.join(diretorio, 'gpt*.json'))
    lista_restaurantes = []
    for arquivo in arquivos:
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = pd.read_json(f)
            lista_restaurantes.append(dados)
    return pd.concat(lista_restaurantes, ignore_index=True)

def tratar_valores_nulos(df):
    df['avaliacoes'].fillna(df['avaliacoes'].median(), inplace=True)
    df['pratos'] = df['pratos'].apply(lambda x: [prato for prato in x 
                                                 if prato['preco'] is not None 
                                                 and prato['preco'] >= 0])
    df['pratos'].replace([], np.nan, inplace=True)
    df.dropna(subset=['pratos'], inplace=True)
    return df

def rebalancear_classes(df):
    smote = SMOTE(sampling_strategy='auto')

    classes_count = df['categoria'].value_counts()
    classes_adequadas = classes_count[classes_count > 1].index.tolist()
    
    df_filtrado = df[df['categoria'].isin(classes_adequadas)]
    
    X = df_filtrado.drop(columns=['categoria', 'identificador', 'nome', 'pratos', 'latitude', 'longitude', 'perfil_preco'])
    y = df_filtrado['categoria']
    
    # Aplicar SMOTE
    if not X.empty and len(classes_adequadas) > 1:
        X_res, y_res = smote.fit_resample(X, y)
        
        # Restaurar as colunas removidas após o rebalanceamento
        df_resample = pd.concat([X_res, y_res], axis=1)
        df_resample = pd.merge(df_resample, df[['identificador', 'nome', 'pratos', 'latitude', 'longitude', 'perfil_preco']], left_index=True, right_index=True)
        return df_resample
    else:
        print("Não há classes suficientes para aplicar SMOTE.")
        return df  # Retorna o DataFrame original se SMOTE não puder ser aplicado

def calcular_distancia(df):
    centro_sao_paulo = (CENTROID_LATITUDE, CENTROID_LONGITUDE)  # Latitude e longitude do centro de São Paulo
    
    def distancia(row):
        if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
            try:
                return geodesic((row['latitude'], row['longitude']), centro_sao_paulo).kilometers
            except ValueError:
                return np.nan  # Caso alguma coordenada seja inválida
        else:
            return np.nan  # Se latitude ou longitude estiverem ausentes
    
    df['distancia_centroid'] = df.apply(distancia, axis=1)
    
    return df

def filtrar_restaurantes_distancia(df, max_dist_km=5):
    df = calcular_distancia(df)
    
    df_filtrado = df[df['distancia_centroid'] <= max_dist_km]
    
    return df_filtrado

def redistribuir_restaurantes_geodesia(df, centro_lat, centro_lon, raio_km=5):
    num_restaurantes = len(df)
    redistribuidos_lat = []
    redistribuidos_lon = []
    
    for _ in range(num_restaurantes):
        angulo = random.uniform(0, 2 * math.pi)
        
        distancia = math.sqrt(random.uniform(0, 1)) * raio_km  # Distribuição uniforme
        
        nova_coordenada = distance(kilometers=distancia).destination((centro_lat, centro_lon), math.degrees(angulo))
        
        redistribuidos_lat.append(nova_coordenada.latitude)
        redistribuidos_lon.append(nova_coordenada.longitude)
    
    df['latitude'] = redistribuidos_lat
    df['longitude'] = redistribuidos_lon
    
    return df

def remover_duplicados(df):
    df['duplicado'] = df.duplicated(subset=['identificador'], keep=False) | df.duplicated(subset=['nome'], keep=False)
    
    df_sem_duplicados = df[~df['duplicado']]
    
    df_sem_duplicados = df_sem_duplicados.drop(columns=['duplicado'])
    
    return df_sem_duplicados

# Função para calcular e exibir métricas de remoção e redistribuição
def calcular_metricas(df_original, df_tratado_nulos, df_tratado_duplicados, df_tratado_rebalanceado, df_tratado_redistribuido):
    # Total inicial
    total_inicial = len(df_original)
    
    # Métrica de remoção de valores nulos e inválidos
    total_apos_remocao_nulos = len(df_tratado_nulos)
    percentual_remocao_nulos = 100 * (total_inicial - total_apos_remocao_nulos) / total_inicial
    print(f"Remoção de valores nulos/inválidos: {total_inicial - total_apos_remocao_nulos} registros removidos ({percentual_remocao_nulos:.2f}%)")
    
    # Métrica de remoção de duplicados
    total_apos_remocao_duplicados = len(df_tratado_duplicados)
    percentual_remocao_duplicados = 100 * (total_apos_remocao_nulos - total_apos_remocao_duplicados) / total_apos_remocao_nulos
    print(f"Remoção de duplicados: {total_apos_remocao_nulos - total_apos_remocao_duplicados} registros removidos ({percentual_remocao_duplicados:.2f}%)")
    
    # Métrica de rebalanceamento de classes
    total_apos_rebalanceamento = len(df_tratado_rebalanceado)
    percentual_rebalanceamento = 100 * (total_apos_remocao_duplicados - total_apos_rebalanceamento) / total_apos_remocao_duplicados
    print(f"Rebalanceamento de classes: {total_apos_remocao_duplicados - total_apos_rebalanceamento} registros ajustados ({percentual_rebalanceamento:.2f}%)")
    
    # Métrica de redistribuição geográfica (usando distâncias)
    distancia_media_rebalanceado = df_tratado_rebalanceado['distancia_centroid'].mean()
    distancia_media_redistribuida = df_tratado_redistribuido['distancia_centroid'].mean()
    print(f"Distância média do centro de São Paulo antes da redistribuição: {distancia_media_rebalanceado:.2f} km")
    print(f"Distância média do centro de São Paulo após a redistribuição: {distancia_media_redistribuida:.2f} km")
    
    # Métrica de alteração na distribuição geográfica
    diferenca_distancia = distancia_media_rebalanceado - distancia_media_redistribuida
    percentual_diferenca = 100 * abs(diferenca_distancia) / distancia_media_rebalanceado
    print(f"Ajuste na distribuição geográfica: diferença média de {diferenca_distancia:.2f} km, que representa um ajuste de {percentual_diferenca:.2f}%")

def tratar_dados_e_metricas(diretorio):
    df_original = carregar_arquivos_json(diretorio)  # Carregar dados originais
    print(f'df_original = {len(df_original)}')
    
    # Tratamento de valores nulos ou inválidos
    df_tratado_nulos = tratar_valores_nulos(df_original.copy())
    print(f'df_tratado_nulos = {len(df_tratado_nulos)}')
    
    # Filtrar restaurantes que estão a mais de 5 km do centro de São Paulo
    df_tratado_distancia_maior = filtrar_restaurantes_distancia(df_tratado_nulos)
    print(f'df_tratado_distancia_maior = {len(df_tratado_distancia_maior)}')
    
    # Remoção de duplicados
    df_tratado_duplicados = remover_duplicados(df_tratado_distancia_maior)
    print(f'df_tratado_duplicados = {len(df_tratado_duplicados)}')
    
    # Rebalanceamento das classes
    df_tratado_rebalanceado = rebalancear_classes(df_tratado_duplicados)
    print(f'df_tratado_rebalanceado = {len(df_tratado_rebalanceado)}')

    # Redistribuir restaurantes usando geodesia
    df_tratado_redistribuido = redistribuir_restaurantes_geodesia(df_tratado_rebalanceado.copy(), CENTROID_LATITUDE, CENTROID_LONGITUDE)
    print(f'df_tratado_redistribuido = {len(df_tratado_redistribuido)}')
    
    # Calcular a distância do centro de São Paulo para ambos os dataframes
    df_original = calcular_distancia(df_original)
    df_tratado_redistribuido = calcular_distancia(df_tratado_redistribuido)
    
    # Gerar arquivo JSON final mantendo a estrutura original
    if not os.path.exists("pos_processamento/dados"):
        os.makedirs("pos_processamento/dados")

    df_original.to_json('pos_processamento/dados/restaurantes_original.json', orient='records', force_ascii=False, indent=4)
    df_tratado_rebalanceado.to_json('pos_processamento/dados/restaurantes_tratados.json', orient='records', force_ascii=False, indent=4)
    df_tratado_redistribuido.to_json('pos_processamento/dados/restaurantes_redistribuidos.json', orient='records', force_ascii=False, indent=4)

    # Calcular e exibir métricas
    calcular_metricas(df_original, df_tratado_nulos, df_tratado_duplicados, df_tratado_rebalanceado, df_tratado_redistribuido)

    return df_original, df_tratado_rebalanceado, df_tratado_redistribuido

def desenhar_circulo_geodesico(ax, centro_lat, centro_lon, raio_km):
    num_pontos = 100
    angulos = np.linspace(0, 360, num_pontos)
    circulo_lat = []
    circulo_lon = []
    
    for angulo in angulos:
        ponto = distance(kilometers=raio_km).destination((centro_lat, centro_lon), angulo)
        circulo_lat.append(ponto.latitude)
        circulo_lon.append(ponto.longitude)
    
    ax.plot(circulo_lon, circulo_lat, color='red', linestyle='--', linewidth=2)

def gerar_graficos_comparacao(df_original, df_tratado, df_redistribuido):
    pasta_graficos = 'pos_processamento/graficos'
    os.makedirs(pasta_graficos, exist_ok=True)
    
    # Gráfico 1: Localização dos restaurantes (Antes)
    total_antes = len(df_original)
    plt.figure(figsize=(8, 8))
    ax1 = plt.gca()
    plt.scatter(df_original['longitude'], df_original['latitude'], color='blue', alpha=0.5, label=f'Antes ({total_antes})')
    desenhar_circulo_geodesico(ax1, CENTROID_LATITUDE, CENTROID_LONGITUDE, 5)
    plt.title('Localização dos Restaurantes - Antes do Tratamento')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()
    plt.savefig(os.path.join(pasta_graficos, 'localizacao_restaurantes_antes.png'))
    
    # Gráfico 2: Localização dos restaurantes (Depois)
    total_depois = len(df_tratado)
    plt.figure(figsize=(8, 8))
    ax2 = plt.gca()
    plt.scatter(df_tratado['longitude'], df_tratado['latitude'], color='green', alpha=0.5, label=f'Depois ({total_depois})')
    desenhar_circulo_geodesico(ax2, CENTROID_LATITUDE, CENTROID_LONGITUDE, 5)
    plt.title('Localização dos Restaurantes - Depois do Tratamento')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()
    plt.savefig(os.path.join(pasta_graficos, 'localizacao_restaurantes_depois.png'))
    
    # Gráfico 3: Localização dos restaurantes (Redistribuídos)
    total_redistribuidos = len(df_redistribuido)
    plt.figure(figsize=(8, 8))
    ax3 = plt.gca()
    plt.scatter(df_redistribuido['longitude'], df_redistribuido['latitude'], color='orange', alpha=0.5, label=f'Redistribuído ({total_redistribuidos})')
    desenhar_circulo_geodesico(ax3, CENTROID_LATITUDE, CENTROID_LONGITUDE, 5)
    plt.title('Localização dos Restaurantes - Redistribuídos')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()
    plt.savefig(os.path.join(pasta_graficos, 'localizacao_restaurantes_redistribuidos.png'))

def main():
    parser = argparse.ArgumentParser(description='Tratar dados')
    parser.add_argument('--diretorio', type=str, help='Diretion aonde se encontra arquivo que vamos processar', required=True)

    args = parser.parse_args()

    diretorio = args.diretorio

    df_original, df_tratado_rebalanceado, df_tratado_redistribuido = tratar_dados_e_metricas(diretorio)

    gerar_graficos_comparacao(df_original, df_tratado_rebalanceado, df_tratado_redistribuido)

    print("Dados tratados, redistribuídos e gráficos salvos na pasta 'graficos_comparacao'.")

if __name__ == "__main__":
    main()
