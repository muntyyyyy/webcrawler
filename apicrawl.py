#fazer a api de comunicação com a bd para inserir/listar/remover items da tabela
import requests
import re
import mysql.connector
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any

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
    profundidade: int
    date: Any
    time: Any

class CrawlResponse(CrawlRequest):
    id: int
    status: str

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

    #crawler requests
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CrawlRequests(
            id INT AUTO_INCREMENT PRIMARY KEY,
            data_execucao DATE,
            hora_execucao TIME,
            palavra VARCHAR(255) NOT NULL,
            link VARCHAR(500) NOT NULL,
            status ENUM('pendente','inMediaRes','concluido') DEFAULT 'pendente',
            profundidade INT DEFAULT 0
        )
    """)

    #tabela logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Logs(
            id INT AUTO_INCREMENT PRIMARY KEY,
            data_execucao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            palavra VARCHAR(255) NOT NULL,
            link VARCHAR(500) NOT NULL,
            contagem INT NOT NULL,
            pedido_id INT,
            FOREIGN KEY(pedido_id) REFERENCES CrawlRequests(id) ON DELETE CASCADE
        )
    """)

    db.commit()
    cursor.close()
    db.close()

@app.post("/crawl")
async def criar_pedido(request: CrawlRequest):
    print("recebido o pedido de crawl: ", request)
    db = conecta_db()
    cursor = db.cursor()

    try:
        query = "INSERT INTO CrawlRequests (palavra, link, profundidade, data_execucao, hora_execucao) VALUES (%s, %s, %s, %s, %s)"
        values = (request.palavra, request.url, request.profundidade, request.date, request.time)
        cursor.execute(query, values)
        db.commit()
        return {"message": "Pedido de crawl criado com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()

@app.get("/crawl")
async def listar_pedidos():
    db = conecta_db()
    cursor = db.cursor()
    try:
        query = "SELECT id, link, palavra, profundidade, status, data_execucao, hora_execucao FROM CrawlRequests"
        cursor.execute(query)
        resultados = cursor.fetchall()

        lista = []
        for row in resultados:
            lista.append({
                "id": row[0],
                "url": row[1],
                "palavra": row[2],
                "profundidade": row[3],
                "status": row[4],
                "data_execucao": str(row[5]),
                "hora_execucao": str(row[6])
            })
        return lista
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()

@app.delete("/crawl/{pedido_id}")
async def remover_pedido(pedido_id: int):
    db = conecta_db()
    cursor = db.cursor()
    try:
        query = "DELETE FROM CrawlRequests WHERE id = %s"
        cursor.execute(query, (pedido_id,))
        db.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pedido não encontrado.")
            
        return {"messagem debug": f"pedido {pedido_id} removido"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()

@app.get("/logs")
async def listar_logs():
    db = conecta_db()
    cursor = db.cursor()
    try:
        query = "SELECT id, data_execucao, palavra, link, contagem, pedido_id FROM Logs ORDER BY data_execucao DESC"
        cursor.execute(query)
        resultados = cursor.fetchall()

        logs = []
        for row in resultados:
            log_entry = {
                "id": row[0],
                "data_execucao": row[1],
                "palavra": row[2],
                "link": row[3],
                "contagem": row[4],
                "pedido_id": row[5]
            }
            logs.append(log_entry)

        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    init_db()
    print("servidor iniciado http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)