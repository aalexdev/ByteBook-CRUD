const URL_API = "http://127.0.0.1:8000";

// Estados de Edição para controlar se estamos inserindo ou atualizando
let modosEdicao = { autores: false, clientes: false, livros: false, emprestimos: false };

// Inicializa o sistema carregando o dashboard por padrão
window.onload = () => {
  mudarAba('dashboard');
};

function mudarAba(idAba) {
  document.querySelectorAll('.aba-conteudo').forEach(aba => aba.style.display = 'none');
  document.getElementById(`sec-${idAba}`).style.display = 'flex';

  document.querySelectorAll('.btn-menu').forEach(btn => btn.classList.remove('active'));
  document.getElementById(`btn-${idAba}`).classList.add('active');

  // Reseta qualquer estado de edição pendente ao mudar de aba
  cancelarEdicaoGeral(idAba);

  if (idAba === 'dashboard') carregarMetricasDashboard();
  if (idAba === 'autores') listarAutores();
  if (idAba === 'clientes') listarClientes();
  if (idAba === 'livros') listarLivros();
  if (idAba === 'emprestimos') listarEmprestimos();
}

function cancelarEdicaoGeral(aba) {
  modosEdicao[aba] = false;
  const form = document.getElementById(`form-${aba.replace(/s$/, '')}`);
  const btn = document.getElementById(`btn-submit-${aba.replace(/s$/, '')}`);
  const inputId = document.getElementById(`${aba.substring(0, 3)}-id`);

  if (form) form.reset();
  if (btn) btn.innerText = "Salvar Registro";
  if (inputId) inputId.disabled = false;
}

// ==========================================
// OPERAÇÕES: DASHBOARD (NOVO)
// ==========================================
async function carregarMetricasDashboard() {
  try {
    // 1. Busca total de clientes
    const resClientes = await fetch(`${URL_API}/clientes`);
    const clientes = await resClientes.json();
    document.getElementById('dash-clientes').innerText = clientes.length;

    // 2. Busca total de livros
    const resLivros = await fetch(`${URL_API}/livros`);
    const livros = await resLivros.json();
    document.getElementById('dash-livros').innerText = livros.length;

    // 3. Busca empréstimos e calcula Ativos vs Expirados
    const resEmprestimos = await fetch(`${URL_API}/emprestimos`);
    const emprestimos = await resEmprestimos.json();

    document.getElementById('dash-ativos').innerText = emprestimos.length;

    let contExpirados = 0;
    const dataAtual = new Date();
    const prazoDias = 14; // Regra de negócio: 14 dias para devolução

    emprestimos.forEach(emp => {
      // Converte a string 'AAAA-MM-DD' vinda do FastAPI para um objeto Date do JavaScript
      const dataEmprestimo = new Date(emp.dt_emprestimo);

      // Calcula a data limite de devolução
      const dataLimite = new Date(dataEmprestimo);
      dataLimite.setDate(dataLimite.getDate() + prazoDias);

      // Se a data limite já passou em relação a hoje, está expirado
      if (dataAtual > dataLimite) {
        contExpirados++;
      }
    });

    document.getElementById('dash-expirados').innerText = contExpirados;

  } catch (error) {
    console.error("Erro ao carregar dados do dashboard:", error);
    document.getElementById('dash-clientes').innerText = "error";
    document.getElementById('dash-livros').innerText = "error";
    document.getElementById('dash-ativos').innerText = "error";
    document.getElementById('dash-expirados').innerText = "error";
  }
}

// ==========================================
// OPERAÇÕES: AUTORES
// ==========================================
async function listarAutores() {
  const res = await fetch(`${URL_API}/autores`);
  const autores = await res.json();
  const corpo = document.getElementById('tabela-autores');
  corpo.innerHTML = '';
  autores.forEach(a => {
    corpo.innerHTML += `<tr>
            <td>${a.id_autor}</td>
            <td>${a.nome}</td>
            <td>${a.idade}</td>
            <td>${a.nacionalidade}</td>
            <td>
                <div class="acoes-flex">
                    <button class="btn-editar" onclick="prepararEditarAutor(${a.id_autor}, '${a.nome.replace(/'/g, "\\'")}', ${a.idade}, '${a.nacionalidade.replace(/'/g, "\\'")}')">Editar</button>
                    <button class="btn-deletar" onclick="deletarItem('autores', ${a.id_autor})">Eliminar</button>
                </div>
            </td>
        </tr>`;
  });
}

