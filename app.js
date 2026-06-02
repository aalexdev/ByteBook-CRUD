/**
 * ByteBook — app.js
 * Lógica completa do frontend: navegação, CRUD, modais, toast
 */

const API = "http://localhost:5000/api";

/* ══════════════════════════════════════════════
   NAVEGAÇÃO
══════════════════════════════════════════════ */
document.querySelectorAll(".nav-item").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
    btn.classList.add("active");
    const sec = btn.dataset.section;
    document.getElementById(`section-${sec}`).classList.add("active");
    if (sec === "dashboard")   carregarDashboard();
    if (sec === "livros")      carregarLivros();
    if (sec === "clientes")    carregarClientes();
    if (sec === "emprestimos") carregarEmprestimos("todos");
  });
});

/* ══════════════════════════════════════════════
   TOAST
══════════════════════════════════════════════ */
let toastTimer;
function showToast(msg, type = "info") {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = `toast ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.add("hidden"), 3500);
}

/* ══════════════════════════════════════════════
   HTTP HELPERS
══════════════════════════════════════════════ */
async function api(path, options = {}) {
  try {
    const res = await fetch(`${API}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Erro desconhecido");
    return data;
  } catch (err) {
    showToast(err.message, "error");
    throw err;
  }
}

/* ══════════════════════════════════════════════
   DASHBOARD
══════════════════════════════════════════════ */
async function carregarDashboard() {
  try {
    const stats = await api("/dashboard");
    document.getElementById("val-livros").textContent      = stats.total_livros;
    document.getElementById("val-clientes").textContent    = stats.total_clientes;
    document.getElementById("val-ativos").textContent      = stats.emprestimos_ativos;
    document.getElementById("val-devolvidos").textContent  = stats.emprestimos_devolvidos;

    const ul = document.getElementById("lista-populares");
    ul.innerHTML = "";
    if (!stats.livros_populares?.length) {
      ul.innerHTML = "<li style='color:var(--text-3);font-style:italic'>Nenhum empréstimo registrado ainda.</li>";
    } else {
      stats.livros_populares.forEach(l => {
        const li = document.createElement("li");
        li.innerHTML = `<span>${l.titulo}</span><span class="pop-count">${l.total}x</span>`;
        ul.appendChild(li);
      });
    }
  } catch (_) {}
}

/* ══════════════════════════════════════════════
   LIVROS
══════════════════════════════════════════════ */
async function carregarLivros(q = "") {
  try {
    const livros = await api(`/livros${q ? `?q=${encodeURIComponent(q)}` : ""}`);
    const tbody  = document.getElementById("tbody-livros");
    tbody.innerHTML = "";
    if (!livros.length) {
      tbody.innerHTML = `<tr class="empty-row"><td colspan="8">Nenhum livro encontrado.</td></tr>`;
      return;
    }
    livros.forEach(l => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${l.id}</td>
        <td style="color:var(--text);font-weight:600">${esc(l.titulo)}</td>
        <td>${esc(l.autor)}</td>
        <td><code style="font-family:var(--font-mono);font-size:11px;color:var(--text-3)">${esc(l.isbn || "—")}</code></td>
        <td>${esc(l.genero || "—")}</td>
        <td>${l.ano || "—"}</td>
        <td style="text-align:center">${l.quantidade}</td>
        <td>
          <div class="actions-cell">
            <button class="btn-icon" onclick='editarLivro(${JSON.stringify(l)})'>Editar</button>
            <button class="btn-icon danger" onclick="confirmarDelete('livro',${l.id},'${esc(l.titulo)}')">Excluir</button>
          </div>
        </td>`;
      tbody.appendChild(tr);
    });
  } catch (_) {}
}

function buscar(tipo) {
  const q = document.getElementById(`busca-${tipo}`).value;
  if (tipo === "livros")   carregarLivros(q);
  if (tipo === "clientes") carregarClientes(q);
}

/* ── Form Livro ───────────────────────────────── */
document.getElementById("form-livro").addEventListener("submit", async e => {
  e.preventDefault();
  const id = document.getElementById("livro-id").value;
  const payload = {
    titulo:     document.getElementById("livro-titulo").value,
    autor:      document.getElementById("livro-autor").value,
    isbn:       document.getElementById("livro-isbn").value  || null,
    genero:     document.getElementById("livro-genero").value || null,
    ano:        parseInt(document.getElementById("livro-ano").value) || null,
    quantidade: parseInt(document.getElementById("livro-quantidade").value) || 1,
  };
  try {
    if (id) {
      await api(`/livros/${id}`, { method: "PUT", body: JSON.stringify(payload) });
      showToast("Livro atualizado com sucesso!", "success");
    } else {
      await api("/livros", { method: "POST", body: JSON.stringify(payload) });
      showToast("Livro cadastrado com sucesso!", "success");
    }
    fecharModal("livro");
    carregarLivros();
  } catch (_) {}
});

function editarLivro(livro) {
  document.getElementById("modal-livro-title").textContent = "Editar Livro";
  document.getElementById("livro-id").value        = livro.id;
  document.getElementById("livro-titulo").value    = livro.titulo;
  document.getElementById("livro-autor").value     = livro.autor;
  document.getElementById("livro-isbn").value      = livro.isbn || "";
  document.getElementById("livro-genero").value    = livro.genero || "";
  document.getElementById("livro-ano").value       = livro.ano || "";
  document.getElementById("livro-quantidade").value = livro.quantidade;
  document.getElementById("modal-livro").classList.remove("hidden");
}

/* ══════════════════════════════════════════════
   CLIENTES
══════════════════════════════════════════════ */
async function carregarClientes(q = "") {
  try {
    const clientes = await api(`/clientes${q ? `?q=${encodeURIComponent(q)}` : ""}`);
    const tbody    = document.getElementById("tbody-clientes");
    tbody.innerHTML = "";
    if (!clientes.length) {
      tbody.innerHTML = `<tr class="empty-row"><td colspan="6">Nenhum cliente encontrado.</td></tr>`;
      return;
    }
    clientes.forEach(c => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${c.id}</td>
        <td style="color:var(--text);font-weight:600">${esc(c.nome)}</td>
        <td>${esc(c.email)}</td>
        <td>${esc(c.telefone || "—")}</td>
        <td><code style="font-family:var(--font-mono);font-size:11px;color:var(--text-3)">${esc(c.cpf || "—")}</code></td>
        <td>
          <div class="actions-cell">
            <button class="btn-icon" onclick='editarCliente(${JSON.stringify(c)})'>Editar</button>
            <button class="btn-icon danger" onclick="confirmarDelete('cliente',${c.id},'${esc(c.nome)}')">Excluir</button>
          </div>
        </td>`;
      tbody.appendChild(tr);
    });
  } catch (_) {}
}

