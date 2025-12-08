

## 🧠 Diagnóstico Empresarial 10 Dias — InNovaIdeia  
**MVP 1.4 — Flask + Bootstrap + Gemini 2.0/2.5 (com fallback offline)**

Sistema web inteligente projetado para gerar análises empresariais completas em minutos.  
Inclui: metas SMART, mapeamento de sistemas, ROI, roadmap de 180 dias e brief executivo final — tudo gerado automaticamente via IA (Gemini) ou via modo *Mock* offline.

---

## 🚀 Funcionalidades Principais

- ✔ Diagnóstico empresarial completo em 6 passos  
- ✔ Formulários limpos e responsivos (Bootstrap 5)  
- ✔ IA Gemini 2.0/2.5 integrada com fallback automático offline  
- ✔ Regeneração de conteúdo com IA (AJAX + endpoint `/api/regenerate`)  
- ✔ Visual corporativo com stepper, cards compactos e UI moderna  
- ✔ Exportação do relatório final em PDF via impressão  
- ✔ Totalmente executável localmente sem necessidade de conta Google  

---

## 🏗️ Arquitetura do Projeto

📁 raiz-do-projeto ├── app_v3.py ├── .env ├── requirements.txt └── README.md

---

## 🔧 Requisitos

### Python
- Python **3.9+**

### Pacotes Python (requirements.txt)
```txt
Flask
python-dotenv
google-generativeai
markupsafe


---

⚙️ Configuração das Variáveis de Ambiente

Crie um arquivo .env:

SECRET_KEY=sua_chave_secreta_aqui
GEMINI_API_KEY=sua_api_key_google_aqui

Se GEMINI_API_KEY não estiver configurada, o sistema opera automaticamente em modo de desenvolvimento (Mock AI), garantindo que nada quebre.


---

▶️ Como Executar

1. Instale dependências:



pip install -r requirements.txt

2. Execute o sistema:



python app_v3.py

3. Acesse no navegador:



http://127.0.0.1:5000


---

🧩 Estrutura das Rotas

Rota	Função

/	Formulário inicial (dados do cliente)
/create	Cria sessão inicial
/scope	Gera metas SMART
/map	Mapa de sistemas e gargalos
/roi	Simulação e análise de ROI
/roadmap	Roadmap de execução (3 fases)
/brief	Relatório final executivo
/api/regenerate	Regeneração inteligente via IA (AJAX)



---

🤖 Sobre o Modo Mock (Offline)

Se a chave do Gemini não estiver configurada, o sistema entra no modo:

🔧 MockGeminiModel — IA simulada

Ele retorna:

metas SMART padrão

tabelas simuladas

roadmap

ROI

brief executivo


Permitindo testes 100% offline.


---

🖥️ Prints do Sistema (adicione aqui)

![Tela Inicial](docs/screenshot1.png)
![Metas SMART](docs/screenshot2.png)
![Mapa de Sistemas](docs/screenshot3.png)
![ROI](docs/screenshot4.png)
![Roadmap](docs/screenshot5.png)
![Brief Executivo](docs/screenshot6.png)


---

🛠️ Tecnologias Utilizadas

Flask — Backend leve e rápido

Bootstrap 5 — UI responsiva

Bootstrap Icons — Ícones modernos

Gemini 2.0/2.5 — IA generativa integrada

Mock AI — fallback automático

HTML Semântico + Components


📌 Próximos Passos (Roadmap interno)

[ ] Criar sistema de login (admin/user)

[ ] Exportação nativa para PDF

[ ] Dashboard com históricos de diagnósticos

[ ] Plugin para VS Code (gerar briefs corporativos)

[ ] Versão SaaS com multiclientes


👨‍💻 Autor

Desenvolvido por InNovaIdeia Assessoria em Tecnologia ®

<div align="center">
  <sub>
    <div class="footer">
        <p>Desenvolvido por Dione Castro Alves | © 2025 InNovaIdeia</p>
        <p><a href="https://innovaideia-github-io.vercel.app" target="_blank">Visite meu portfólio</a></p>
    </div>
  </sub>
</div>
```
