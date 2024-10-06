import correcao_e_extracao as ce
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

# Chamada para todos os exemplos:
# ce.gerar_prompt(ce.processar_busca("""Quero um piza com entrega gratis para entregar no centro"""))
# ce.gerar_prompt(ce.processar_busca("""Quero um restaurante com entrega gratis e com nota maior que 4.5, pode ser de qualquer tipo de comida"""))
# ce.gerar_prompt(ce.processar_busca("""To procurando um lugar que venda pizza barato e que tenha pelo menos umas 500 avaliações"""))
# ce.gerar_prompt(ce.processar_busca("""Onde encontro um restaurante japones com mais de 100 avaliacoes e nota acima de 4?"""))
# ce.gerar_prompt(ce.processar_busca("""Procuro restaurante mineiro com taxa de entrega grátis, e que fique proximo ao centro da cidade"""))
# ce.gerar_prompt(ce.processar_busca("""Preciso de um restaurante mexicano com nota minima de 4.2 e que entrega na rua dos Alfeneiros, número 12"""))
# ce.gerar_prompt(ce.processar_busca("""Estou a procura de algum restaurante de comida japonesa, cuja a entrega seja gratis e que tenha mais de 300 avaliações e a sua nota seja maior do que 4"""))
# ce.gerar_prompt(ce.processar_busca("""Quero comer um hamburguer, qual é o melhor restaurante perto do meu endereço, av praça da sé, 205, são paulo"""))
# ce.gerar_prompt(ce.processar_busca("""Estou a procura de algum restaurante de comida japonesa, cuja a entrega seja gratis e que tenha mais de 300 avaliações e a sua nota seja maior do que 4"""))
# ce.gerar_prompt(ce.processar_busca("""Quero um restaurante com entrega gratis e com nota maior que 4.5, pode ser de qualquer tipo de comida"""))
# ce.gerar_prompt(ce.processar_busca("""To procurando um lugar que venda pizza barato e que tenha pelo menos umas 500 avaliações"""))
# ce.gerar_prompt(ce.processar_busca("""Onde encontro um restaurante japones com mais de 100 avaliacoes e nota acima de 4?"""))
# ce.gerar_prompt(ce.processar_busca("""Procuro restaurante mineiro com taxa de entrega grátis, e que fique proximo ao centro da cidade"""))
# ce.gerar_prompt(ce.processar_busca("""Quero comer comida italiana, mas só vou pedir se a entrega for gratis e tiver um prato de macarrão até 40 reais"""))
# ce.gerar_prompt(ce.processar_busca("""Tem algum restaurante de hamburguer com mais de 300 reviews e taxa de entrega maxima de 5 reais?"""))
# ce.gerar_prompt(ce.processar_busca("""Preciso de um restaurante mexicano com nota minima de 4.2 e que entrega na rua dos Alfeneiros, número 12"""))
# ce.gerar_prompt(ce.processar_busca("""Gostaria de um restaurante de comida árabe, com perfil de preço caro e entrega grátis"""))
# ce.gerar_prompt(ce.processar_busca("""To buscando um restaurante que tenha sushi e mais de 200 avaliacoes, pode ser na avenida paulista"""))
# ce.gerar_prompt(ce.processar_busca("""Tem algum restaurante com perfil muito caro, que venda sobremesas e entrega na rua da Mooca?"""))
ce.gerar_prompt(ce.processar_busca("""Estou procurando um restaurante de comida mexicana chamado El Sombrero, 
                                      com nota média acima de 4.5 e mais de 150 avaliações. 
                                      O perfil de preço deve ser caro, e estou buscando por tacos e burritos, 
                                      que não custem mais que 30 e 25 reais, respectivamente. 
                                      A entrega precisa ser gratuita, e a taxa de entrega máxima que posso pagar é de 10 reais. 
                                      O endereço de entrega é na Rua dos Alfeneiros, número 12, bairro Jardim, 
                                      na cidade de São Paulo, estado SP."""))
