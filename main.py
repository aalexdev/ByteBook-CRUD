import pyodbc
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

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
        conexao = pyodbc.connect(connection_string)
        return conexao
    except pyodbc.Error as e:
        print(f"Erro ao conectar com o banco de dados: {e}")
        return None

class AutorModel(BaseModel):
    id_autor: int
    nome: str
    dt_nasc: str

class LivroModel(BaseModel):
    id_livro: int
    nome: str
    quantidade: int
    dt_lancamento: str
    id_autor_fk: int

class ClienteModel(BaseModel):
    id_cliente: int
    nome: str
    endereco: str

class EmprestimoModel(BaseModel):
    id_emprestimo: int
    id_livro_fk: int
    id_cliente_fk: int
    dt_emprestimo: str

@app.get("/")
def testar_conexao():
    conn = get_conexao()
    if conn:
        conn.close()
        return {"mensagem": "Conexão com o banco realizada com sucesso!"}
    else:
        return {"mensagem": "Erro ao conectar com o banco de dados."}

@app.post("/autores")
async def criar_autor(autor: AutorModel):
    conn = get_conexao()
    cursor = conn.cursor()
    comando = "INSERT INTO autor (id_autor_pk, nome, dt_nasc) VALUES (?, ?, ?)"
    cursor.execute(comando, (autor.id_autor, autor.nome, autor.dt_nasc))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "Autor criado com sucesso", "dados": autor}

@app.get("/autores/{id_autor}")
async def ver_autor(id_autor: int):
    conn = get_conexao()
    cursor = conn.cursor()
    comando = "SELECT id_autor_pk, nome, dt_nasc FROM autor WHERE id_autor_pk = ?"
    cursor.execute(comando, (id_autor,))
    linha = cursor.fetchone()
    cursor.close()
    conn.close()
    return {"id_autor": linha[0], "nome": linha[1], "dt_nasc": str(linha[2])}

@app.post("/livros")
async def criar_livro(livro: LivroModel):
    conn = get_conexao()
    cursor = conn.cursor()
    comando = "INSERT INTO Livro (id_livro, dt_lancamento, quantidade, id_autor_fk, nome) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(comando, (livro.id_livro, livro.dt_lancamento, livro.quantidade, livro.id_autor_fk, livro.nome))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "Livro cadastrado com sucesso", "dados": livro}

@app.get("/livros")
async def listar_livros():
    conn = get_conexao()
    cursor = conn.cursor()
    comando = "SELECT id_livro, nome, quantidade FROM Livro"
    cursor.execute(comando)
    linhas = cursor.fetchall()
    resultado = []
    for linha in linhas:
        resultado.append({"id_livro": linha[0], "nome": linha[1], "quantidade": linha[2]})
    cursor.close()
    conn.close()
    return resultado

@app.post("/clientes")
async def criar_cliente(cliente: ClienteModel):
    conn = get_conexao()
    cursor = conn.cursor()
    comando = "INSERT INTO cliente (id_cliente_pk, nome, endereco) VALUES (?, ?, ?)"
    cursor.execute(comando, (cliente.id_cliente, cliente.nome, cliente.endereco))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "Cliente cadastrado com sucesso", "dados": cliente}

@app.post("/emprestimos")
async def novo_emprestimo(emprestimo: EmprestimoModel):
    conn = get_conexao()
    cursor = conn.cursor()
    comando = "INSERT INTO emprestimo (id_emprestimo_pk, id_livro_fk, id_cliente_fk, dt_emprestimo) VALUES (?, ?, ?, ?)"
    cursor.execute(comando, (emprestimo.id_emprestimo, emprestimo.id_livro_fk, emprestimo.id_cliente_fk, emprestimo.dt_emprestimo))
    conn.commit()
    cursor.close()
    conn.close()
    return {"mensagem": "Empréstimo registrado com sucesso", "dados": emprestimo}

@app.delete("/emprestimos/{id_emprestimo}")
async def encerrar_emprestimo(id_emprestimo: int):
    conn = get_conexao()
    cursor = conn.cursor()
    comando = "DELETE FROM emprestimo WHERE id_emprestimo_pk = ?"
    cursor.execute(comando, (id_emprestimo,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": f"Empréstimo {id_emprestimo} finalizado"}

