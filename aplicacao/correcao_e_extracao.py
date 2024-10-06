import requests
from typing import Optional, List
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Carregar as variáveis do arquivo .env
load_dotenv()

# os.environ["OPENAI_API_KEY"] = '' # sua chave aqui caso queira rodar script manualmente e debugar
# os.environ["GOOGLE_GEOCODING_API_KEY"] = '' # sua chave aqui caso queira rodar script manualmente e debugar

class Endereco(BaseModel):
    """Informações sobre o endereço de entrega."""
    rua: Optional[str] = Field(default=None, description="Nome da rua para a entrega")
    numero: Optional[str] = Field(default=None, description="Número da residência ou local de entrega")
    bairro: Optional[str] = Field(default=None, description="Bairro do endereço")
    cidade: Optional[str] = Field(default=None, description="Cidade do endereço")
    estado: Optional[str] = Field(default=None, description="Estado do endereço")

    def to_dict(self):
        return {
            "rua": self.rua,
            "numero": self.numero,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "estado": self.estado
        }

class Prato(BaseModel):
    """Informações sobre o prato que a pessoa está buscando."""
    nome: Optional[str] = Field(default=None, description="Nome do prato")
    preco_maximo: Optional[float] = Field(default=None, description="Preço máximo que o usuário deseja pagar pelo prato")

    def to_dict(self):
        return {
            "nome": self.nome,
            "preco_maximo": self.preco_maximo
        }

class Busca(BaseModel):
    """Critérios de busca para recomendação de restaurantes."""
    identificador: Optional[str] = Field(default=None, description="Identificador único do restaurante")
    nome: Optional[str] = Field(default=None, description="Nome do restaurante")
    nota_media: Optional[float] = Field(default=None, description="Nota média mínima do restaurante")
    avaliacoes: Optional[int] = Field(default=None, description="Número mínimo de avaliações que o restaurante possui")
    categoria: Optional[str] = Field(default=None, description="Categoria de comida oferecida pelo restaurante")
    perfil_preco: Optional[str] = Field(default=None, description="Perfil de preço do restaurante (barato, caro, muito caro)")
    buscando_por_taxa_gratis: Optional[bool] = Field(default=None, description="Se o usuário está buscando restaurantes com entrega gratuita")
    taxa_de_entrega_limite: Optional[float] = Field(default=None, description="Limite máximo que o usuário deseja pagar pela taxa de entrega")
    pratos: Optional[List[Prato]] = Field(default=None, description="Lista de pratos que o usuário está buscando")
    endereco_entrega: Optional[Endereco] = Field(default=None, description="Endereço para entrega")
    endereco_indefinido: Optional[bool] = Field(default=False, description="Indica se o endereço fornecido é incompleto ou indefinido")

    def to_dict(self):
        return {
            "identificador": self.identificador,
            "nome": self.nome,
            "nota_media": self.nota_media,
            "avaliacoes": self.avaliacoes,
            "categoria": self.categoria,
            "perfil_preco": self.perfil_preco,
            "buscando_por_taxa_gratis": self.buscando_por_taxa_gratis,
            "taxa_de_entrega_limite": self.taxa_de_entrega_limite,
            "pratos": [prato.to_dict() for prato in self.pratos] if self.pratos else None,
            "endereco_entrega": self.endereco_entrega.to_dict() if self.endereco_entrega else None,
            "endereco_indefinido": self.endereco_indefinido
        }

# Função para buscar latitude e longitude com a API do Google
def obter_latitude_longitude_google(endereco):
    chave_api = os.environ["GOOGLE_GEOCODING_API_KEY"]
    endereco_str = f"{endereco.get('rua', '')}, {endereco.get('numero', '')}, {endereco.get('bairro', '')}, {endereco.get('cidade', '')}, {endereco.get('estado', '')}"
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={endereco_str}&key={chave_api}"
    resposta = requests.get(url)
    dados = resposta.json()

    if dados['status'] == 'OK':
        coordenadas = dados['results'][0]['geometry']['location']
        return coordenadas['lat'], coordenadas['lng']
    else:
        return None

