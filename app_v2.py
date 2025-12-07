"""
MVP Flask + Bootstrap — Diagnóstico de 10 Dias (InNovaIdeia)
Versão: MVP 1.1 - Modelo Gemini Flash Latest

Instruções:
1. Instale: pip install flask google-generativeai python-dotenv
2. Configure seu .env com GEMINI_API_KEY=...
3. Execute: python app.py
"""

from flask import Flask, request, render_template_string, redirect, url_for, session, jsonify
from datetime import datetime
import os
import google.generativeai as genai
from markupsafe import escape
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('.env')

app = Flask(__name__)
# Em produção, use uma chave aleatória fixa
app.secret_key = os.getenv('SECRET_KEY', 'diagnostico_innovaideia_dev_secret')

# Configurar Gemini AI
#GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

GEMINI_API_KEY="AIzaSyAIqqiDHdJDw9To5PMBT9W9pvAdOey7LdY"
GEMINI_ENABLED = False

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # ---------------------------------------------------------
        # ATUALIZAÇÃO: Usando o modelo 'gemini-1.5-flash-latest'
        # Isso garante o uso da versão mais recente e otimizada.
        # ---------------------------------------------------------
        gemini_model = genai.GenerativeModel('gemini-pro')
        
        GEMINI_ENABLED = True
        print(f"✅ Gemini API Configurada. Modelo: gemini-pro")
    except Exception as e:
        print(f"⚠️ Erro ao configurar Gemini: {e}")
else:
    print("⚠️ Gemini API Key não encontrada no .env")

BOOTSTRAP_CDN = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
ICONS_CDN = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"

# ==========================================
# TEMPLATES HTML (Modularizados via String)
# ==========================================

