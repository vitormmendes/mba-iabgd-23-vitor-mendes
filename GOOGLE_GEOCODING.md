# Como Obter a Chave da Google API Geocoding

Este guia descreve os passos necessários para obter uma chave da API do Google Geocoding.

## Passos para Obtenção da Chave

### 1. Criar uma Conta no Google Cloud

Se ainda não possui uma conta no Google Cloud, siga os passos abaixo:

- Acesse o Google Cloud: [https://cloud.google.com/](https://cloud.google.com/)
- Clique em **Get Started for Free** e crie sua conta.

### 2. Criar um Novo Projeto

1. Após fazer login, no painel de controle do Google Cloud, clique em **Select a Project** no canto superior esquerdo e em seguida em **New Project**.
2. Dê um nome ao seu projeto e clique em **Create**.

### 3. Habilitar a API de Geocoding

1. No painel do Google Cloud, clique no menu de navegação (três linhas horizontais no canto superior esquerdo).
2. Selecione **APIs & Services** > **Library**.
3. Na biblioteca de APIs, pesquise por **Geocoding API**.
4. Clique em **Geocoding API** e em seguida clique no botão **Enable** para ativar a API.

### 4. Criar Credenciais da API

1. No menu de navegação à esquerda, clique em **APIs & Services** > **Credentials**.
2. Clique no botão **Create Credentials** na parte superior da página e selecione **API Key**.
3. Uma nova chave de API será gerada. **Copie essa chave**, pois você precisará dela em seu projeto.

### 5. Restringir o Uso da Chave (Opcional)

Para aumentar a segurança, você pode restringir o uso da chave de API:

1. No painel de **Credenciais**, localize sua chave recém-criada e clique no ícone de lápis ao lado para editá-la.
2. Nas configurações de **Restrição de Aplicação**, defina os domínios ou IPs autorizados a usar essa chave.
3. Nas configurações de **Restrição de API**, selecione **Geocoding API** para garantir que a chave seja usada apenas para esta API.

### 6. Utilizando a Chave da API

Agora que você tem a chave da API, pode utilizá-la no seu código para fazer solicitações ao Google Geocoding API. Aqui está um exemplo de como utilizá-la em uma requisição HTTP:

```bash
https://maps.googleapis.com/maps/api/geocode/json?address=SUA_ENDERECO_AQUI&key=SUA_CHAVE_DE_API
