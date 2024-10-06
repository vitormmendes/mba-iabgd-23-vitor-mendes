
Substitua os valores acima pelas chaves geradas em suas respectivas plataformas.

## Instruções de criação do arquivo `.env`

### Linux/macOS

1. Navegue até o diretório raiz do projeto no explorador de arquivos ou via terminal.

2. Abra algum editor de texto ou use de `vi` ou `vim` ou `nano`.

3. Adicione as chaves de API no arquivo e salve. O conteúdo deve ser como este:
    ```
    OPENAI_API_KEY=chave_openai_gerada
    GOOGLE_GEOCODING_API_KEY=chave_google_geocoding_gerada
    ```

4. Salve o arquivo com o nome `.env`.

### Windows

1. Navegue até o diretório raiz do projeto no explorador de arquivos.

2. Abra o **Bloco de Notas** ou outro editor de texto.

3. Crie um novo arquivo e adicione as chaves de API no formato:
    ```
    OPENAI_API_KEY=chave_openai_gerada
    GOOGLE_GEOCODING_API_KEY=chave_google_geocoding_gerada
    ```

4. Salve o arquivo com o nome `.env` (garanta que está selecionado o tipo de arquivo **Todos os arquivos** no momento de salvar para evitar a extensão `.txt`).

## Cuidados com as Chaves de API

- **Mantenha suas chaves seguras**: Nunca compartilhe suas chaves de API publicamente. Elas são usadas para acessar serviços pagos e devem ser mantidas privadas para evitar abusos.
- **Revogação de chaves comprometidas**: Se você suspeitar que sua chave foi exposta ou comprometida, gere uma nova chave e atualize seu arquivo `.env`.
- **Verifique permissões**: No Linux e macOS, certifique-se de que o arquivo `.env` não tenha permissões excessivas. Isso pode ser feito com o seguinte comando:
    ```bash
    chmod 600 .env
    ```