/* ── Form Cliente ─────────────────────────────── */
document.getElementById("form-cliente").addEventListener("submit", async e => {
  e.preventDefault();
  const id = document.getElementById("cliente-id").value;
  const payload = {
    nome:      document.getElementById("cliente-nome").value,
    email:     document.getElementById("cliente-email").value,
    telefone:  document.getElementById("cliente-telefone").value || null,
    cpf:       document.getElementById("cliente-cpf").value || null,
  };
  try {
    if (id) {
      await api(`/clientes/${id}`, { method: "PUT", body: JSON.stringify(payload) });
      showToast("Cliente atualizado!", "success");
    } else {
      await api("/clientes", { method: "POST", body: JSON.stringify(payload) });
      showToast("Cliente cadastrado!", "success");
    }
    fecharModal("cliente");
    carregarClientes();
  } catch (_) {}
});

function editarCliente(cliente) {
  document.getElementById("modal-cliente-title").textContent = "Editar Cliente";
  document.getElementById("cliente-id").value       = cliente.id;
  document.getElementById("cliente-nome").value     = cliente.nome;
  document.getElementById("cliente-email").value    = cliente.email;
  document.getElementById("cliente-telefone").value = cliente.telefone || "";
  document.getElementById("cliente-cpf").value      = cliente.cpf || "";
  document.getElementById("modal-cliente").classList.remove("hidden");
}

/* ══════════════════════════════════════════════
   EMPRÉSTIMOS
══════════════════════════════════════════════ */
let filtroAtual = "todos";

