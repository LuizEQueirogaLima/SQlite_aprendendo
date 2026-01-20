import sqlite3
import requests
import time
import yfinance as yf
import matplotlib.pyplot as plt
#import pandas as pd



empresas_ticker = {
    '02474103000119': 'EGIE3.SA',   # Engie Brasil
    '03220438000173': 'EQTL3.SA',   # Equatorial
    '02429144000193': 'CPFE3.SA',   # CPFL
    '17155730000164': 'CMIG4.SA',   # CEMIG
    '00864214000106': 'ENGI11.SA',  # Energisa
    '07859971000130': 'TAEE11.SA',  # TAESA
    '01083200000118': 'NEOE3.SA'    # Neoenergia
}

Nome_Banco_Empresas = 'setor_eletrico.db'

def coletar_dados_financeiros(ticker):
    try:
        acao = yf.Ticker(ticker)
        info = acao.info
        market_cap = info.get('marketCap', 0)

        historico = acao.history(period="1mo")

        return market_cap, historico
    except Exception as e:
        print(f" -> Erro no Yahoo Finance para {ticker}: {e}")
        return 0, None

def gerar_dashboards_automaticos(dados_grafico): 
    if not dados_grafico:
        print("Sem dados suficientes para gerar gráficos")
        return
    print("\nGerando gráficos automáticos...")

    nomes = [d['nome']for d in dados_grafico]
    valores = [d['market_cap'] / 1e9 for d in dados_grafico]

    plt.figure(figsize = (12,7))
    barras = plt.bar(nomes, valores, color="#436FE9")
    plt.title('Valor de Mercado Atual (bilhões R$)', fontsize=18)
    plt.ylabel('Bilhões (R$)')
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    for barra in barras:
        altura= barra.get_height()
        plt.text(barra.get_x() +barra.get_width()/2.,altura,
                  f'{altura:.1f}B', ha='center', va='bottom')
    plt.show()

    plt.figure(figsize=(12,7))
    tem_historico = False
    for item in dados_grafico:
        hist = item['historico']
        if hist is not None and not hist.empty:
            preco_ini = hist['Close'].iloc[0]
            variacao = ((hist['Close']- preco_ini) / preco_ini) * 100
            plt.plot(hist.index, variacao, label=item['nome'])
            tem_historico = True
    if tem_historico:
        plt.title('Variação das Ações do Último Mês (%)', fontsize = 14)
        plt.ylabel('Variação Acumulada (%)')
        plt.xlabel('Data')
        plt.legend()
        plt.grid(True)
        plt.show()

print( ">>> Iniciando o Sistema <<<", end= " ", flush = True)
time.sleep(2)

dados_para_visualizacao = []


with sqlite3.connect(Nome_Banco_Empresas) as conexao:
    cursor = conexao.cursor()


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
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
            data_coleta DATETIME DEFAULT CURRENT_TIMESTAMP,
            valor_acao REAL,
            valor_mercado_bi REAL,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        )
    ''')


    for cnpj, ticker in empresas_ticker.items():
        print(f"\n--- processando {ticker} ---")

        tentativas_contador = 0
        max_tentativas = 3
        sucesso_api = False
        dados_receita = None

        while tentativas_contador < max_tentativas:
            try:
                url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
                resp = requests.get(url)

                if resp.status_code == 200:
                    dados_receita = resp.json()
                    sucesso_api = True
                    print(f"  -> API receita: OK (tentativa {tentativas_contador+1})")
                    break

                elif resp.status_code == 429:
                    tentativas_contador += 1
                    tempo = 15 * tentativas_contador
                    print(f"  -> Erro 429: Bloqueio temporário. Tentativa {tentativas_contador}/{max_tentativas}. Esperando {tempo}s...")
                    time.sleep(tempo)

                elif resp.status_code == 404:
                    print(f"  -> Erro 404: CNPJ não existe.")
                    break
                else:
                    print(f"  -> Erro desconhecido: {resp.status_code}")
                    break
            except Exception as e:
                print(f"  -> Erro de conexão: {e}")
                tentativas_contador += 1
                time.sleep(5)
            
        if sucesso_api and dados_receita:
            nome_final = dados_receita.get('nome_fantasia') or dados_receita['razao_social']

            cursor.execute('''
                INSERT INTO empresas (cnpj, razao_social, nome_fantasia, ticker)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(cnpj) DO UPDATE SET ticker=excluded.ticker
            ''', (cnpj, dados_receita['razao_social'], nome_final, ticker))

            cursor.execute('SELECT id FROM empresas WHERE cnpj = ?', (cnpj,))
            empresa_id = cursor.fetchone()[0]

            mkt_cap, historico = coletar_dados_financeiros(ticker)

            if mkt_cap > 0:
                preco_atual = historico['Close'].iloc[-1]
                mkt_cap_bi = mkt_cap  / 1e9


                cursor.execute('''
                    INSERT INTO financas (empresa_id, valor_acao, valor_mercado_bi)
                    VALUES(?, ?, ?)

                ''', (empresa_id, float(preco_atual), float(mkt_cap_bi)))

                print(f"  -> Financeiro: R${preco_atual:.2f} | Mkt Cap: {mkt_cap_bi:.2f}")

                dados_para_visualizacao.append({
                    'nome': ticker,
                    'market_cap': mkt_cap,
                    'historico': historico
                })
                conexao.commit()
            else:
                print(" -> Falha nos dados financeiros.")
        else:
            print(f" -> Falha ao processar {ticker} após todas as tentativas.")
        time.sleep(2)

print("\n" + "="*50)
print("Coleta finalizada! Abrindo visualização...")
gerar_dashboards_automaticos(dados_para_visualizacao)