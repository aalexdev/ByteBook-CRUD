from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="ByteBook API")

# Configuração do CORS para permitir que o front-end (app.js) comunique com o back-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite qualquer origem local durante o desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, PUT, DELETE)
    allow_headers=["*"],
)

# ========================================================
# 📋 MODELOS DE DADOS (Pydantic)
# ========================================================

class Autor(BaseModel):
    id_autor: int
    nome: str
    idade: int
    nacionalidade: str

class Cliente(BaseModel):
    id_cliente: int
    nome: str
    cpf: str
    telefone: str
    endereco: str

class Livro(BaseModel):
    id_livro: int
    id_autor: int
    titulo: str
    lancamento: str

class Emprestimo(BaseModel):
    id_emprestimo: int
    id_cliente: int
    id_livro: int
    dt_emprestimo: str

# ========================================================
# 💾 BANCO DE DADOS EM MEMÓRIA (Listas)
# ========================================================
db_autores: List[Autor] = []
db_clientes: List[Cliente] = []
db_livros: List[Livro] = []
db_emprestimos: List[Emprestimo] = []

# ========================================================
# 👥 CRUD: AUTORES
# ========================================================

# CORRIGIDO: de 'obtener_autores' para 'obter_autores'
@app.get("/autores", response_model=List[Autor])
def obter_autores():
    return db_autores

@app.post("/autores", status_code=201)
def criar_autor(autor: Autor):
    for a in db_autores:
        if a.id_autor == autor.id_autor:
            raise HTTPException(status_code=400, detail="Já existe um autor com este ID.")
    db_autores.append(autor)
    return {"message": "Autor cadastrado com sucesso!"}

@app.put("/autores/{id_autor}")
def atualizar_autor(id_autor: int, autor_atualizado: Autor):
    for i, a in enumerate(db_autores):
        if a.id_autor == id_autor:
            db_autores[i] = autor_atualizado
            return {"message": "Autor actualizado com sucesso!"}
    raise HTTPException(status_code=404, detail="Autor não encontrado.")

@app.delete("/autores/{id_autor}")
def eliminar_autor(id_autor: int):
    for i, a in enumerate(db_autores):
        if a.id_autor == id_autor:
            # Validação: impede remoção se o autor tiver livros associados
            for livro in db_livros:
                if livro.id_autor == id_autor:
                    raise HTTPException(status_code=400, detail="Não é possível eliminar um autor que possui livros cadastrados.")
            db_autores.pop(i)
            return {"message": "Autor eliminado com sucesso!"}
    raise HTTPException(status_code=404, detail="Autor não encontrado.")

# ========================================================
# 👤 CRUD: CLIENTES
# ========================================================

# CORRIGIDO: de 'obtener_clientes' para 'obter_clientes'
@app.get("/clientes", response_model=List[Cliente])
def obter_clientes():
    return db_clientes

@app.post("/clientes", status_code=201)
def criar_cliente(cliente: Cliente):
    for c in db_clientes:
        if c.id_cliente == cliente.id_cliente:
            raise HTTPException(status_code=400, detail="Já existe um cliente com este ID.")
    db_clientes.append(cliente)
    return {"message": "Cliente cadastrado com sucesso!"}

@app.put("/clientes/{id_cliente}")
def atualizar_cliente(id_cliente: int, cliente_atualizado: Cliente):
    for i, c in enumerate(db_clientes):
        if c.id_cliente == id_cliente:
            db_clientes[i] = cliente_atualizado
            return {"message": "Cliente atualizado com sucesso!"}
    raise HTTPException(status_code=404, detail="Cliente não encontrado.")

@app.delete("/clientes/{id_cliente}")
def eliminar_cliente(id_cliente: int):
    for i, c in enumerate(db_clientes):
        if c.id_cliente == id_cliente:
            # Validação: impede remoção se o cliente tiver empréstimos ativos
            for emp in db_emprestimos:
                if emp.id_cliente == id_cliente:
                    raise HTTPException(status_code=400, detail="Não é possível eliminar um cliente com empréstimos pendentes.")
            db_clientes.pop(i)
            return {"message": "Cliente eliminado com sucesso!"}
    raise HTTPException(status_code=404, detail="Cliente não encontrado.")

