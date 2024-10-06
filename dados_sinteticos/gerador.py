# exemplo de execução
# python gerador.py  --restaurantes 10 --modelo "gpt-3.5-turbo"

import json
import os
import time
import numpy as np
import argparse
import traceback
from typing import List
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_openai import ChatOpenAI
from langchain_experimental.tabular_synthetic_data.openai import create_openai_data_generator
from langchain_experimental.tabular_synthetic_data.prompts import SYNTHETIC_FEW_SHOT_PREFIX, SYNTHETIC_FEW_SHOT_SUFFIX
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

# os.environ["OPENAI_API_KEY"] = '' # sua chave aqui caso queira rodar script manualmente e debugar

# Classe que define o modelo de Prato
class Prato(BaseModel):
    nome: str
    preco: float

    def to_dict(self):
        return {
            "nome": self.nome,
            "preco": self.preco
        }

# Classe que define o modelo de Restaurante
class Restaurante(BaseModel):
    identificador: str
    nome: str
    nota_media: float
    avaliacoes: int
    categoria: str
    perfil_preco: str
    latitude: float
    longitude: float
    taxa_1000_metros: float
    taxa_2000_metros: float
    taxa_3000_metros: float
    taxa_4000_metros: float
    pratos: List[Prato] = []

    def to_dict(self):
        return {
            "identificador": self.identificador,
            "nome": self.nome,
            "nota_media": self.nota_media,
            "avaliacoes": self.avaliacoes,
            "categoria": self.categoria,
            "perfil_preco": self.perfil_preco,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "taxa_1000_metros": self.taxa_1000_metros,
            "taxa_2000_metros": self.taxa_2000_metros,
            "taxa_3000_metros": self.taxa_3000_metros,
            "taxa_4000_metros": self.taxa_4000_metros,
            "pratos": [prato.to_dict() for prato in self.pratos]
        }

# Classe que agrupa vários restaurantes
class Restaurantes(BaseModel):
    restaurantes: List[Restaurante] = []

# Exemplo de restaurantes para o template
examples = [
    {
        "example": """
            Identificador: a974406b-b6d0-4743-8235-7bd83b9e6e78, 
            Nome: Cantina do Sabor, 
            Nota Media: 4.5, 
            Avaliacoes: 120, 
            Categoria: Italiana, 
            Perfil Preco: caro, 
            Latitude: -23.5629, 
            Longitude: -46.6544, 
            Taxa 1000 metros: 7.0, 
            Taxa 2000 metros: 8.5, 
            Taxa 3000 metros: 9.0,
            Taxa 4000 metros: 10.0, 
            Pratos: [Nome: Spaghetti Carbonara, preco: R$45.0, Nome: Lasanha Bolonhesa, Preco: R$50.0]
        """
    },
    {
        "example": """
            Identificador: 475bfe4e-b02f-4e03-b985-7ecc16f8d869, 
            Nome: Churrascaria Fogo Forte, 
            Nota Media: 4.8, 
            Avaliacoes: 350, 
            Categoria: Churrascaria, 
            Perfil Preco: muito caro, 
            Latitude: -22.9068, Longitude: -43.1729, 
            Taxa 1000 metros: 0.0, 
            Taxa 2000 metros: 5.0,
            Taxa 3000 metros: 7.0,
            Taxa 4000 metros: 10.0, 
            Pratos: [Nome: Picanha na Brasa, Preco: R$85.0, Nome: Costela de Cordeiro, Preco: R$90.0]
        """
    },
    {
        "example": """
            Identificador: 7214e339-1af1-400f-8b45-17e281cc7e90, 
            Nome: Sushi Master, 
            Nota Media: 4.2, 
            Avaliacoes: 80, 
            Categoria: Japonesa, 
            Perfil Preco: barato, 
            Latitude: -19.9350, 
            Longitude: -43.9378, 
            Taxa 1000 metros: 4.0, 
            Taxa 2000 metros: 5.0, 
            Taxa 3000 metros: 6.5, 
            Taxa 4000 metros: 8.0, 
            Pratos: [Nome: Sushi Combo 15 peças, Preco: R$30.0, Nome: Temaki de Salmão, Preco: R$25.0]
        """
    }
]

