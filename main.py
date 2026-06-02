# ByteBook — main.py  (FastAPI + pyodbc + SQL Server)

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import date
import pyodbc, os

app = FastAPI(title="ByteBook")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Conexão
def db():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER','localhost')};"
        f"DATABASE={os.getenv('DB_DATABASE','ByteBook')};"
        f"UID={os.getenv('DB_USERNAME','sa')};"
        f"PWD={os.getenv('DB_PASSWORD','SuaSenhaAqui')};"
        "TrustServerCertificate=yes;"
    )

def rows(cursor):
    cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, r)) for r in cursor.fetchall()]

# Schemas
class Livro(BaseModel):
    titulo: str; autor: str
    isbn: Optional[str] = None; genero: Optional[str] = None
    ano: Optional[int] = None;  quantidade: int = 1

class Cliente(BaseModel):
    nome: str; email: str
    telefone: Optional[str] = None; cpf: Optional[str] = None

class Emprestimo(BaseModel):
    livro_id: int; cliente_id: int; data_emprestimo: date
    data_devolucao: Optional[date] = None

class Devolucao(BaseModel):
    data_devolucao: date = date.today()

# Setup DB
@app.post("/api/setup")
def setup():
    stmts = [
        """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='livros' AND xtype='U')
           CREATE TABLE livros (id INT IDENTITY PRIMARY KEY, titulo NVARCHAR(200) NOT NULL,
           autor NVARCHAR(150) NOT NULL, isbn NVARCHAR(20) UNIQUE, genero NVARCHAR(80),
           ano INT, quantidade INT DEFAULT 1, criado_em DATETIME DEFAULT GETDATE())""",
        """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='clientes' AND xtype='U')
           CREATE TABLE clientes (id INT IDENTITY PRIMARY KEY, nome NVARCHAR(150) NOT NULL,
           email NVARCHAR(150) UNIQUE NOT NULL, telefone NVARCHAR(20),
           cpf NVARCHAR(14) UNIQUE, criado_em DATETIME DEFAULT GETDATE())""",
        """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='emprestimos' AND xtype='U')
           CREATE TABLE emprestimos (id INT IDENTITY PRIMARY KEY,
           livro_id INT NOT NULL REFERENCES livros(id),
           cliente_id INT NOT NULL REFERENCES clientes(id),
           data_emprestimo DATE DEFAULT CAST(GETDATE() AS DATE),
           data_devolucao DATE, devolvido BIT DEFAULT 0,
           criado_em DATETIME DEFAULT GETDATE())""",
    ]
    conn = db(); cur = conn.cursor()
    for s in stmts: cur.execute(s)
    conn.commit(); conn.close()
    return {"message": "Tabelas criadas com sucesso!"}

# Livros
@app.get("/api/livros")
def listar_livros(q: str = Query("")):
    conn = db(); cur = conn.cursor()
    if q:
        cur.execute("SELECT * FROM livros WHERE titulo LIKE ? OR autor LIKE ? ORDER BY titulo", f"%{q}%", f"%{q}%")
    else:
        cur.execute("SELECT * FROM livros ORDER BY titulo")
    result = rows(cur); conn.close(); return result

@app.post("/api/livros", status_code=201)
def criar_livro(l: Livro):
    conn = db(); cur = conn.cursor()
    cur.execute("INSERT INTO livros (titulo,autor,isbn,genero,ano,quantidade) VALUES (?,?,?,?,?,?)",
                l.titulo, l.autor, l.isbn, l.genero, l.ano, l.quantidade)
    conn.commit()
    cur.execute("SELECT * FROM livros WHERE id=SCOPE_IDENTITY()")
    result = rows(cur)[0]; conn.close(); return result

@app.put("/api/livros/{id}")
def atualizar_livro(id: int, l: Livro):
    conn = db(); cur = conn.cursor()
    cur.execute("UPDATE livros SET titulo=?,autor=?,isbn=?,genero=?,ano=?,quantidade=? WHERE id=?",
                l.titulo, l.autor, l.isbn, l.genero, l.ano, l.quantidade, id)
    if not cur.rowcount: raise HTTPException(404, "Livro não encontrado")
    conn.commit()
    cur.execute("SELECT * FROM livros WHERE id=?", id)
    result = rows(cur)[0]; conn.close(); return result

@app.delete("/api/livros/{id}")
def deletar_livro(id: int):
    conn = db(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM emprestimos WHERE livro_id=? AND devolvido=0", id)
    if cur.fetchone()[0]: raise HTTPException(409, "Livro com empréstimos ativos")
    cur.execute("DELETE FROM livros WHERE id=?", id)
    if not cur.rowcount: raise HTTPException(404, "Livro não encontrado")
    conn.commit(); conn.close(); return {"message": "Livro removido"}

# Clientes
@app.get("/api/clientes")
def listar_clientes(q: str = Query("")):
    conn = db(); cur = conn.cursor()
    if q:
        cur.execute("SELECT * FROM clientes WHERE nome LIKE ? OR email LIKE ? ORDER BY nome", f"%{q}%", f"%{q}%")
    else:
        cur.execute("SELECT * FROM clientes ORDER BY nome")
    result = rows(cur); conn.close(); return result

@app.post("/api/clientes", status_code=201)
def criar_cliente(c: Cliente):
    conn = db(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome,email,telefone,cpf) VALUES (?,?,?,?)",
                c.nome, c.email, c.telefone, c.cpf)
    conn.commit()
    cur.execute("SELECT * FROM clientes WHERE id=SCOPE_IDENTITY()")
    result = rows(cur)[0]; conn.close(); return result

