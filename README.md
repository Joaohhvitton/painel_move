# 📊 Painel de Atualização MOVE 07.02.50

Acompanhamento em tempo real dos terminais MOVE atualizados para a versão **07.02.50**, por Diretoria e DDD.

---

## 🚀 Como configurar (passo a passo)

### 1 — Criar o repositório no GitHub

1. Acesse [github.com](https://github.com) e faça login
2. Clique em **"New repository"**
3. Nome sugerido: `painel-move`
4. Marque **Private** (recomendado) ou Public
5. Clique em **"Create repository"**

---

### 2 — Enviar os arquivos

> Se não tiver o Git instalado, use o **GitHub Desktop** (mais fácil).

**Opção A — GitHub Desktop (recomendado para iniciantes):**
1. Baixe em: https://desktop.github.com
2. Clone o repositório que você criou
3. Copie todos os arquivos desta pasta para dentro do repositório clonado
4. Faça commit e Push

**Opção B — Git via terminal:**
```bash
git init
git remote add origin https://github.com/SEU_USUARIO/painel-move.git
git add .
git commit -m "🚀 Estrutura inicial do painel"
git push -u origin main
```

---

### 3 — Ativar o GitHub Pages

1. No repositório, vá em **Settings** → **Pages**
2. Em "Source", selecione:
   - Branch: `main`
   - Folder: `/docs`
3. Clique em **Save**
4. Aguarde ~1 minuto. Seu site ficará em:
   ```
   https://SEU_USUARIO.github.io/painel-move/
   ```

---

### 4 — Dar permissão ao Actions para fazer commit

1. Vá em **Settings** → **Actions** → **General**
2. Role até "Workflow permissions"
3. Selecione **"Read and write permissions"**
4. Clique em **Save**

---

## 🔄 Como atualizar os dados

### Fluxo automático

```
Você substitui o arquivo Excel em data/
          ↓
GitHub detecta a mudança
          ↓
GitHub Actions roda o Python automaticamente
          ↓
data.json é atualizado no repositório
          ↓
Site reflete os novos dados (sem mexer em nada)
```

### Passo a passo para atualizar

1. **Substitua** o arquivo Excel na pasta `data/`
   - O arquivo pode ter qualquer nome (`.xlsx`)
   - Ele precisa ter a aba chamada **"Base"**
   - A aba Base precisa ter as colunas: `DDD`, `New Versão` (ou `Versão SGV`), `Dia Avaliado`

2. **Faça commit e push** do novo Excel

3. **Aguarde ~1-2 minutos** — o GitHub Actions vai processar automaticamente

4. **Verifique** em Actions → "🤖 Atualizar Painel MOVE" que o workflow ficou verde ✅

5. O site atualiza sozinho. Clique em **"Atualizar"** no painel para ver os novos dados.

---

## 📁 Estrutura de arquivos

```
painel-move/
├── .github/
│   └── workflows/
│       └── update.yml        ← Automação do GitHub Actions
├── data/
│   └── base.xlsx             ← Coloque aqui o Excel atualizado
├── docs/
│   ├── index.html            ← Site do painel (não mexa)
│   └── data.json             ← Gerado automaticamente (não mexa)
├── scripts/
│   └── process.py            ← Script Python de processamento
├── requirements.txt          ← Dependências Python
└── README.md                 ← Este arquivo
```

---

## ⚙️ Colunas esperadas na aba "Base"

| Coluna | Descrição | Obrigatória |
|--------|-----------|-------------|
| `DDD` | DDD do terminal | ✅ Sim |
| `New Versão` | Versão atual do terminal | ✅ Sim |
| `Versão SGV` | Alternativa se "New Versão" não existir | ✅ (uma das duas) |
| `Dia Avaliado` | Data em que o terminal foi atualizado | Para o gráfico de evolução |
| `Versão App` | Versão do app | Opcional |

> A versão alvo é **07.02.50**. Terminais com `New Versão = 07.02.50` são contados como atualizados.

---

## 🛠 Execução local (para testar)

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar o script manualmente
python scripts/process.py

# Abrir o site localmente
# Use um servidor local — o index.html precisa buscar data.json via HTTP
python -m http.server 8080 --directory docs
# Acesse: http://localhost:8080
```

---

## 🐛 Problemas comuns

| Problema | Solução |
|----------|---------|
| Actions deu erro | Vá em Actions → clique no workflow com ❌ → veja os logs |
| `Aba 'Base' não encontrada` | Verifique se a aba do Excel se chama exatamente **Base** |
| `Nenhum arquivo .xlsx encontrado` | Verifique se o Excel está na pasta `data/` |
| Site mostra dados antigos | Clique no botão "Atualizar" no painel ou force refresh (Ctrl+F5) |
| GitHub Pages não abre | Aguarde 2-3 minutos após ativar, verifique Settings → Pages |