BASE_HTML_TEMPLATE = '''
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Diagnóstico 10 Dias — InNovaIdeia</title>
    <link href="{bootstrap_cdn}" rel="stylesheet">
    <link href="{icons_cdn}" rel="stylesheet">
    <style>
      :root {{
        --primary-color: #6c63ff;
        --secondary-color: #2c3e50;
        --bg-color: #f8f9fa;
      }}
      body {{
        padding-top: 70px;
        background-color: var(--bg-color);
        font-family: 'Segoe UI', system-ui, sans-serif;
        color: var(--secondary-color);
      }}
      /* Navbar */
      .navbar-dark.bg-dark {{
        background-color: var(--secondary-color) !important;
      }}
      .card-compact {{
        border: none;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        background: white;
        transition: transform 0.2s;
      }}
      .step-indicator {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 40px;
        position: relative;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
      }}
      .step-indicator::before {{
        content: '';
        position: absolute;
        top: 15px;
        left: 0;
        right: 0;
        height: 2px;
        background-color: #e9ecef;
        z-index: 1;
      }}
      .step {{
        position: relative;
        z-index: 2;
        text-align: center;
        background: var(--bg-color);
        padding: 0 10px;
      }}
      .step-number {{
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background-color: #e9ecef;
        color: #adb5bd;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin: 0 auto 8px;
        transition: all 0.3s;
      }}
      .step.active .step-number {{
        background-color: var(--primary-color);
        color: white;
        transform: scale(1.1);
      }}
      .step-label {{ font-size: 0.75rem; color: #adb5bd; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
      .step.active .step-label {{ color: var(--primary-color); }}
      
      /* Utilities */
      .loading-spinner {{
        display: none;
        width: 1rem;
        height: 1rem;
        border: 2px solid currentColor;
        border-right-color: transparent;
        border-radius: 50%;
        animation: spinner .75s linear infinite;
      }}
      @keyframes spinner {{ to {{ transform: rotate(360deg); }} }}
      
      /* Print Styles */
      @media print {{
        .no-print {{ display: none !important; }}
        body {{ padding-top: 0; background: white; }}
        .card-compact {{ box-shadow: none; border: 1px solid #ddd; }}
        .container {{ max-width: 100%; }}
        a {{ text-decoration: none; color: black; }}
      }}
    </style>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top no-print">
      <div class="container">
        <a class="navbar-brand fw-bold" href="/">
          <i class="bi bi-clipboard2-pulse me-2"></i>InNovaIdeia
        </a>
        <div class="collapse navbar-collapse">
          <ul class="navbar-nav ms-auto small">
            <li class="nav-item"><a class="nav-link" href="/"><i class="bi bi-house me-1"></i>Início</a></li>
            <li class="nav-item"><a class="nav-link" href="/brief"><i class="bi bi-file-text me-1"></i>Relatório Final</a></li>
          </ul>
        </div>
      </div>
    </nav>

    <main class="container py-4">
      <div class="step-indicator no-print">
        <div class="step {step1}">
          <div class="step-number">1</div>
          <div class="step-label">Dados</div>
        </div>
        <div class="step {step2}">
          <div class="step-number">2</div>
          <div class="step-label">Escopo</div>
        </div>
        <div class="step {step3}">
          <div class="step-number">3</div>
          <div class="step-label">Sistemas</div>
        </div>
        <div class="step {step4}">
          <div class="step-number">4</div>
          <div class="step-label">ROI</div>
        </div>
        <div class="step {step5}">
          <div class="step-number">5</div>
          <div class="step-label">Roadmap</div>
        </div>
        <div class="step {step6}">
          <div class="step-number">6</div>
          <div class="step-label">Brief</div>
        </div>
      </div>

      <div id="alert-area"></div>

      {content}
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
      // Função Genérica para chamar a API Flask -> Gemini
      async function regenerateContent(sectionId, targetDivId, btnElement) {{
        const originalText = btnElement.innerHTML;
        const spinner = btnElement.querySelector('.loading-spinner');
        
        // UI State: Loading
        btnElement.disabled = true;
        if(spinner) spinner.style.display = 'inline-block';
        btnElement.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Gerando IA...';

        try {{
            const response = await fetch('/api/regenerate', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ section: sectionId }})
            }});

            const data = await response.json();

            if (response.ok) {{
                // Atualiza o conteúdo com Fade In
                const target = document.getElementById(targetDivId);
                target.style.opacity = '0';
                setTimeout(() => {{
                    target.innerHTML = data.content;
                    target.style.opacity = '1';
                }}, 200);
            }} else {{
                alert('Erro: ' + (data.error || 'Falha desconhecida'));
            }}

        }} catch (error) {{
            console.error('Erro:', error);
            alert('Erro de conexão com o servidor.');
        }} finally {{
            // Restore UI
            btnElement.disabled = false;
            btnElement.innerHTML = originalText;
            if(spinner) spinner.style.display = 'none';
        }}
      }}

      // Validação de formulários
      document.addEventListener('DOMContentLoaded', () => {{
        const forms = document.querySelectorAll('.needs-validation');
        Array.from(forms).forEach(form => {{
            form.addEventListener('submit', event => {{
                if (!form.checkValidity()) {{
                    event.preventDefault();
                    event.stopPropagation();
                }}
                form.classList.add('was-validated');
            }}, false);
        }});
      }});
    </script>
  </body>
</html>
'''

# ==========================================
# LÓGICA DE IA E PROMPTS
# ==========================================

def clean_ai_response(text):
    """Remove blocos de markdown ```html ou ``` que o Gemini possa retornar"""
    if not text: return ""
    text = text.replace("```html", "").replace("```", "")
    return text.strip()

def generate_with_gemini(prompt, temperature=0.7):
    if not GEMINI_ENABLED:
        return None
    try:
        response = gemini_model.generate_content(
            prompt,
            generation_config={'temperature': temperature}
        )
        return clean_ai_response(response.text)
    except Exception as e:
        print(f"Erro Gemini: {e}")
        return f"<div class='alert alert-danger'>Erro na geração IA: {str(e)}</div>"

