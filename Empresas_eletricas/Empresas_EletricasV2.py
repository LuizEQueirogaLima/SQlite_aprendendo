import sqlite3
import requests
import time
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go 
from plotly.subplots import make_subplots

# Definindo Empresas para a pesquisa.
empresas_ticker = {
    '02474103000119': 'EGIE3.SA',   # Engie Brasil
    '03220438000173': 'EQTL3.SA',   # Equatorial
    '02429144000193': 'CPFE3.SA',   # CPFL
    '17155730000164': 'CMIG4.SA',   # CEMIG
    '00864214000106': 'ENGI11.SA',  # Energisa
    '07859971000130': 'TAEE11.SA',  # TAESA
    '01083200000118': 'NEOE3.SA'    # Neoenergia    
}

nome_Banco_Empresas = 'setor_eletrico.db'


#Função de interação com o usuário
def solicitar_periodo_usuario():
    opcoes = {
        '1': ('5d', 'Última Semana'),
        '2': ('1mo', 'Último Mês'),
        '3': ('6mo', 'Últimos 6 Meses'),
        '4': ('1y', 'Último Ano')
    }

    while True:
        print("\n" + "="*40)
        print("Selecione o Periodo de análise:")
        for k,v in opcoes.items():
            print(f"{k} - {v[1]}")
        print("="*40)
        
        escolha = input("Digite o número da opção: ").strip()

        if escolha in opcoes:
            return opcoes[escolha][0], opcoes[escolha][1]
        else:
            print("\n Opção Inválida! Digite apenas 1, 2, 3 ou 4.")
            time.sleep(2)

# Função de coleta de dados financeiros
def coletar_dados_financeiros(ticker, periodo):
    try:
        acao = yf.Ticker(ticker)
        info = acao.info
        market_cap = info.get('marketCap', 0)
        
        historico = acao.history(period=periodo)
        return market_cap, historico
    
    except Exception as e:
        print(f' -> Erro no Yahoo Finance para {ticker}: {e}')
        # Retorna valores vazios seguros para não quebrar o código
        return 0, None
    