@app.put("/api/clientes/{id}")
def atualizar_cliente(id: int, c: Cliente):
    conn = db(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET nome=?,email=?,telefone=?,cpf=? WHERE id=?",
                c.nome, c.email, c.telefone, c.cpf, id)
    if not cur.rowcount: raise HTTPException(404, "Cliente não encontrado")
    conn.commit()
    cur.execute("SELECT * FROM clientes WHERE id=?", id)
    result = rows(cur)[0]; conn.close(); return result

@app.delete("/api/clientes/{id}")
def deletar_cliente(id: int):
    conn = db(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM emprestimos WHERE cliente_id=? AND devolvido=0", id)
    if cur.fetchone()[0]: raise HTTPException(409, "Cliente com empréstimos ativos")
    cur.execute("DELETE FROM clientes WHERE id=?", id)
    if not cur.rowcount: raise HTTPException(404, "Cliente não encontrado")
    conn.commit(); conn.close(); return {"message": "Cliente removido"}

# Empréstimos 
@app.get("/api/emprestimos")
def listar_emprestimos(status: str = "todos"):
    conn = db(); cur = conn.cursor()
    q = """SELECT e.id, e.data_emprestimo, e.data_devolucao, e.devolvido,
                  l.id livro_id, l.titulo livro_titulo,
                  c.id cliente_id, c.nome cliente_nome
           FROM emprestimos e JOIN livros l ON e.livro_id=l.id JOIN clientes c ON e.cliente_id=c.id"""
    if status == "ativos":     cur.execute(q + " WHERE e.devolvido=0 ORDER BY e.data_emprestimo DESC")
    elif status == "devolvidos": cur.execute(q + " WHERE e.devolvido=1 ORDER BY e.data_devolucao DESC")
    else:                       cur.execute(q + " ORDER BY e.id DESC")
    result = rows(cur); conn.close(); return result

@app.post("/api/emprestimos", status_code=201)
def criar_emprestimo(e: Emprestimo):
    conn = db(); cur = conn.cursor()
    cur.execute("SELECT quantidade FROM livros WHERE id=?", e.livro_id)
    livro = cur.fetchone()
    if not livro: raise HTTPException(404, "Livro não encontrado")
    cur.execute("SELECT COUNT(*) FROM emprestimos WHERE livro_id=? AND devolvido=0", e.livro_id)
    if cur.fetchone()[0] >= livro[0]: raise HTTPException(409, "Sem exemplares disponíveis")
    cur.execute("INSERT INTO emprestimos (livro_id,cliente_id,data_emprestimo,data_devolucao) VALUES (?,?,?,?)",
                e.livro_id, e.cliente_id, e.data_emprestimo, e.data_devolucao)
    conn.commit()
    cur.execute("SELECT id FROM emprestimos WHERE id=SCOPE_IDENTITY()")
    new_id = cur.fetchone()[0]; conn.close()
    return {"message": "Empréstimo registrado", "id": new_id}

@app.patch("/api/emprestimos/{id}/devolver")
def devolver(id: int, d: Devolucao = Devolucao()):
    conn = db(); cur = conn.cursor()
    cur.execute("UPDATE emprestimos SET devolvido=1, data_devolucao=? WHERE id=? AND devolvido=0",
                d.data_devolucao, id)
    if not cur.rowcount: raise HTTPException(404, "Empréstimo não encontrado ou já devolvido")
    conn.commit(); conn.close(); return {"message": "Devolução registrada"}

@app.delete("/api/emprestimos/{id}")
def deletar_emprestimo(id: int):
    conn = db(); cur = conn.cursor()
    cur.execute("DELETE FROM emprestimos WHERE id=?", id)
    if not cur.rowcount: raise HTTPException(404, "Empréstimo não encontrado")
    conn.commit(); conn.close(); return {"message": "Empréstimo removido"}

# Dashboard
@app.get("/api/dashboard")
def dashboard():
    conn = db(); cur = conn.cursor()
    def count(q): cur.execute(q); return cur.fetchone()[0]
    cur.execute("SELECT TOP 5 l.titulo, COUNT(*) n FROM emprestimos e JOIN livros l ON e.livro_id=l.id GROUP BY l.titulo ORDER BY n DESC")
    populares = [{"titulo": r[0], "total": r[1]} for r in cur.fetchall()]
    result = {
        "total_livros":          count("SELECT COUNT(*) FROM livros"),
        "total_clientes":        count("SELECT COUNT(*) FROM clientes"),
        "emprestimos_ativos":    count("SELECT COUNT(*) FROM emprestimos WHERE devolvido=0"),
        "emprestimos_devolvidos":count("SELECT COUNT(*) FROM emprestimos WHERE devolvido=1"),
        "livros_populares": populares,
    }
    conn.close(); return result

# Run 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
