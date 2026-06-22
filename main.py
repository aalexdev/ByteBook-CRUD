# ByteBook — main.py (FastAPI + pyodbc + SQL Server)
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import pyodbc
import uvicorn

app = FastAPI(title="ByteBook")

# Habilita o CORS para conectar com o seu frontend sem restrições
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# ── Conexão com o SQLEXPRESS Local ───────────────────────────
def db():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=ByteBook;"
        "Trusted_Connection=yes;"
    )

# ── Schemas ──────────────────────────────────────────────────
class Livro(BaseModel):
    titulo: str
    autor: str
    isbn: Optional[str] = None
    genero: Optional[str] = None
    ano: Optional[int] = None
    quantidade: int = 1

class Cliente(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    cpf: Optional[str] = None

class Emprestimo(BaseModel):
    livro_id: int
    cliente_id: int
    data_emprestimo: str
    data_devolucao: Optional[str] = None

# ── Livros ───────────────────────────────────────────────────
@app.get("/api/livros")
def listar_livros():
    conn = db(); cur = conn.cursor()
    cur.execute("SELECT id, titulo, autor, isbn, genero, ano, quantidade FROM livros")
    res = [{"id": r[0], "titulo": r[1], "autor": r[2], "isbn": r[3], "genero": r[4], "ano": r[5], "quantidade": r[6]} for r in cur.fetchall()]
    conn.close(); return res

@app.post("/api/livros", status_code=201)
def cadastrar_livro(l: Livro):
    conn = db(); cur = conn.cursor()
    cur.execute("INSERT INTO livros (titulo, autor, isbn, genero, ano, quantidade) VALUES (?,?,?,?,?,?)",
                l.titulo, l.autor, l.isbn, l.genero, l.ano, l.quantidade)
    conn.commit(); conn.close(); return {"message": "Livro cadastrado"}

@app.delete("/api/livros/{id}")
def deletar_livro(id: int):
    conn = db(); cur = conn.cursor()
    cur.execute("DELETE FROM livros WHERE id=?", id)
    if not cur.rowcount: raise HTTPException(404, "Livro não encontrado")
    conn.commit(); conn.close(); return {"message": "Livro removido"}

# ── Clientes ─────────────────────────────────────────────────
@app.get("/api/clientes")
def listar_clientes():
    conn = db(); cur = conn.cursor()
    cur.execute("SELECT id, nome, email, telefone, cpf FROM clientes")
    res = [{"id": r[0], "nome": r[1], "email": r[2], "telefone": r[3], "cpf": r[4]} for r in cur.fetchall()]
    conn.close(); return res

@app.post("/api/clientes", status_code=201)
def cadastrar_cliente(c: Cliente):
    conn = db(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome, email, telefone, cpf) VALUES (?,?,?,?)", c.nome, c.email, c.telefone, c.cpf)
    conn.commit(); conn.close(); return {"message": "Cliente cadastrado"}

@app.delete("/api/clientes/{id}")
def deletar_cliente(id: int):
    conn = db(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE id=?", id)
    if not cur.rowcount: raise HTTPException(404, "Cliente não encontrado")
    conn.commit(); conn.close(); return {"message": "Cliente removido"}

# ── Empréstimos ──────────────────────────────────────────────
@app.get("/api/emprestimos")
def listar_emprestimos():
    conn = db(); cur = conn.cursor()
    cur.execute("""
        SELECT e.id, l.titulo, c.nome, e.data_emprestimo, e.data_devolucao, e.devolvido, l.id, c.id
        FROM emprestimos e 
        JOIN livros l ON e.livro_id=l.id 
        JOIN clientes c ON e.cliente_id=c.id
    """)
    res = [{
        "id": r[0], "livro_titulo": r[1], "cliente_nome": r[2],
        "data_emprestimo": str(r[3]), "data_devolucao": str(r[4]) if r[4] else None,
        "devolvido": bool(r[5]), "livro_id": r[6], "cliente_id": r[7]
    } for r in cur.fetchall()]
    conn.close(); return res

@app.post("/api/emprestimos", status_code=201)
def cadastrar_emprestimo(e: Emprestimo):
    conn = db(); cur = conn.cursor()
    cur.execute("SELECT quantidade FROM livros WHERE id=?", e.livro_id)
    livro = cur.fetchone()
    if not livro or livro[0] <= 0:
        conn.close()
        raise HTTPException(status_code=400, detail="Livro indisponível no estoque.")

    cur.execute("INSERT INTO emprestimos (livro_id, cliente_id, data_emprestimo, data_devolucao, devolvido) VALUES (?,?,?,?,0)",
                e.livro_id, e.cliente_id, e.data_emprestimo, e.data_devolucao)
    cur.execute("UPDATE livros SET quantidade = quantidade - 1 WHERE id=?", e.livro_id)
    conn.commit(); conn.close(); return {"message": "Empréstimo registrado"}

@app.post("/api/emprestimos/{id}/devolver")
def devolver_emprestimo(id: int):
    conn = db(); cur = conn.cursor()
    cur.execute("SELECT livro_id, devolvido FROM emprestimos WHERE id=?", id)
    res = cur.fetchone()
    if not res:
        conn.close()
        raise HTTPException(404, "Empréstimo não encontrado")
    if res[1] == 1:
        conn.close()
        return {"message": "Livro já devolvido"}

    cur.execute("UPDATE emprestimos SET devolvido=1 WHERE id=?", id)
    cur.execute("UPDATE livros SET quantidade = quantidade + 1 WHERE id=?", res[0])
    conn.commit(); conn.close(); return {"message": "Devolução registrada"}

@app.delete("/api/emprestimos/{id}")
def deletar_emprestimo(id: int):
    conn = db(); cur = conn.cursor()
    cur.execute("DELETE FROM emprestimos WHERE id=?", id)
    if not cur.rowcount: raise HTTPException(404, "Empréstimo não encontrado")
    conn.commit(); conn.close(); return {"message": "Empréstimo removido"}

# ── Dashboard ────────────────────────────────────────────────
@app.get("/api/dashboard")
def dashboard():
    conn = db(); cur = conn.cursor()
    def count(q): cur.execute(q); return cur.fetchone()[0]
    cur.execute("SELECT TOP 5 l.titulo, COUNT(*) n FROM emprestimos e JOIN livros l ON e.livro_id=l.id GROUP BY l.titulo ORDER BY n DESC")
    populares = [{"titulo": r[0], "total": r[1]} for r in cur.fetchall()]
    result = {
        "total_livros":           count("SELECT COUNT(*) FROM livros"),
        "total_clientes":         count("SELECT COUNT(*) FROM clientes"),
        "emprestimos_ativos":     count("SELECT COUNT(*) FROM emprestimos WHERE devolvido=0"),
        "emprestimos_devolvidos": count("SELECT COUNT(*) FROM emprestimos WHERE devolvido=1"),
        "livros_populares":       populares
    }
    conn.close(); return result

if __name__ == "__main__":
    # Alterado com sucesso para a porta padrão 8000!
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
