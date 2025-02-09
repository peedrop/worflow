# 📈 Stock Analysis Workflow - Prefect

Este projeto implementa um **workflow automatizado** para coletar e analisar dados de ações, utilizando **Prefect Cloud** para gerenciamento e agendamento de execuções.

O workflow **busca dados financeiros**, calcula indicadores e armazena os resultados de maneira estruturada. Ele pode ser executado **localmente** ou em um ambiente gerenciado pelo **Prefect Cloud**.

---

## 📌 **Índice**

- [🎯 Visão Geral](#-visão-geral)
- [📂 Estrutura do Projeto](#-estrutura-do-projeto)
- [⚙️ Requisitos](#-requisitos)
- [🛠 Instalação e Configuração](#-instalação-e-configuração)
- [🚀 Deploy no Prefect Cloud](#-deploy-no-prefect-cloud)
- [📊 Como Visualizar os Resultados](#-como-visualizar-os-resultados)

---

## 🎯 **Visão Geral**

O **Stock Analysis Workflow** coleta dados financeiros de ações via **Yahoo Finance (yfinance)**, realiza cálculos de **médias móveis, variação percentual e volatilidade**, e salva os resultados em arquivos CSV organizados por **data e mês**.

Os resultados são registrados no **Prefect Cloud**, permitindo **monitoramento e reexecução automática**.

---

## 📂 **Estrutura do Projeto**

```
📚 stock-analysis-workflow
├── 📄 workflow.py            # Código principal do fluxo Prefect
├── 📄 README.md              # Documentação do projeto
└── 📂 data/                  # Diretório onde os arquivos CSV são armazenados
```

---

## ⚙️ **Requisitos**

- **Python 3.9+** instalado
- Conta no **[Prefect Cloud](https://app.prefect.cloud/)**
- Bibliotecas:
  - `prefect`
  - `pandas`
  - `yfinance`
  - `matplotlib`

📌 Se estiver rodando **no Prefect Managed Work Pool**, certifique-se de adicionar as dependências na configuração do **Work Pool**.

---

## 🛠 **Instalação e Configuração**

1️⃣ **Clone o repositório**:

```bash
git clone https://github.com/peedrop/worflow.git
cd stock-analysis-workflow
```

2️⃣ **Autentique-se no Prefect Cloud**:

```bash
prefect cloud login --key SEU_PREFECT_API_KEY
```

3️⃣ **Crie um Work Pool no Prefect Cloud**:

- Acesse **Work Pools** no Prefect Cloud
- Clique em **Create Work Pool**
- Escolha **"Managed"**
- Adicione os pacotes necessários (`pandas`, `yfinance`, `matplotlib`)

4️⃣ **Inicie o Worker (se for rodar localmente)**:

```bash
prefect worker start -p stock-analysis-local
```

---

## 🚀 **Deploy no Prefect Cloud**

Agora, crie e aplique o deployment para que o Prefect Cloud possa gerenciar a execução.

```bash
prefect deploy
```

Para testar manualmente:

```bash
prefect run deployment "Stock Analysis"
```

---

## 📊 **Como Visualizar os Resultados**

### **No Prefect Cloud**

1️⃣ Acesse [Prefect Cloud](https://app.prefect.cloud/)
2️⃣ Veja os logs e artefatos em `Runs`

### **Nos Arquivos CSV**

Os dados coletados são salvos na pasta `data/` com a seguinte estrutura:

```
📂 data/
   ├── 2025/
   │   ├── 02/
   │   │   ├── 2025-02-01.csv
   │   │   ├── 2025-02-02.csv
```

---