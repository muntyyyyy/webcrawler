import requests
import re
import mysql.connector
import time
from urllib.parse import urljoin, urlparse
from datetime import datetime

def conecta_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="crawler_db"
    )

def guarda_log(palavra, link, contagem, pedido_id):
    db = conecta_db()
    cursor = db.cursor()
    try:
        query = """
            INSERT INTO Logs (palavra, link, contagem, pedido_id) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (palavra, link, contagem, pedido_id))
        db.commit()
    except Exception as e:
        print(f"Erro ao salvar log: {e}")
    finally:
        cursor.close()
        db.close()

def analisa_pagina(url, palavra, profundidadeAtual, profundidadeMax, visitados, pedido_id):
    if profundidadeAtual > profundidadeMax or url in visitados:
        return
    
    visitados.add(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/'
    }
    print(f"profundidade: {profundidadeAtual}  a explorar: {url}")

    try:
        resposta = requests.get(url, headers=headers, timeout=10)

        if resposta.status_code == 403:
            print(f"Bloqueio 403 em {url}. O site detectou o crawler.")
            return

        if resposta.status_code != 200:
            print(f"Erro ao acessar {url}: Status {resposta.status_code}")
            return
        
        conteudo = resposta.text

        texto_sem_scripts = re.sub(r'<(script|style).*?>.*?</\1>', '', conteudo, flags=re.DOTALL | re.IGNORECASE)
        # textoLimpo = re.sub(r'<[^>]*>', ' ', texto_sem_scripts)
        textoLimpo = re.sub(r'</?[a-zA-Z][^>]*>', ' ', texto_sem_scripts)

        ocorrencias = re.findall(re.escape(palavra), textoLimpo, re.IGNORECASE)
        contagem = len(ocorrencias)

        if contagem > 0:
            print(f"Encontrado '{palavra}' {contagem} vezes em {url}")
            guarda_log(palavra, url, contagem, pedido_id)
        
        if profundidadeAtual < profundidadeMax:
            links = re.findall(r'href=["\'](https?://.*?|/.*?)["\']', conteudo, re.IGNORECASE)

            for link in links:
                novo_url = urljoin(url, link)
                
                if urlparse(novo_url).scheme in ['http', 'https']:
                    analisa_pagina(novo_url, palavra, profundidadeAtual + 1, profundidadeMax, visitados, pedido_id)
    except Exception as e:
        print(f"Erro ao processar {url}: {e}")

def processa_pedidos():
    db = conecta_db()
    cursor = db.cursor()

    agora = datetime.now()
    data_atual = agora.date()
    hora_atual = agora.time()

    query = ("""SELECT id, link, palavra, profundidade FROM CrawlRequests WHERE status = 'pendente'
                AND (data_execucao < %s OR (data_execucao = %s AND hora_execucao <= %s))
            """)
    
    cursor.execute(query, (data_atual, data_atual, hora_atual))

    pedidos = cursor.fetchall()

    for pedido in pedidos:

        p_id, url_inicial, palavra, profundidadeMax = pedido

        cursor.execute("UPDATE CrawlRequests SET status = 'inMediaRes' WHERE id = %s", (p_id,))
        db.commit()

        print(f"A processar pedido {p_id}: {palavra} em {url_inicial}" )
        analisa_pagina(url_inicial, palavra, 0, profundidadeMax, set(), p_id)

        cursor.execute("UPDATE CrawlRequests SET status = 'concluido' WHERE id = %s", (p_id,))
        db.commit()
        print(f"Pedido {p_id} concluído.")
    
    cursor.close()
    db.close()

if __name__ == "__main__":
    print("Crawler ativo. A verificar pedidos a cada 5 segundos.")
    while True:
        print("Verificando pedidos pendentes...")
        processa_pedidos()
        time.sleep(5)