Continuando com a versão 2 do projeto de análise de empresas, foram implementadas algumas mudanças importantes:

1. Mudamos o segmento alvo para empresas do setor elétrico.

2. Além de coletar informações cadastrais no arquivo .db, o programa agora armazena informações de valores na bolsa (B3) e gera gráficos com o valor de mercado e a oscilação do último mês.

Novas Ferramentas e Bibliotecas: Foram adicionadas as bibliotecas yfinance e matplotlib.

* A primeira é utilizada para extrair os dados financeiros das empresas pesquisadas.

* A segunda é utilizada para a geração e visualização dos gráficos.

Melhorias na Estrutura do Código: Algumas alterações foram feitas para deixá-lo mais dinâmico e organizado:

* A lista inicial das empresas foi substituída por um dicionário, facilitando o mapeamento e o acesso às informações.

* Foi adotada a utilização de funções (modularização), com o intuito de tornar o código mais limpo, dinâmico e menos propenso a erros (bugs).