# ========================================================
# 📖 CRUD: LIVROS
# ========================================================

# CORRIGIDO: de 'obtener_livros' para 'obter_livros'
@app.get("/livros", response_model=List[Livro])
def obter_livros():
    return db_livros

@app.post("/livros", status_code=201)
def criar_livro(livro: Livro):
    # Garante que o autor informado realmente existe na memória
    autor_existe = any(a.id_autor == livro.id_autor for a in db_autores)
    if not autor_existe:
        raise HTTPException(status_code=400, detail="Autor vinculado não existe. Cadastre o autor primeiro.")
        
    for l in db_livros:
        if l.id_livro == livro.id_livro:
            raise HTTPException(status_code=400, detail="Já existe um livro com este ID.")
            
    db_livros.append(livro)
    return {"message": "Livro cadastrado com sucesso!"}

@app.put("/livros/{id_livro}")
def atualizar_livro(id_livro: int, livro_atualizado: Livro):
    autor_existe = any(a.id_autor == livro_atualizado.id_autor for a in db_autores)
    if not autor_existe:
        raise HTTPException(status_code=400, detail="Autor vinculado não existe.")
        
    for i, l in enumerate(db_livros):
        if l.id_livro == id_livro:
            db_livros[i] = livro_atualizado
            return {"message": "Livro atualizado com sucesso!"}
    raise HTTPException(status_code=404, detail="Livro não encontrado.")

@app.delete("/livros/{id_livro}")
def eliminar_livro(id_livro: int):
    for i, l in enumerate(db_livros):
        if l.id_livro == id_livro:
            # Validação: impede a remoção se o livro estiver emprestado no momento
            for emp in db_emprestimos:
                if emp.id_livro == id_livro:
                    raise HTTPException(status_code=400, detail="Não é possível eliminar um livro que está emprestado.")
            db_livros.pop(i)
            return {"message": "Livro eliminado com sucesso!"}
    raise HTTPException(status_code=404, detail="Livro não encontrado.")

# ========================================================
# 🤝 CRUD: EMPRÉSTIMOS
# ========================================================

# CORRIGIDO: de 'obtener_emprestimos' para 'obter_emprestimos'
@app.get("/emprestimos", response_model=List[Emprestimo])
def obter_emprestimos():
    return db_emprestimos

@app.post("/emprestimos", status_code=201)
def criar_emprestimo(emprestimo: Emprestimo):
    # Garante que o cliente e o livro informados existem antes de fechar o empréstimo
    cliente_existe = any(c.id_cliente == emprestimo.id_cliente for c in db_clientes)
    livro_existe = any(l.id_livro == emprestimo.id_livro for l in db_livros)
    
    if not cliente_existe:
        raise HTTPException(status_code=400, detail="Cliente não encontrado.")
    if not livro_existe:
        raise HTTPException(status_code=400, detail="Livro não encontrado.")
        
    for e in db_emprestimos:
        if e.id_emprestimo == emprestimo.id_emprestimo:
            raise HTTPException(status_code=400, detail="Já existe um empréstimo com este ID.")
            
    db_emprestimos.append(emprestimo)
    return {"message": "Empréstimo realizado com sucesso!"}

@app.put("/emprestimos/{id_emprestimo}")
def atualizar_emprestimo(id_emprestimo: int, emprestimo_atualizado: Emprestimo):
    cliente_existe = any(c.id_cliente == emprestimo_atualizado.id_cliente for c in db_clientes)
    livro_existe = any(l.id_livro == emprestimo_atualizado.id_livro for l in db_livros)
    
    if not cliente_existe or not livro_existe:
        raise HTTPException(status_code=400, detail="Cliente ou Livro inválido.")
        
    for i, e in enumerate(db_emprestimos):
        if e.id_emprestimo == id_emprestimo:
            db_emprestimos[i] = emprestimo_atualizado
            return {"message": "Empréstimo atualizado com sucesso!"}
    raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")

@app.delete("/emprestimos/{id_emprestimo}")
def eliminar_emprestimo(id_emprestimo: int):
    for i, e in enumerate(db_emprestimos):
        if e.id_emprestimo == id_emprestimo:
            db_emprestimos.pop(i)
            return {"message": "Empréstimo removido/devolvido com sucesso!"}
    raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