# ==========================================
# ROTAS E CONTROLLERS
# ==========================================

def get_step_classes(current_step):
    steps = ['home', 'scope', 'map', 'roi', 'roadmap', 'brief']
    try:
        idx = steps.index(current_step)
    except ValueError:
        idx = 0
    return {f'step{i+1}': 'active' if i <= idx else '' for i in range(6)}

def render_page(body_html, current_step='home'):
    step_classes = get_step_classes(current_step)
    return render_template_string(
        BASE_HTML_TEMPLATE.format(
            bootstrap_cdn=BOOTSTRAP_CDN,
            icons_cdn=ICONS_CDN,
            content=body_html,
            **step_classes
        )
    )

@app.route('/')
def home():
    session.clear()
    body = f'''
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card card-compact p-5">
          <div class="text-center mb-5">
            <h2 class="fw-bold text-primary">Diagnóstico Empresarial IA</h2>
            <p class="text-muted">Gere um plano de transformação de 10 dias em segundos.</p>
            { "" if GEMINI_ENABLED else '<div class="alert alert-warning">⚠️ API Key não configurada. Modo Offline.</div>' }
          </div>
          
          <form method="post" action="/create" class="needs-validation" novalidate>
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label fw-bold">Nome do Cliente</label>
                <input type="text" class="form-control" name="client_name" required placeholder="Ex: TechSolutions Ltda">
              </div>
              <div class="col-md-6">
                <label class="form-label fw-bold">Setor</label>
                <select class="form-select" name="industry" required>
                  <option value="">Selecione...</option>
                  <option value="Varejo">Varejo</option>
                  <option value="Serviços">Serviços</option>
                  <option value="Indústria">Indústria</option>
                  <option value="Tecnologia">Tecnologia</option>
                  <option value="Saúde">Saúde</option>
                  <option value="Logística">Logística</option>
                </select>
              </div>
              
              <div class="col-12">
                <label class="form-label fw-bold">Problema Principal (A "Dor")</label>
                <textarea class="form-control" name="area" rows="2" required 
                  placeholder="Ex: Processo de vendas lento, falta de integração entre marketing e comercial..."></textarea>
              </div>

              <div class="col-12">
                <label class="form-label fw-bold">Contexto & Dados (Opcional mas recomendado)</label>
                <textarea class="form-control" name="context" rows="3" 
                  placeholder="Dados quantitativos ajudam a IA. Ex: Queda de 20% no faturamento; equipe de 50 pessoas..."></textarea>
              </div>
              
               <div class="col-12">
                <label class="form-label fw-bold">Objetivo Esperado</label>
                <input type="text" class="form-control" name="objective" required placeholder="Ex: Aumentar conversão em 15% em 3 meses">
              </div>
            </div>

            <div class="d-grid gap-2 mt-5">
              <button type="submit" class="btn btn-primary btn-lg">
                Inicar Diagnóstico <i class="bi bi-arrow-right ms-2"></i>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    '''
    return render_page(body, 'home')

@app.route('/create', methods=['POST'])
def create():
    session['client_data'] = {
        'client_name': escape(request.form.get('client_name')),
        'industry': request.form.get('industry'),
        'area': escape(request.form.get('area')),
        'context': escape(request.form.get('context', 'Contexto padrão')),
        'objective': escape(request.form.get('objective')),
        'timeline': '60'
    }
    return redirect(url_for('scope'))