async function carregarEmprestimos(status = filtroAtual) {
  filtroAtual = status;
  try {
    const lista = await api(`/emprestimos?status=${status}`);
    const tbody = document.getElementById("tbody-emprestimos");
    tbody.innerHTML = "";
    if (!lista.length) {
      tbody.innerHTML = `<tr class="empty-row"><td colspan="7">Nenhum empréstimo encontrado.</td></tr>`;
      return;
    }
    lista.forEach(emp => {
      const devolvido = !!emp.devolvido;
      const badge = devolvido
        ? `<span class="badge badge-done">Devolvido</span>`
        : `<span class="badge badge-active">Ativo</span>`;
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${emp.id}</td>
        <td style="color:var(--text);font-weight:600">${esc(emp.livro_titulo)}</td>
        <td>${esc(emp.cliente_nome)}</td>
        <td><code style="font-family:var(--font-mono);font-size:11px">${formatDate(emp.data_emprestimo)}</code></td>
        <td><code style="font-family:var(--font-mono);font-size:11px">${formatDate(emp.data_devolucao)}</code></td>
        <td>${badge}</td>
        <td>
          <div class="actions-cell">
            ${!devolvido ? `<button class="btn-icon success" onclick="devolverEmprestimo(${emp.id})">Devolver</button>` : ""}
            <button class="btn-icon danger" onclick="confirmarDelete('emprestimo',${emp.id},'empréstimo #${emp.id}')">Excluir</button>
          </div>
        </td>`;
      tbody.appendChild(tr);
    });
  } catch (_) {}
}

async function devolverEmprestimo(id) {
  try {
    await api(`/emprestimos/${id}/devolver`, { method: "PATCH", body: JSON.stringify({}) });
    showToast("Devolução registrada!", "success");
    carregarEmprestimos();
    carregarDashboard();
  } catch (_) {}
}

function filtrarEmprestimos(status, btn) {
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  carregarEmprestimos(status);
}

/* ── Form Empréstimo ──────────────────────────── */
document.getElementById("form-emprestimo").addEventListener("submit", async e => {
  e.preventDefault();
  const payload = {
    livro_id:         parseInt(document.getElementById("emp-livro").value),
    cliente_id:       parseInt(document.getElementById("emp-cliente").value),
    data_emprestimo:  document.getElementById("emp-data-emprestimo").value,
    data_devolucao:   document.getElementById("emp-data-devolucao").value || null,
  };
  try {
    await api("/emprestimos", { method: "POST", body: JSON.stringify(payload) });
    showToast("Empréstimo registrado!", "success");
    fecharModal("emprestimo");
    carregarEmprestimos();
    carregarDashboard();
  } catch (_) {}
});

/* ── Popular selects ao abrir modal empréstimo ─── */
async function popularSelectsEmprestimo() {
  try {
    const [livros, clientes] = await Promise.all([api("/livros"), api("/clientes")]);
    const selLivro   = document.getElementById("emp-livro");
    const selCliente = document.getElementById("emp-cliente");
    selLivro.innerHTML   = `<option value="">Selecione um livro…</option>`;
    selCliente.innerHTML = `<option value="">Selecione um cliente…</option>`;
    livros.forEach(l => {
      const opt = document.createElement("option");
      opt.value = l.id; opt.textContent = `${l.titulo} — ${l.autor}`;
      selLivro.appendChild(opt);
    });
    clientes.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.id; opt.textContent = `${c.nome} (${c.email})`;
      selCliente.appendChild(opt);
    });
    document.getElementById("emp-data-emprestimo").value = new Date().toISOString().split("T")[0];
  } catch (_) {}
}

/* ══════════════════════════════════════════════
   MODAIS
══════════════════════════════════════════════ */
function abrirModal(tipo) {
  if (tipo === "livro") {
    document.getElementById("modal-livro-title").textContent = "Novo Livro";
    document.getElementById("form-livro").reset();
    document.getElementById("livro-id").value = "";
  }
  if (tipo === "cliente") {
    document.getElementById("modal-cliente-title").textContent = "Novo Cliente";
    document.getElementById("form-cliente").reset();
    document.getElementById("cliente-id").value = "";
  }
  if (tipo === "emprestimo") {
    document.getElementById("form-emprestimo").reset();
    popularSelectsEmprestimo();
  }
  document.getElementById(`modal-${tipo}`).classList.remove("hidden");
}

function fecharModal(tipo) {
  document.getElementById(`modal-${tipo}`).classList.add("hidden");
}

/* Fechar ao clicar fora */
document.querySelectorAll(".modal-overlay").forEach(overlay => {
  overlay.addEventListener("click", e => {
    if (e.target === overlay) {
      overlay.classList.add("hidden");
    }
  });
});

/* ══════════════════════════════════════════════
   DELETE COM CONFIRMAÇÃO
══════════════════════════════════════════════ */
function confirmarDelete(tipo, id, nome) {
  const msgs = {
    livro:      `Excluir o livro "${nome}"? Esta ação não poderá ser desfeita.`,
    cliente:    `Excluir o cliente "${nome}"? Esta ação não poderá ser desfeita.`,
    emprestimo: `Excluir o ${nome}? Esta ação não poderá ser desfeita.`,
  };
  document.getElementById("confirm-msg").textContent = msgs[tipo];
  document.getElementById("modal-confirm").classList.remove("hidden");

  const btn = document.getElementById("btn-confirm-delete");
  btn.onclick = async () => {
    try {
      const endpoints = { livro: "livros", cliente: "clientes", emprestimo: "emprestimos" };
      await api(`/${endpoints[tipo]}/${id}`, { method: "DELETE" });
      showToast("Item excluído com sucesso.", "info");
      fecharModal("confirm");
      if (tipo === "livro")       carregarLivros();
      if (tipo === "cliente")     carregarClientes();
      if (tipo === "emprestimo")  carregarEmprestimos();
      carregarDashboard();
    } catch (_) { fecharModal("confirm"); }
  };
}

/* ══════════════════════════════════════════════
   UTILS
══════════════════════════════════════════════ */
function esc(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatDate(dateStr) {
  if (!dateStr) return "—";
  const [y, m, d] = dateStr.split("T")[0].split("-");
  return `${d}/${m}/${y}`;
}

/* ══════════════════════════════════════════════
   INICIALIZAÇÃO
══════════════════════════════════════════════ */
carregarDashboard();
