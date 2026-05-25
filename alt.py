import pyodbc
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="ByteBook API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVER   = "localhost\\SQLEXPRESS"
DATABASE = "bytebook"

def get_conexao():
    try:
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"Trusted_Connection=yes;"
        )
        return pyodbc.connect(connection_string)
    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com o banco: {e}")


# ─────────────────────────────────────────────
# MODELOS
# ─────────────────────────────────────────────

class AutorModel(BaseModel):
    id_autor: int
    nome: str
    dt_nasc: str

class AutorUpdateModel(BaseModel):
    nome: Optional[str] = None
    dt_nasc: Optional[str] = None

class LivroModel(BaseModel):
    id_livro: int
    nome: str
    quantidade: int
    dt_lancamento: str
    id_autor_fk: int

class LivroUpdateModel(BaseModel):
    nome: Optional[str] = None
    quantidade: Optional[int] = None
    dt_lancamento: Optional[str] = None
    id_autor_fk: Optional[int] = None

class ClienteModel(BaseModel):
    id_cliente: int
    nome: str
    endereco: str

class ClienteUpdateModel(BaseModel):
    nome: Optional[str] = None
    endereco: Optional[str] = None

class EmprestimoModel(BaseModel):
    id_emprestimo: int
    id_livro_fk: int
    id_cliente_fk: int
    dt_emprestimo: str


# ─────────────────────────────────────────────
# RAIZ — teste de conexão
# ─────────────────────────────────────────────

@app.get("/")
def testar_conexao():
    conn = get_conexao()
    conn.close()
    return {"mensagem": "ByteBook API online. Conexão com o banco realizada com sucesso!"}


# ─────────────────────────────────────────────
# AUTORES
# ─────────────────────────────────────────────

@app.get("/autores")
async def listar_autores():
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id_autor_pk, nome, dt_nasc FROM autor")
    linhas = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id_autor": l[0], "nome": l[1], "dt_nasc": str(l[2])} for l in linhas]


@app.get("/autores/{id_autor}")
async def ver_autor(id_autor: int):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id_autor_pk, nome, dt_nasc FROM autor WHERE id_autor_pk = ?", (id_autor,))
    linha = cursor.fetchone()
    cursor.close()
    conn.close()
    if not linha:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    return {"id_autor": linha[0], "nome": linha[1], "dt_nasc": str(linha[2])}


@app.post("/autores", status_code=201)
async def criar_autor(autor: AutorModel):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO autor (id_autor_pk, nome, dt_nasc) VALUES (?, ?, ?)",
        (autor.id_autor, autor.nome, autor.dt_nasc)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "Autor criado com sucesso", "dados": autor}


@app.put("/autores/{id_autor}")
async def atualizar_autor(id_autor: int, dados: AutorUpdateModel):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id_autor_pk FROM autor WHERE id_autor_pk = ?", (id_autor,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    if dados.nome:
        cursor.execute("UPDATE autor SET nome = ? WHERE id_autor_pk = ?", (dados.nome, id_autor))
    if dados.dt_nasc:
        cursor.execute("UPDATE autor SET dt_nasc = ? WHERE id_autor_pk = ?", (dados.dt_nasc, id_autor))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": f"Autor {id_autor} atualizado com sucesso"}


@app.delete("/autores/{id_autor}")
async def deletar_autor(id_autor: int):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id_autor_pk FROM autor WHERE id_autor_pk = ?", (id_autor,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    cursor.execute("DELETE FROM autor WHERE id_autor_pk = ?", (id_autor,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": f"Autor {id_autor} removido com sucesso"}


# ─────────────────────────────────────────────
# LIVROS
# ─────────────────────────────────────────────

@app.get("/livros")
async def listar_livros():
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id_livro, nome, quantidade, dt_lancamento, id_autor_fk FROM Livro")
    linhas = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {"id_livro": l[0], "nome": l[1], "quantidade": l[2], "dt_lancamento": str(l[3]), "id_autor_fk": l[4]}
        for l in linhas
    ]


@app.get("/livros/{id_livro}")
async def ver_livro(id_livro: int):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_livro, nome, quantidade, dt_lancamento, id_autor_fk FROM Livro WHERE id_livro = ?",
        (id_livro,)
    )
    linha = cursor.fetchone()
    cursor.close()
    conn.close()
    if not linha:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return {"id_livro": linha[0], "nome": linha[1], "quantidade": linha[2], "dt_lancamento": str(linha[3]), "id_autor_fk": linha[4]}


@app.post("/livros", status_code=201)
async def criar_livro(livro: LivroModel):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Livro (id_livro, dt_lancamento, quantidade, id_autor_fk, nome) VALUES (?, ?, ?, ?, ?)",
        (livro.id_livro, livro.dt_lancamento, livro.quantidade, livro.id_autor_fk, livro.nome)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "Livro cadastrado com sucesso", "dados": livro}


