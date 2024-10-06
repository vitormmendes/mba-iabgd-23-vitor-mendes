import streamlit as st
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
import os
from dotenv import load_dotenv
import argparse
from correcao_e_extracao import processar_busca, obter_latitude_longitude_google
from cabecalho import gerar_cabecalho

# Carregar as variáveis do arquivo .env
load_dotenv()

# Definir o ambiente headless para desabilitar o botão de deploy
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

# os.environ["OPENAI_API_KEY"] = '' # sua chave aqui caso queira rodar script manualmente e debugar
# os.environ["GOOGLE_GEOCODING_API_KEY"] = '' # sua chave aqui caso queira rodar script manualmente e debugar

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

# Configuração da página
st.set_page_config(page_title="Sistema de Recomendação de Restaurantes", page_icon="🍽️", layout="centered", initial_sidebar_state="auto", menu_items=None)

gerar_cabecalho()

st.markdown("<br><h6>Uma maneira disruptiva para se pedir comida</h6>", unsafe_allow_html=True)

# Inicializa o histórico de mensagens
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Como posso te ajudar? me diga que tipo de comida você pretende comer e eu posso te indicar diversos restaurantes!",
        }
    ]

parser = argparse.ArgumentParser(description='Tratar dados')
parser.add_argument('--diretorio', type=str, help='Diretorio aonde se encontra arquivo que vamos processar', required=True)

args = parser.parse_args()

diretorio = args.diretorio

@st.cache_resource(show_spinner=False)
def load_data():
    reader = SimpleDirectoryReader(input_dir=diretorio, recursive=True)
    docs = reader.load_data()
    Settings.llm = OpenAI(
        model="gpt-3.5-turbo",
        temperature=1,
        system_prompt="""Você é um especialista em recomendações de restaurantes. Seu trabalho é sugerir restaurantes com base nos critérios que o usuário fornecer.""",
    )
    index = VectorStoreIndex.from_documents(docs)
    return index

index = load_data()

# Inicializa o motor de chat com LlamaIndex
if "chat_engine" not in st.session_state.keys():
    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode="condense_question", verbose=True, streaming=True
    )

# Captura a entrada do usuário
if prompt := st.chat_input("Digite suas preferências para recomendação de restaurantes"):
    st.session_state.messages.append({"role": "user", "content": prompt})

# Exibe o histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=("👤" if message["role"] == "user" else "🤖")):
        st.write(message["content"])

# Gera a resposta com base na entrada do usuário
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar="🤖"):
        # Processa a última mensagem do usuário usando `processar_buscas`
        user_input = st.session_state.messages[-1]["content"]
        
        # Chama `processar_buscas` para analisar a entrada do usuário e gerar um objeto de busca
        busca = processar_busca(user_input)

        # Gera o prompt com base na extração dos dados
        prompt_gerado = gerar_prompt(busca)

        formatacao_saida = ("""Sempre exiba a resposta seguindo este padrão abaixo de exemplo em markdown, caso você responda um restaurante ou N restaurantes
        Restaurante: {nome}
        Categoria: {categoria}
        Avaliações: {avaliacoes} avaliações
        Nota média: {nota_media} (com duas casas decimais apenas)
        Distância: Aproximadamente {distancia_centroid} km do centro de São Paulo
        Perfil de Preço: {prefil_preco}

        Taxas de Entrega: {taxa_1000_metros, taxa_2000_metros, taxa_3000_metros e taxa_4000_metros}
            Até 1 km: Grátis
            De 1 km a 2 km: R$ 2,00
            De 2 km a 3 km: R$ 6,00
            De 3 km a 4 km: R$ 9,00
        Pratos: {pratos}
            Picanha na Brasa - R$ 85,00
            Costela de Porco - R$ 70,00
            Cordeiro Assado - R$ 90,00
        """)

        busca_final = (f""" 
        O usuario digitou isto aqui: 
                       {user_input}   
                        
        Eu consegui extrair estas informações para a busca sair melhor:
                       {prompt_gerado}    

        Sempre formate a resposta com os dados disponiveis dos restaurantes em markdown
        Sempre que retorna a taxa de entrega, seja em reais ex.: R$10.00
        Não retorne o campo localização
        Sempre retorne:
            Nome
            Avaliações
            Categoria
            Note Media
            Perfil Preço
            Taxas de Entrega
                Até 1km, usar valor do campo taxa_1000_metros preço em reais
                Até 2km, usar valor do campo taxa_2000_metros preço em reais
                Até 3km, usar valor do campo taxa_3000_metros preço em reais
                Até 4km, usar valor do campo taxa_4000_metros preço em reais
            Pratos
        """)

        print(busca_final)
        
        # Chama o motor de chat para gerar a resposta com base no prompt gerado
        response_stream = st.session_state.chat_engine.stream_chat(busca_final)
        st.write_stream(response_stream.response_gen)

        message = {"role": "assistant", "content": response_stream.response}
        # Adiciona a resposta ao histórico de mensagens
        st.session_state.messages.append(message)