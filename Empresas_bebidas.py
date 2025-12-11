import sqlite3 
import requests
import time

empresas_de_bebidas_cnpjs =[
    '07526557000100', # AMBEV S.A 
    '61153169000176', # AZUMA KIRIN
    '46842894000168', # CASA DI CONTI LTDA.
    '71947592000444', # Cervejaria Ashby 
    '08875424000101', # Cervejaria Saint Bier
    '16940827000115', # CEREALISTA AURORA
    '07301954000183', # BAMBERG
    '04475763000140', # B.B.L.
    '07633384000129',  # BEBA BRASIL
    '45997418000153' #Coca Cola Industrias Ltda (Matriz)
]

print('-=-'*5,"Programa verificador de situação cadastral de empresas",'-=-'*5)

with sqlite3.connect('empresas_de_bebidas_no_brasil.db') as conexao:
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnpj TEXT UNIQUE,
            razao_social TEXT,
            nome_fantasia TEXT,
            situacao_cadastral TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enderecos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER,
            logradouro TEXT,
            numero TEXT,
            bairro TEXT,
            municipio TEXT,
            uf TEXT,
            cep TEXT,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id),
            UNIQUE(empresa_id)
        )
    ''')

    for cnpj in empresas_de_bebidas_cnpjs:
        print(f"Realizando a consulta: {cnpj}...", end = " ", flush=True)

        tentativas = 0

        while True:
            try:
                url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
                response = requests.get(url)

                if response.status_code == 200:
                    dados = response.json()


                    cursor.execute('''
                        INSERT INTO empresas (cnpj, razao_social, nome_fantasia, situacao_cadastral)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT (cnpj) DO UPDATE SET
                            razao_social = excluded.razao_social,
                            nome_fantasia = excluded.nome_fantasia,
                            situacao_cadastral = excluded.situacao_cadastral

                    ''', (
                        dados['cnpj'],
                        dados['razao_social'],
                        dados.get('nome_fantasia', 'não informado'),
                        dados['descricao_situacao_cadastral']
                    ))
                    cursor.execute('SELECT id FROM empresas WHERE cnpj = ?',(dados['cnpj'],))
                    empresa_id = cursor.fetchone()[0]

                    cursor.execute('DELETE FROM enderecos WHERE empresa_id = ?', (empresa_id,))
                    cursor.execute('''
                        INSERT INTO enderecos (empresa_id, logradouro, numero, bairro, municipio, uf, cep)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''',(
                        empresa_id,
                        dados['logradouro'],
                        dados['numero'],
                        dados['bairro'],
                        dados['municipio'],
                        dados['uf'],
                        dados['cep']
                    ))
                    print("Informação atualizada!!")
                    conexao.commit()
                    break
                elif response.status_code == 429:
                    tentativas += 1
                    if tentativas == 4:
                        print(f"Pulando CNPJ {cnpj} foi feito três tentativas")
                        break
                    print(f"\n Erro 429 (Muitos pedidos feitos ao servidor). Esperando vinte segundos para tentar {cnpj} de novo...")
                    time.sleep(20)
                    print(f"Tentando o {cnpj} novamente...", end= " ")
                elif response.status_code == 404:
                    print(f"Erro CNPJ {cnpj} não encontrado pela API!!")
                    break
                else:
                    print(f"Erro desconhecido: {response.status_code}")
                    break
            except Exception as falha:
                print(f"Erro Crítico: {falha}")
                break
        
        time.sleep(5)
print("\n Fim do processo!!\n Favor verificar o arquivo .db criaddo!!")