@app.route('/scope')
def scope():
    if 'client_data' not in session: return redirect('/')
    
    # Renderização inicial (pode ser vazia ou pré-carregada se quiser)
    # A mágica acontece no botão "Gerar" ou onLoad se preferir. 
    # Aqui vamos carregar via Server Side na primeira vez para simplicidade.
    
    data = session['client_data']
    
    # Prompt Otimizado
    prompt = f"""
    Atue como consultor de negócios sênior. 
    Cliente: {data['client_name']} ({data['industry']}).
    Problema: {data['area']}. Contexto: {data['context']}.
    Crie 5 Metas SMART em formato HTML (lista <ul> com <li> contendo <strong>Meta:</strong> Descrição).
    Não use markdown, apenas tags HTML.
    """
    
    content = generate_with_gemini(prompt) or "<p>IA Indisponível. Defina as metas manualmente.</p>"
    
    body = f"""
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3>🎯 Escopo e Metas</h3>
        <button class="btn btn-outline-primary btn-sm" onclick="regenerateContent('scope', 'scope-content', this)">
            <i class="bi bi-stars me-1"></i>Regenerar IA
        </button>
    </div>
    <div class="card card-compact p-4">
        <div id="scope-content">{content}</div>
    </div>
    <div class="d-flex justify-content-between mt-4 no-print">
        <a href="/" class="btn btn-light">Voltar</a>
        <a href="/map" class="btn btn-primary">Próximo: Mapeamento <i class="bi bi-arrow-right"></i></a>
    </div>
    """
    return render_page(body, 'scope')

@app.route('/map')
def map_systems():
    if 'client_data' not in session: return redirect('/')
    data = session['client_data']
    
    prompt = f"""
    Para uma empresa de {data['industry']} com problema em '{data['area']}',
    crie uma tabela HTML simples (table class='table') listando:
    Sistema Provável | Função | Possível Gargalo.
    Apenas HTML.
    """
    content = generate_with_gemini(prompt) or "<p>Conteúdo indisponível.</p>"

    body = f"""
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3>🧩 Mapa de Sistemas e Gargalos</h3>
        <button class="btn btn-outline-primary btn-sm" onclick="regenerateContent('map', 'map-content', this)">
            <i class="bi bi-stars"></i> Regenerar
        </button>
    </div>
    <div class="card card-compact p-4">
        <div id="map-content">{content}</div>
    </div>
    <div class="d-flex justify-content-between mt-4 no-print">
        <a href="/scope" class="btn btn-light">Voltar</a>
        <a href="/roi" class="btn btn-primary">Próximo: ROI <i class="bi bi-arrow-right"></i></a>
    </div>
    """
    return render_page(body, 'map')

@app.route('/roi')
def roi():
    if 'client_data' not in session: return redirect('/')
    data = session['client_data']
    
    prompt = f"""
    Estime o ROI para resolver '{data['area']}' na indústria {data['industry']}.
    Retorne HTML com:
    1. <h3>Estimativa de Economia/Ganho</h3> (texto curto)
    2. <div class='alert alert-success'> (Destaque do valor potencial)
    3. Lista de benefícios intangíveis.
    """
    content = generate_with_gemini(prompt) or "<p>Conteúdo indisponível.</p>"

    body = f"""
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3>💰 Análise de ROI</h3>
        <button class="btn btn-outline-primary btn-sm" onclick="regenerateContent('roi', 'roi-content', this)">
            <i class="bi bi-stars"></i> Recalcular
        </button>
    </div>
    <div class="card card-compact p-4">
        <div id="roi-content">{content}</div>
    </div>
    <div class="d-flex justify-content-between mt-4 no-print">
        <a href="/map" class="btn btn-light">Voltar</a>
        <a href="/roadmap" class="btn btn-primary">Próximo: Roadmap <i class="bi bi-arrow-right"></i></a>
    </div>
    """
    return render_page(body, 'roi')

