import geojson
from geojson import Feature, FeatureCollection
from shapely.geometry import Point, Polygon
import math
import os
import processar as p
from geopy.distance import distance
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

# Coordenadas do centro de São Paulo
CENTROID_LATITUDE = -23.550520
CENTROID_LONGITUDE = -46.633309
centro_sao_paulo = Point(CENTROID_LONGITUDE, CENTROID_LATITUDE)

def create_geodesic_circle(center_lat, center_lon, radius_km, num_points=100):
    coords = []
    for i in range(num_points):
        angle = math.pi * 2 * i / num_points
        destination = distance(kilometers=radius_km).destination((center_lat, center_lon), math.degrees(angle))
        coords.append([destination.longitude, destination.latitude])  # Usar lista em vez de tupla
    coords.append(coords[0])  # Fechar o polígono
    return Polygon(coords)

circle_geodesic = create_geodesic_circle(CENTROID_LATITUDE, CENTROID_LONGITUDE, 5)

def gerar_geojson(df, nome_arquivo):
    points = []
    
    if 'distancia_centroid' not in df.columns:
        print(f"Erro: a coluna 'distancia_centroid' não foi encontrada no DataFrame.")
        return
    
    for index, row in df.iterrows():
        latitude = row['latitude']
        longitude = row['longitude']
        point = Point(longitude, latitude)
        
        # Criar um feature com o ponto, o ID do restaurante e a distância calculada
        feature = Feature(geometry=point, properties={
            'id': row['identificador'],
            'distancia_centroid': row['distancia_centroid']
        })
        points.append(feature)
    
    circle_geojson = Feature(geometry=circle_geodesic, properties={'name': 'Raio de 5 km em torno do Centro de Sao Paulo'})
    
    centro_sao_paulo_feature = Feature(geometry=centro_sao_paulo, properties={
        'name': 'Centro de Sao Paulo',
        'marker-color': '#FF0000'  # Cor vermelha para o marcador do centro
    })
    
    geojson_feature_collection = FeatureCollection(points + [circle_geojson, centro_sao_paulo_feature])
    
    with open(nome_arquivo, 'w') as f:
        geojson.dump(geojson_feature_collection, f)
    
    print(f"GeoJSON '{nome_arquivo}' criado com sucesso!")

def gerar_geojsons_comparacao(df_original, df_tratado, df_redistribuido):
    
    pasta_geojson = 'geojson_comparacao'
    os.makedirs(pasta_geojson, exist_ok=True)
    
    df_original = p.calcular_distancia(df_original)
    df_tratado = p.calcular_distancia(df_tratado)
    df_redistribuido = p.calcular_distancia(df_redistribuido)
    
    gerar_geojson(df_original, os.path.join(pasta_geojson, 'restaurantes_antes.geojson'))
    
    gerar_geojson(df_tratado, os.path.join(pasta_geojson, 'restaurantes_depois.geojson'))
    
    gerar_geojson(df_redistribuido, os.path.join(pasta_geojson, 'restaurantes_redistribuidos.geojson'))

diretorio = '/Users/vitor.moreira/Downloads/MBA - Conteudo/TCC/new/teste'  # Caminho correto
df_tratado, df_redistribuido = p.tratar_dados_e_metricas(diretorio)

# Gerar GeoJSONs
gerar_geojsons_comparacao(df_original=p.carregar_arquivos_json(diretorio), df_tratado=df_tratado, df_redistribuido=df_redistribuido)