# Função para gerar dados de restaurantes sintéticos
def gerar_restaurantes(quantidade, modelo):
    try:
        prompt_template = criar_prompt_template()
        data_generator = criar_data_generator(prompt_template, modelo)
        resultado = data_generator.generate(
            subject=f"Você é um gerador de dados de restaurantes, gere exatamente {quantidade} restaurantes",
            extra="""
                        - O identificador do restaurante é um uuid v4, não me gere id numerico e sequencial.
                        - Gere um nome de restaurante único e que tenha haver com a categoria escolhida.
                        - Uma pontuação deve estar entre 0.5 e 5.0.
                        - Uma quantidade de avaliações no maximo 500.
                        - Uma categoria dentre estas (Comida Brasileira, Pizzaria, Churrascaria, Hamburgueria, 
                                                    Japonês/Sushi, Mexicano, Italiana, Frutos do Mar, Lanchonete,
                                                    Comida Nordestina, Comida Mineira, Comida Peruana, Açaí, Sorveteria) 
                        - Perfil de preço deve estar entre estes (barato, caro e muito caro).
                        - Para as taxa de entrega, levar em conta estes criterios:
                            - A taxa 1000 metros pode começar com 0 em alguns caso, não todos.
                            - A taxa 4000 metros nunca deve passar de 10
                            - A taxa seguinte nunca deve ser igual ou menor que a taxa de entrega anterior, veja abaixo:
                                - 1000: 0.0, 2000: 2.5, 3000: 7.0, 4000: 10.0     (correto)
                                - 1000: 3.0, 2000: 6.0, 3000: 6.5, 4000: 8.0      (correto)
                                - 1000: 3.5, 2000: 0.0, 3000: 7.0, 4000: 10.0     (errado)
                                - 1000: 3.5, 2000: 3.5, 3000: 7.0, 4000: 10.0     (errado)
                        - Os pratos deste restaurante deve pertencer a categoria escolhida e pode gerar de 3 até 8 pratos 
                            de maneira randomica.
                        - A latitude e longitude do estabelecimento deve ser aleatorio e levando em conta o centro da 
                            cidade São Paulo, deve estar dentro de um raio de 5 km no maximo.
                    """,
            runs=1
        )
        return resultado[0].restaurantes
    except Exception as e:
        # Geração de log em caso de erro
        timestamp_unix = int(time.time())
        nome_arquivo_log = f"log_erro_{modelo}_{timestamp_unix}.log"
        
        diretorio_script = os.path.dirname(os.path.realpath(__file__))  # Diretório onde o script está localizado
        diretorio_erros = os.path.join(diretorio_script, f'erros_{modelo}')
        if not os.path.exists(diretorio_erros):
            os.makedirs(diretorio_erros)
        
        caminho_log = os.path.join(diretorio_erros, nome_arquivo_log)

        with open(caminho_log, 'a') as arquivo_log:
            arquivo_log.write(f"Erro ocorrido: {e}\n")
            arquivo_log.write("Detalhes da exceção:\n")
            arquivo_log.write(traceback.format_exc())
            arquivo_log.write("\n")

        # Retorna uma lista vazia em caso de falha para não interronper o processamento
        return []

def criar_prompt_template():
    OPENAI_TEMPLATE = PromptTemplate(input_variables=["example"], template="{example}")
    return FewShotPromptTemplate(
        prefix=SYNTHETIC_FEW_SHOT_PREFIX,
        examples=examples,
        suffix=SYNTHETIC_FEW_SHOT_SUFFIX,
        input_variables=["subject", "extra"],
        example_prompt=OPENAI_TEMPLATE,
    )

def criar_data_generator(prompt_template, modelo):
    return create_openai_data_generator(
        output_schema=Restaurantes,
        llm=ChatOpenAI(model=modelo, temperature=1),
        prompt=prompt_template
    )