function prepararEditarAutor(id, nome, idade, nacionalidade) {
  modosEdicao.autores = true;
  document.getElementById('aut-id').value = id;
  document.getElementById('aut-id').disabled = true;
  document.getElementById('aut-nome').value = nome;
  document.getElementById('aut-idade').value = idade;
  document.getElementById('aut-nacionalidade').value = nacionalidade;
  document.getElementById('btn-submit-autor').innerText = "Atualizar Registro 📝";
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function salvarAutor(event) {
  event.preventDefault();
  const id = parseInt(document.getElementById('aut-id').value);
  const dados = {
    id_autor: id,
    nome: document.getElementById('aut-nome').value,
    idade: parseInt(document.getElementById('aut-idade').value),
    nacionalidade: document.getElementById('aut-nacionalidade').value
  };

  let res;
  if (modosEdicao.autores) {
    res = await fetch(`${URL_API}/autores/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) });
  } else {
    res = await fetch(`${URL_API}/autores`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) });
  }
  tratarResposta(res, 'form-autor', listarAutores, 'autores');
}

// ==========================================
// OPERAÇÕES: CLIENTES
// ==========================================
async function listarClientes() {
  const res = await fetch(`${URL_API}/clientes`);
  const clientes = await res.json();
  const corpo = document.getElementById('tabela-clientes');
  corpo.innerHTML = '';
  clientes.forEach(c => {
    corpo.innerHTML += `<tr>
            <td>${c.id_cliente}</td>
            <td>${c.nome}</td>
            <td>${c.cpf}</td>
            <td>${c.telefone}</td>
            <td>
                <div class="acoes-flex">
                    <button class="btn-editar" onclick="prepararEditarCliente(${c.id_cliente}, '${c.nome.replace(/'/g, "\\'")}', '${c.cpf}', '${c.telefone}', '${c.endereco.replace(/'/g, "\\'")}')">Editar</button>
                    <button class="btn-deletar" onclick="deletarItem('clientes', ${c.id_cliente})">Eliminar</button>
                </div>
            </td>
        </tr>`;
  });
}

function prepararEditarCliente(id, nome, cpf, telephone, address) {
  modosEdicao.clientes = true;
  document.getElementById('cli-id').value = id;
  document.getElementById('cli-id').disabled = true;
  document.getElementById('cli-nome').value = nome;
  document.getElementById('cli-cpf').value = cpf;
  document.getElementById('cli-tel').value = telephone;
  document.getElementById('cli-end').value = address;
  document.getElementById('btn-submit-cliente').innerText = "Atualizar Registro 📝";
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function salvarCliente(event) {
  event.preventDefault();
  const id = parseInt(document.getElementById('cli-id').value);
  const dados = {
    id_cliente: id,
    nome: document.getElementById('cli-nome').value,
    cpf: document.getElementById('cli-cpf').value,
    telephone: document.getElementById('cli-tel').value,
    address: document.getElementById('cli-end').value
  };

  let res;
  if (modosEdicao.clientes) {
    res = await fetch(`${URL_API}/clientes/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) });
  } else {
    res = await fetch(`${URL_API}/clientes`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) });
  }
  tratarResposta(res, 'form-cliente', listarClientes, 'clientes');
}

// ==========================================
// OPERAÇÕES: LIVROS
// ==========================================
async function listarLivros() {
  const res = await fetch(`${URL_API}/livros`);
  const livros = await res.json();
  const corpo = document.getElementById('tabela-livros');
  corpo.innerHTML = '';
  livros.forEach(l => {
    corpo.innerHTML += `<tr>
            <td>${l.id_livro}</td>
            <td>${l.id_autor}</td>
            <td>${l.titulo}</td>
            <td>${l.lancamento}</td>
            <td>
                <div class="acoes-flex">
                    <button class="btn-editar" onclick="prepararEditarLivro(${l.id_livro}, ${l.id_autor}, '${l.titulo.replace(/'/g, "\\'")}', '${l.lancamento}')">Editar</button>
                    <button class="btn-deletar" onclick="deletarItem('livros', ${l.id_livro})">Eliminar</button>
                </div>
            </td>
        </tr>`;
  });
}