# Definindo o prompt para o modelo de extração
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Você é um algoritmo especializado em corrigir e extrair critérios de busca de restaurantes. "
            "Extraia apenas as informações relevantes do texto. "
            "Só preencha a 'categoria' se ela pertencer à lista de categorias permitidas. "
            "Se o endereço fornecido estiver incompleto ou vago (faltando rua ou número), preencha o campo 'endereco_indefinido' como True. "
            "Se o campo 'endereco_entrega' não for mencionado, o 'endereco_indefinido' deve ser False. "
            "Se você não souber o valor de um atributo solicitado para extração, "
            "retorne nulo para o valor do atributo.",
        ),
        ("human", "{texto}"),
    ]
)

modelo = ChatOpenAI(model="gpt-4-turbo", temperature=1)

chain = prompt | modelo.with_structured_output(schema=Busca)

def processar_busca(texto):
    print("\n- Texto:", texto)
    resultado = chain.invoke({"texto": texto}).to_dict()
    print(json.dumps(resultado, indent=4, ensure_ascii=False))
    return resultado

def gerar_prompt(busca):
    prompt_parts = ["Estou buscando restaurantes com os seguintes critérios abaixo:"]

    # Nome do restaurante
    if busca.get('nome'):
        prompt_parts.append(f"- Nome do restaurante: {busca['nome']}")

    # Nota média mínima
    if busca.get('nota_media'):
        prompt_parts.append(f"- Nota média mínima: {busca['nota_media']}")

    # Avaliações mínimas
    if busca.get('avaliacoes'):
        prompt_parts.append(f"- Pelo menos {busca['avaliacoes']} avaliações")

    # Categoria
    if busca.get('categoria'):
        prompt_parts.append(f"- Categoria: {busca['categoria']}")

    # Perfil de preço
    if busca.get('perfil_preco'):
        prompt_parts.append(f"- Perfil de preço: {busca['perfil_preco']}")

    # Taxa de entrega grátis
    if busca.get('buscando_por_taxa_gratis'):
        prompt_parts.append(f"- Entrega grátis: Sim")

    # Limite de taxa de entrega
    if busca.get('taxa_de_entrega_limite'):
        prompt_parts.append(f"- Limite da taxa de entrega: até {busca['taxa_de_entrega_limite']} reais")

    # Pratos
    if busca.get('pratos'):
        prompt_parts.append("- Pratos desejados:")
        for prato in busca['pratos']:
            prato_desc = f"  - {prato['nome']}"
            if prato.get('preco_maximo'):
                prato_desc += f" (até {prato['preco_maximo']} reais)"
            prompt_parts.append(prato_desc)

    # Endereço
    if busca.get('endereco_entrega') and not busca.get('endereco_indefinido'):
        endereco = busca['endereco_entrega']
        endereco_parts = []
        if endereco.get('rua'):
            endereco_parts.append(f"Rua: {endereco['rua']}")
        if endereco.get('numero'):
            endereco_parts.append(f"Número: {endereco['numero']}")
        if endereco.get('bairro'):
            endereco_parts.append(f"Bairro: {endereco['bairro']}")
        if endereco.get('cidade'):
            endereco_parts.append(f"Cidade: {endereco['cidade']}")
        if endereco.get('estado'):
            endereco_parts.append(f"Estado: {endereco['estado']}")
        
        # Obter latitude e longitude usando a API do Google
        coordenadas = obter_latitude_longitude_google(endereco)
        
        if coordenadas:
            latitude, longitude = coordenadas
            prompt_parts.append(f"- Latitude: {latitude}, Longitude: {longitude}, buscando restaurantes em um raio de 5 km")

    prompt_final = "\n".join(prompt_parts)

    print(f'\n{prompt_final}')

    return prompt_final