@app.route('/roadmap')
def roadmap():
    if 'client_data' not in session: return redirect('/')
    data = session['client_data']
    
    prompt = f"""
    Crie um Roadmap de 3 fases (Curto, Médio, Longo Prazo) para atingir: {data['objective']}.
    Retorne HTML estruturado com cards ou lista bootstrap para cada fase.
    """
    content = generate_with_gemini(prompt) or "<p>Conteúdo indisponível.</p>"

    body = f"""
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3>🚀 Roadmap de Execução</h3>
        <button class="btn btn-outline-primary btn-sm" onclick="regenerateContent('roadmap', 'roadmap-content', this)">
            <i class="bi bi-stars"></i> Regenerar
        </button>
    </div>
    <div class="card card-compact p-4">
        <div id="roadmap-content">{content}</div>
    </div>
    <div class="d-flex justify-content-between mt-4 no-print">
        <a href="/roi" class="btn btn-light">Voltar</a>
        <a href="/brief" class="btn btn-primary">Próximo: Brief Final <i class="bi bi-arrow-right"></i></a>
    </div>
    """
    return render_page(body, 'roadmap')

@app.route('/brief')
def brief():
    if 'client_data' not in session: return redirect('/')
    data = session['client_data']
    
    prompt = f"""
    Escreva um Brief Executivo Profissional (Resumo da Consultoria) para o cliente {data['client_name']}.
    Resuma o problema, a solução proposta e o impacto esperado.
    Use tom formal e persuasivo. Formate com HTML (h2, p, strong).
    """
    content = generate_with_gemini(prompt, temperature=0.5) or "<p>Conteúdo indisponível.</p>"

    body = f"""
    <div class="d-flex justify-content-between align-items-center mb-4 no-print">
        <h3>📄 Brief Executivo Final</h3>
        <div>
            <button class="btn btn-outline-primary btn-sm me-2" onclick="regenerateContent('brief', 'brief-content', this)">
                <i class="bi bi-stars"></i> Reescrever
            </button>
            <button onclick="window.print()" class="btn btn-success btn-sm">
                <i class="bi bi-printer"></i> Imprimir PDF
            </button>
        </div>
    </div>
    
    <div class="card card-compact p-5 mb-5 border-0 shadow-none">
        <div class="text-center mb-5 border-bottom pb-4">
            <h1>Diagnóstico Estratégico</h1>
            <h4 class="text-muted">{data['client_name']}</h4>
            <small class="text-muted">{datetime.now().strftime('%d/%m/%Y')}</small>
        </div>
        
        <div id="brief-content">
            {content}
        </div>
        
        <div class="mt-5 pt-4 border-top text-center text-muted small">
            <p>Gerado via InNovaIdeia AI Diagnosis</p>
        </div>
    </div>
    
    <div class="text-center mb-5 no-print">
        <a href="/" class="btn btn-outline-secondary">Iniciar Novo Diagnóstico</a>
    </div>
    """
    return render_page(body, 'brief')

# ==========================================
# API ENDPOINT (AJAX)
# ==========================================

@app.route('/api/regenerate', methods=['POST'])
def api_regenerate():
    if 'client_data' not in session:
        return jsonify({'error': 'Sessão expirada'}), 401
    
    data = request.json
    section = data.get('section')
    client = session['client_data']
    
    # Roteamento de prompts baseado na seção solicitada
    prompts = {
        'scope': f"Reescreva 5 Metas SMART diferentes para {client['client_name']} focado em {client['objective']}. Use HTML <ul><li>.",
        'map': f"Reanalise os sistemas para setor {client['industry']} focando em inovação. Use HTML Table.",
        'roi': f"Recalcule o ROI para {client['client_name']} sendo mais agressivo/otimista. Use HTML.",
        'roadmap': f"Crie um roadmap alternativo para {client['client_name']} focado em resultados rápidos (Quick Wins). Use HTML.",
        'brief': f"Reescreva o Brief Executivo para {client['client_name']} com tom mais urgente e vendedor. Use HTML."
    }
    
    if section not in prompts:
        return jsonify({'error': 'Seção inválida'}), 400
        
    content = generate_with_gemini(prompts[section])
    
    if content:
        return jsonify({'content': content})
    else:
        return jsonify({'error': 'Falha na geração IA'}), 500

if __name__ == '__main__':
    # Debug=True é ótimo para dev, mas cuidado em produção
    app.run(debug=True, port=5000)