function prepararEditarLivro(id, idAutor, titulo, lancamento) {
  modosEdicao.livros = true;
  document.getElementById('liv-id').value = id;
  document.getElementById('liv-id').disabled = true;
  document.getElementById('liv-autor-id').value = idAutor;
  document.getElementById('liv-titulo').value = titulo;
  document.getElementById('liv-lancamento').value = lancamento;
  document.getElementById('btn-submit-livro').innerText = "Atualizar Registro 📝";
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function salvarLivro(event) {
  event.preventDefault();
  const id = parseInt(document.getElementById('liv-id').value);
  const dados = {
    id_livro: id,
    id_autor: parseInt(document.getElementById('liv-autor-id').value),
    titulo: document.getElementById('liv-titulo').value,
    lancamento: document.getElementById('liv-lancamento').value
  };

  let res;
  if (modosEdicao.livros) {
    res = await fetch(`${URL_API}/livros/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) });
  } else {
    res = await fetch(`${URL_API}/livros`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) });
  }
  tratarResposta(res, 'form-livro', listarLivros, 'livros');
}

// ==========================================
// OPERAÇÕES: EMPRÉSTIMOS
// ==========================================
async function listarEmprestimos() {
  const res = await fetch(`${URL_API}/emprestimos`);
  const emprestimos = await res.json();
  const corpo = document.getElementById('tabela-emprestimos');
  corpo.innerHTML = '';
  emprestimos.forEach(e => {
    corpo.innerHTML += `<tr>
            <td>${e.id_emprestimo}</td>
            <td>${e.id_cliente}</td>
            <td>${e.id_livro}</td>
            <td>${e.dt_emprestimo}</td>
            <td>
                <div class="acoes-flex">
                    <button class="btn-editar" onclick="prepararEditarEmprestimo(${e.id_emprestimo}, ${e.id_cliente}, ${e.id_livro}, '${e.dt_emprestimo}')">Editar</button>
                    <button class="btn-deletar" onclick="deletarItem('emprestimos', ${e.id_emprestimo})">Eliminar</button>
                </div>
            </td>
        </tr>`;
  });
}

function prepararEditarEmprestimo(id, idCliente, idLivro, data) {
  modosEdicao.emprestimos = true;
  document.getElementById('emp-id').value = id;
  document.getElementById('emp-id').disabled = true;
  document.getElementById('emp-cli-id').value = idCliente;
  document.getElementById('emp-liv-id').value = idLivro;
  document.getElementById('emp-data').value = data;
  document.getElementById('btn-submit-emprestimo').innerText = "Atualizar Operação 📝";
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function salvarEmprestimo(event) {
  event.preventDefault();
  const id = parseInt(document.getElementById('emp-id').value);
  const dados = {
    id_emprestimo: id,
    id_cliente: parseInt(document.getElementById('emp-cli-id').value),
    id_livro: parseInt(document.getElementById('emp-liv-id').value),
    dt_emprestimo: document.getElementById('emp-data').value
  };

  let res;
  if (modosEdicao.emprestimos) {
    res = await fetch(`${URL_API}/emprestimos/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) });
  } else {
    res = await fetch(`${URL_API}/emprestimos`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) });
  }
  tratarResposta(res, 'form-emprestimo', listarEmprestimos, 'emprestimos');
}

// ==========================================
// COMPONENTES AUXILIARES GLOBAIS
// ==========================================
async function deletarItem(endpoint, id) {
  const res = await fetch(`${URL_API}/${endpoint}/${id}`, { method: 'DELETE' });
  const data = await res.json();
  if (res.ok) {
    alert(data.message);
    mudarAba(endpoint);
  } else {
    alert("Erro: " + data.detail);
  }
}

async function tratarResposta(resposta, idForm, funcaoListar, aba) {
  const data = await responseData(resposta);
  if (resposta.ok) {
    alert(data.message || "Operação realizada com sucesso!");
    cancelarEdicaoGeral(aba);
    funcaoListar();
  } else {
    alert("Erro: " + (data.detail || "Falha na comunicação com o servidor."));
  }
}

async function responseData(res) {
  try {
    return await res.json();
  } catch (e) {
    return {};
  }
}
