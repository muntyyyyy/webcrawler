import requests
import re
import mysql.connector

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CrawlRequest(BaseModel):
    url: str
    palavra: str

def conecta_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="crawler_db"
    )

def init_db():
    db = conecta_db()
    cursor = db.cursor()

    #tabela links
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Links (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(500) UNIQUE NOT NULL
        )
    """)

    #tabela palavras
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Palavras (
            id INT AUTO_INCREMENT PRIMARY KEY,
            palavra VARCHAR(255) NOT NULL,
            link_id INT,
            FOREIGN KEY(link_id) REFERENCES Links(id) ON DELETE CASCADE
        )
    """)

    #tabela profundidade
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Profundidade(
            id INT AUTO_INCREMENT PRIMARY KEY,
            nivel INT DEFAULT 0,
            palavra_id INT,
            link_id INT,
            FOREIGN KEY(palavra_id) REFERENCES Palavras(id) ON DELETE CASCADE,
            FOREIGN KEY(link_id) REFERENCES Links(id) ON DELETE CASCADE
        )
    """)

    #tabela logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Logs(
            id INT AUTO_INCREMENT PRIMARY KEY,
            data_execucao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            palavra_id INT,
            url_encontrada VARCHAR(500),
            contagem INT,
            FOREIGN KEY(palavra_id) REFERENCES Palavras(id) ON DELETE CASCADE
        )
    """)


def executar_crawl(request: CrawlRequest):
    try:
        #obter html do site
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(request.url, headers=headers, timeout=10)
        html = response.text

        #extrair titulo com regex
        match_titulo = re.search(r'<title>(.*?)</title>', html, re.I | re.S)
        titulo = match_titulo.group(1).strip() if match_titulo else "sem titulo"

        #limpar tags html para contar a palavra no texto visivel
        texto_limpo = re.sub(r'<[^>]*>', ' ', html)

        #contar palavra com regex
        padrao = re.compile(re.escape(request.palavra), re.I)
        ocorrencias = len(padrao.findall(texto_limpo))
        







