Continuando com a versão 2 do projeto de análise de empresas, foram implementadas algumas mudanças importantes:
Empresas Elétricas Versão 1 
  1. **Mudança de Segmento:** Foi mudado o segmento alvo para empresas do setor elétrico.
  
  2. **Mudança na coleta de informações:** Além de coletar informações cadastrais no arquivo .db, o programa agora armazena              informações de valores na bolsa (B3), gera gráficos com o valor de mercado e a oscilação do último mês.
  
      2.1: **Novas Ferramentas e Bibliotecas:** Foram adicionadas as bibliotecas `yfinance` e `matplotlib`.
  
      * A primeira é utilizada para extrair os dados financeiros das empresas pesquisadas.
  
      * A segunda é utilizada para gerar os gráficos
  
      2.2: **Melhorias na Estrutura do Código:** Algumas alterações foram feitas para deixá-lo mais dinâmico e organizado:
  
      * A lista inicial das empresas foi substituída por um dicionário, facilitando o mapeamento e o acesso às informações.
  
      * Foi adotada a utilização de funções, com o intuito de tornar o código mais limpo, dinâmico e menos propenso a bugs.
3. **Observações Importantes**
   
**Manutenção da API:** É fundamental manter a biblioteca `yfinance` sempre atualizada. Como o Yahoo Finance altera sua estrutura com frequência, versões antigas da biblioteca podem falhar na extração dos dados.
* **Dependências:** Para a execução correta do projeto, é necessário instalar as seguintes bibliotecas externas: `yfinance`, `matplotlib` e `pandas`.


**Empresas Elétricas - Versão 2**

1.  **Interatividade:** Nesta versão, foi dada mais autonomia ao usuário para escolher o período financeiro que mais lhe agrada. Além disso, agora é possível interagir diretamente com os gráficos gerados.
   
2.  **Mudanças principais de código:** O `matplotlib` foi retirado para dar espaço às ferramentas do `plotly`. O motivo da alteração deve-se à versatilidade da nova ferramenta, que oferece ao usuário muito mais autonomia na interação com o código.
   
3.  **Observação:** É necessário instalar a biblioteca `plotly` para que haja o perfeito funcionamento da ferramenta.