@app.put("/livros/{id_livro}")
async def atualizar_livro(id_livro: int, dados: LivroUpdateModel):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id_livro FROM Livro WHERE id_livro = ?", (id_livro,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    campos = []
    valores = []
    if dados.nome is not None:
        campos.append("nome = ?"); valores.append(dados.nome)
    if dados.quantidade is not None:
        campos.append("quantidade = ?"); valores.append(dados.quantidade)
    if dados.dt_lancamento is not None:
        campos.append("dt_lancamento = ?"); valores.append(dados.dt_lancamento)
    if dados.id_autor_fk is not None:
        campos.append("id_autor_fk = ?"); valores.append(dados.id_autor_fk)
    if campos:
        valores.append(id_livro)
        cursor.execute(f"UPDATE Livro SET {', '.join(campos)} WHERE id_livro = ?", valores)
        conn.commit()
    cursor.close()
    conn.close()
    return {"status": f"Livro {id_livro} atualizado com sucesso"}


@app.delete("/livros/{id_livro}")
async def deletar_livro(id_livro: int):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id_livro FROM Livro WHERE id_livro = ?", (id_livro,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    cursor.execute("DELETE FROM Livro WHERE id_livro = ?", (id_livro,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": f"Livro {id_livro} removido com sucesso"}


# ─────────────────────────────────────────────
# CLIENTES
# ─────────────────────────────────────────────

@app.get("/clientes")
async def listar_clientes():
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id_cliente_pk, nome, endereco FROM cliente")
    linhas = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id_cliente": l[0], "nome": l[1], "endereco": l[2]} for l in linhas]


@app.get("/clientes/{id_cliente}")
async def ver_cliente(id_cliente: int):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id_cliente_pk, nome, endereco FROM cliente WHERE id_cliente_pk = ?", (id_cliente,))
    linha = cursor.fetchone()
    cursor.close()
    conn.close()
    if not linha:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {"id_cliente": linha[0], "nome": linha[1], "endereco": linha[2]}


@app.post("/clientes", status_code=201)
async def criar_cliente(cliente: ClienteModel):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cliente (id_cliente_pk, nome, endereco) VALUES (?, ?, ?)",
        (cliente.id_cliente, cliente.nome, cliente.endereco)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "Cliente cadastrado com sucesso", "dados": cliente}


@app.put("/clientes/{id_cliente}")
async def atualizar_cliente(id_cliente: int, dados: ClienteUpdateModel):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id_cliente_pk FROM cliente WHERE id_cliente_pk = ?", (id_cliente,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    if dados.nome:
        cursor.execute("UPDATE cliente SET nome = ? WHERE id_cliente_pk = ?", (dados.nome, id_cliente))
    if dados.endereco:
        cursor.execute("UPDATE cliente SET endereco = ? WHERE id_cliente_pk = ?", (dados.endereco, id_cliente))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": f"Cliente {id_cliente} atualizado com sucesso"}


@app.delete("/clientes/{id_cliente}")
async def deletar_cliente(id_cliente: int):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id_cliente_pk FROM cliente WHERE id_cliente_pk = ?", (id_cliente,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    cursor.execute("DELETE FROM cliente WHERE id_cliente_pk = ?", (id_cliente,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": f"Cliente {id_cliente} removido com sucesso"}


# ─────────────────────────────────────────────
# EMPRÉSTIMOS
# ─────────────────────────────────────────────

@app.get("/emprestimos")
async def listar_emprestimos():
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_emprestimo_pk, id_livro_fk, id_cliente_fk, dt_emprestimo FROM emprestimo"
    )
    linhas = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {"id_emprestimo": l[0], "id_livro_fk": l[1], "id_cliente_fk": l[2], "dt_emprestimo": str(l[3])}
        for l in linhas
    ]


@app.get("/emprestimos/{id_emprestimo}")
async def ver_emprestimo(id_emprestimo: int):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_emprestimo_pk, id_livro_fk, id_cliente_fk, dt_emprestimo FROM emprestimo WHERE id_emprestimo_pk = ?",
        (id_emprestimo,)
    )
    linha = cursor.fetchone()
    cursor.close()
    conn.close()
    if not linha:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    return {"id_emprestimo": linha[0], "id_livro_fk": linha[1], "id_cliente_fk": linha[2], "dt_emprestimo": str(linha[3])}


@app.post("/emprestimos", status_code=201)
async def novo_emprestimo(emprestimo: EmprestimoModel):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO emprestimo (id_emprestimo_pk, id_livro_fk, id_cliente_fk, dt_emprestimo) VALUES (?, ?, ?, ?)",
        (emprestimo.id_emprestimo, emprestimo.id_livro_fk, emprestimo.id_cliente_fk, emprestimo.dt_emprestimo)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "Empréstimo registrado com sucesso", "dados": emprestimo}


@app.delete("/emprestimos/{id_emprestimo}")
async def encerrar_emprestimo(id_emprestimo: int):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id_emprestimo_pk FROM emprestimo WHERE id_emprestimo_pk = ?", (id_emprestimo,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    cursor.execute("DELETE FROM emprestimo WHERE id_emprestimo_pk = ?", (id_emprestimo,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": f"Empréstimo {id_emprestimo} encerrado com sucesso"}
