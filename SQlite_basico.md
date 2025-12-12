Esse é um projeto de aprendizado em banco de dados que estou iniciando, meu foco será em python, estou usando a extensão nativa dele que é o SQlite.

O projeto funciona da seguinte forma

1 ° Eu faço uma lista de algumas empresas de bebidas com CNPJs cadastrados no brasil.
Com essa informação eu faço duas tabelas diretamente relacionadas em um arquivo    .db

A primeira tabela tem as informações: Nome da empresa, nome fantasia (se existir), CNPJ e situação cadastral

Já segunda a planilha pega as informações de localização da empresa, que seriam: ID (para que a planilha consiga se achar na planilha anterior), endereço, número, bairro, Município, estado e CEP

2° Sobre as ferramentas utilizadas:
Utilizei as bibliotecas, Sqlite3, Time e Requests.

A ferramenta Requests deve ser instalada com o comando Pip no terminal
Usamos o Cursor para poder criar e editar todas as planilhas criadas neste código

A comunicação por Request é feita com uma API open source(brasilapi.com.br).
Por fim o código rodará em loop até que complete a consulta de todas as empresas que estão na lista “empresas_de_bebidas_cnpjs” 

3° O  processo de Request acontece da seguinte forma, o comando entra em contato com a Api e coleta a informação que já está quase pronta (mais mastigada), essa informação por sua vez ainda passa ferramenta .Json para que possa ser lida pelo python, por fim a informação é armazenada pelo comando Commit dentro do arquivo empresas_de_bebidas_no_brasil.db