def gerar(total_restaurantes, modelo):
    resultado = []
    maximo_por_chamada = 20

    tempos_execucao = []  # Lista para armazenar o tempo de cada execução bem-sucedida
    erros = 0  # Contador de erros (quando a chamada não gera restaurantes)

    # warmup (as vezes a primeira chamad demora um pouco, pode ser algo na minha rede)
    gerar_restaurantes(maximo_por_chamada, modelo)

    inicio_total = time.time()

    # Continue gerando enquanto o número de restaurantes gerados for menor que o total necessário
    while len(resultado) < total_restaurantes:
        quantidade_para_gerar = min(total_restaurantes - len(resultado), maximo_por_chamada)

        inicio = time.time() 
        restaurantes = gerar_restaurantes(quantidade_para_gerar, modelo)
        fim = time.time()

        if len(restaurantes) == 0:
            print('❌ ', end='', flush=True)
            erros += 1 
        else:
            resultado.extend(restaurantes)
            tempo_execucao = fim - inicio
            tempos_execucao.append(tempo_execucao) 
            print('✅ ', end='', flush=True)

    fim_total = time.time()

    # Se o número de restaurantes for maior que o necessário, removemos os extras
    if len(resultado) > total_restaurantes:
        resultado = resultado[:total_restaurantes]

    # Apenas para pular uma linha
    print()  

    # Calculando o tempo total do processo
    tempo_total = fim_total - inicio_total
    print(f'\nTempo total do processo: {tempo_total:.4f} segundos')

    # Gerando algumas metricas
    if tempos_execucao:
        tempo_medio = np.mean(tempos_execucao)
        percentil_50 = np.percentile(tempos_execucao, 50)
        percentil_90 = np.percentile(tempos_execucao, 90)
        percentil_95 = np.percentile(tempos_execucao, 95)
        percentil_99 = np.percentile(tempos_execucao, 99)

        print(f'Métricas de Execução (Chamadas bem-sucedidas apenas):')
        print(f'- Tempo médio por chamada: {tempo_medio:.4f} segundos')
        print(f'- Percentil 50 (mediana): {percentil_50:.4f} segundos')
        print(f'- Percentil 90: {percentil_90:.4f} segundos')
        print(f'- Percentil 95: {percentil_95:.4f} segundos')
        print(f'- Percentil 99: {percentil_99:.4f} segundos')
    else:
        print(f'\nNenhuma chamada bem-sucedida foi registrada.')

    print(f'- Total de erros: {erros}')
    print(f'- Total de chamadas: {len(tempos_execucao) + erros}\n')

    return resultado

def salvar_dados_json(modelo, dados):
    caminho_arquivo_json = gerar_caminho_arquivo(modelo)
    with open(caminho_arquivo_json, 'w', encoding='utf-8') as arquivo_json:
        json.dump([restaurante.to_dict() for restaurante in dados], arquivo_json, ensure_ascii=False)
    print(f'Arquivo JSON salvo: dados_sinteticos/sucesso_{modelo}/{os.path.basename(caminho_arquivo_json)}')

def gerar_caminho_arquivo(modelo):
    diretorio_script = os.path.dirname(os.path.realpath(__file__))  # Diretório onde o script está localizado
    diretorio_sucesso = os.path.join(diretorio_script, f'sucesso_{modelo}')
    if not os.path.exists(diretorio_sucesso):
        os.makedirs(diretorio_sucesso)
    
    timestamp = int(time.time())
    nome_arquivo = f'{modelo}_{timestamp}.json'.replace(" ", "_")
    return os.path.join(diretorio_sucesso, nome_arquivo)

def main():
    # Lista de modelos suportados pelo ChatOpenAI
    MODELOS_SUPORTADOS = ["gpt-3.5-turbo", "gpt-4-turbo"]

    parser = argparse.ArgumentParser(description='Salvar JSON com timestamp')
    parser.add_argument('--modelo', type=str, choices=MODELOS_SUPORTADOS, 
                        help=f'Escolha o modelo: {", ".join(MODELOS_SUPORTADOS)}', required=True)
    parser.add_argument('--restaurantes', type=int, help='Quantidade de restaurantes', required=True)

    args = parser.parse_args()

    restaurantes = args.restaurantes 
    modelo = args.modelo

    # Para debugar comente o trecho acima até antes de `def main():` e descomente as variaveis abaixo
    # restaurantes = 10
    # modelo = "gpt-3.5-turbo"

    # Gera os dados de restaurantes
    dados = gerar(restaurantes, modelo)

    # Salva os dados em arquivo JSON
    salvar_dados_json(modelo, dados)

    print(f'- Modelo solicitado: {modelo}')
    print(f'- Quantidade de restaurantes solicitados: {restaurantes}')
    print(f'- Quantidade de restaurantes gerados: {len(dados)}')

if __name__ == "__main__":
    main()