# Função de gráficos personalizados
def gerar_dashboards_automaticos(dados_grafico, periodo_nome):
    if not dados_grafico:
        print("Sem dados Suficientes para gerar gráficos")
        return
    
    print("\nGerando gráfico interativos...")
    time.sleep(1)

    nomes = [d['nome'] for d in dados_grafico]
    valores = [d['market_cap'] / 1e9 for d in dados_grafico]
    
    # Cria a estrutura de gráficos (um em cima do outro)
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Valor de Mercado Atual (Bilhões R$)", f"Evolução das ações - {periodo_nome}")
    )
    
    # Gráfico 1: Barras
    fig.add_trace(
        go.Bar(
            x=nomes,
            y=valores,
            text=[f'{v:.1f}B' for v in valores],
            textposition='auto',
            marker_color='royalblue',
            name="Valor de Mercado",
            hovertemplate='%{x}<br>R$ %{y:.2f} Bilhões<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Gráfico 2: Linhas
    for item in dados_grafico:
        hist = item['historico']
        if hist is not None and not hist.empty:
            preco_ini = hist['Close'].iloc[0]
            variacao = ((hist['Close'] - preco_ini) / preco_ini) * 100
            
            fig.add_trace(
                go.Scatter(
                    x=hist.index,
                    y=variacao,
                    mode='lines',
                    name=item['nome'],
                    hovertemplate='<b>%{x|%d/%m}</b>: %{y:.2f}%<extra></extra>'
                ),
                row=2, col=1
            )
            
    fig.update_layout(height=800, template='plotly_white')
    fig.show()

# Inicio do código.
print("\n>>> Iniciando o sistema <<< ")
time.sleep(1)

#Retorno da escolha do usuário
periodo_escolhido, nome_periodo = solicitar_periodo_usuario()
print(f"\nPeríodo selecionado para análise: {nome_periodo}")

dados_para_visualizacao = []

#Conectando dados do Dicionário a ferramenta SQlite
with sqlite3.connect(nome_Banco_Empresas) as conexao:
    cursor = conexao.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empresas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnpj TEXT UNIQUE,
            razao_social TEXT,
            nome_fantasia TEXT,
            ticker TEXT
        )                              
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER,
            data_coleta DATETIME,
            valor_acao REAL,
            valor_mercado_bi REAL,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        )                              
    ''')
    #Realizando limpeza no arquivo .db
    cursor.execute('DELETE FROM financas')
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='financas'")

    cursor.execute('DELETE FROM empresas')
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='empresas'")

    conexao.commit()
    print("\n-> Banco de dados criado e limpo para análise.")


    # Coleta Geral de dados
    for cnpj, ticker in empresas_ticker.items():
        print(f"\n--- processando {ticker} ---")
        
        tentativas_contador = 0
        max_tentativas = 3
        sucesso_api = False
        dados_receita = None

        #Puxa a informação da empresa por API
        while tentativas_contador < max_tentativas:
            try:
                url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
                resp = requests.get(url)
                
                if resp.status_code == 200:
                    dados_receita = resp.json()
                    sucesso_api = True
                    print(f"  -> API receita: OK")
                    break
                
                elif resp.status_code == 429:
                    tentativas_contador += 1
                    tempo = 15 * tentativas_contador
                    print(f"  -> Erro 429: Bloqueio temporário. Tentativa {tentativas_contador}/{max_tentativas}. Esperando {tempo}s...")
                    if tentativas_contador == max_tentativas:
                        print(f'\nNúmero de tentativas excedido, passando para a próxima empresa em {tempo} segundos...')
                        time.sleep(tempo)
                        break
                    time.sleep(tempo)
                    
                elif resp.status_code == 404:
                    print(f" -> Erro 404: CNPJ não existe.")
                    break

                else:
                    print(f"  -> Erro desconhecido: {resp.status_code}")
                    break

            except Exception as e:
                print(f" -> Erro de conexão {e}")
                tentativas_contador += 1
                time.sleep(2)

        # Verifica se existe informação, caso tenha guarda no arquivo .db
        if sucesso_api and dados_receita:
            nome_final = dados_receita.get('nome_fantasia') or dados_receita['razao_social']
            
            cursor.execute('''
                INSERT INTO empresas (cnpj, razao_social, nome_fantasia, ticker)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(cnpj) DO UPDATE SET ticker=excluded.ticker        
            ''',(cnpj, dados_receita['razao_social'], nome_final, ticker))
            
            cursor.execute('SELECT id from empresas WHERE cnpj = ?', (cnpj,))
            empresa_id = cursor.fetchone()[0]
            
            # Busca Dados Financeiros
            mkt_cap, historico = coletar_dados_financeiros(ticker, periodo_escolhido)
           
            if mkt_cap > 0:
               preco_atual = historico['Close'].iloc[-1]
               mkt_cap_bi = mkt_cap / 1e9
               
               data_real_bolsa = historico.index[-1]
               data_formatada = str(data_real_bolsa) 
               
               # Salva Finanças em outra tabela
               cursor.execute('''
                    INSERT INTO financas (empresa_id, valor_acao, valor_mercado_bi, data_coleta)
                    VALUES(?, ?, ?, ?)
               ''', (empresa_id, float(preco_atual), float(mkt_cap_bi), data_formatada))
               
               print(f"  -> Financeiro: R${preco_atual:.2f} | Mkt cap: {mkt_cap_bi:.2f}B")
               
               dados_para_visualizacao.append({
                   'nome': ticker,
                   'market_cap': mkt_cap,
                   'historico': historico
               })
               conexao.commit()
            else:
               print(" -> Falha nos dados Financeiros.")
        else:
            print(f'  -> Falha ao processar {ticker}.')
        
        time.sleep(1) # Pausa leve entre empresas


print("\n" + "="*45)
print("Coleta finalizada! Abrindo visualização...")
gerar_dashboards_automaticos(dados_para_visualizacao, nome_periodo)
