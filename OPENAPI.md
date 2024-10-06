# Como Obter a Chave da API da OpenAI

Este guia mostra como obter a chave de acesso da API da OpenAI e utilizá-la no seu projeto.

## 1. Criar uma Conta na OpenAI

Se ainda não possui uma conta, siga os passos abaixo:

- Acesse o site oficial da OpenAI: [https://platform.openai.com/](https://platform.openai.com/)
- Crie sua conta.

## 2. Acessar o Painel de Controle

- Após o login, você será redirecionado ao painel de controle da OpenAI.

## 3. Navegar até a Página de API Keys

- No painel de controle, clique em **API** no menu à esquerda.
- Em seguida, clique em **API Keys** ou acesse diretamente: [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys).

## 4. Gerar uma Nova Chave

- Clique no botão **Create new secret key**.
- Uma nova chave será gerada. **Copie esta chave imediatamente**, pois ela não será exibida novamente.

## 5. Armazenar a Chave com Segurança

- Guarde a chave em um local seguro, como um gerenciador de senhas.
- Você precisará dela para autenticar suas requisições à API.

## Exemplo de Uso da Chave

Após obter a chave, você pode utilizá-la em seu código. Veja um exemplo em Python:

```python
import openai

openai.api_key = "SUA_CHAVE_AQUI"

response = openai.Completion.create(
  model="text-davinci-003",
  prompt="Escreva um exemplo de uso da OpenAI API",
  max_tokens=100
)

print(response.choices[0].text)
