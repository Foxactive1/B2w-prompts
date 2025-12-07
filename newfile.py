"""
MVP Flask + Bootstrap — Diagnóstico de 10 Dias
Versão com API Gemini AI Integrada

Como usar:
1. Crie um virtualenv: python -m venv venv
2. Ative e instale: pip install flask google-generativeai python-dotenv
3. Crie um arquivo .env com: GEMINI_API_KEY=sua_chave_aqui
4. Execute: python app.py
5. Abra: http://127.0.0.1:5000
"""

from flask import Flask, request, render_template_string, redirect, url_for, session
from datetime import datetime
import re
import os
import google.generativeai as genai
from markupsafe import escape
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('.env')

app = Flask(__name__)
app.secret_key = 'diagnostico10dias_innovaideia_2024'

# Configurar Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-pro')
    GEMINI_ENABLED = True
else:
    GEMINI_ENABLED = False
    print("⚠️  Gemini API Key não encontrada. Configure GEMINI_API_KEY no arquivo .env")

BOOTSTRAP_CDN = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
ICONS_CDN = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"

# Rodapé Universal InNovaIdeia (HTML)
INNOVA_FOOTER = '''
<div class="footer mt-5 pt-4 border-top text-center text-muted">
  <p><i class="bi bi-c-circle"></i> {year} InNovaIdeia ® | Desenvolvido por Dione Castro Alves</p>
  <p><a href="https://innovaideia-github-io.vercel.app" target="_blank" class="text-decoration-none">
    <i class="bi bi-box-arrow-up-right"></i> Visite meu portfólio
  </a></p>
</div>
'''.format(year=datetime.now().year)

# BASE_HTML permanece igual
BASE_HTML_TEMPLATE = '''
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="{bootstrap_cdn}" rel="stylesheet">
    <link href="{icons_cdn}" rel="stylesheet">
    <title>Diagnóstico 10 Dias — InNovaIdeia</title>
    <style>
      body {{
        padding-top: 70px;
        background-color: #f8f9fa;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      }}
      .navbar-brand {{
        font-weight: 600;
      }}
      .card-compact {{
        border-radius: 16px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
      }}
      .card-compact:hover {{
        transform: translateY(-5px);
      }}
      .form-control:focus, .form-select:focus {{
        border-color: #6c63ff;
        box-shadow: 0 0 0 0.25rem rgba(108, 99, 255, 0.25);
      }}
      .btn-primary {{
        background-color: #6c63ff;
        border-color: #6c63ff;
        padding: 10px 24px;
        font-weight: 500;
      }}
      .btn-primary:hover {{
        background-color: #554fd8;
        border-color: #554fd8;
      }}
      .footer p {{
        margin: 0;
        font-size: 0.9rem;
      }}
      .step-indicator {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 40px;
        position: relative;
      }}
      .step-indicator::before {{
        content: '';
        position: absolute;
        top: 15px;
        left: 0;
        right: 0;
        height: 2px;
        background-color: #e0e0e0;
        z-index: 1;
      }}
      .step {{
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        z-index: 2;
        flex: 1;
      }}
      .step-number {{
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background-color: #e0e0e0;
        color: #666;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-bottom: 8px;
        font-size: 14px;
      }}
      .step.active .step-number {{
        background-color: #6c63ff;
        color: white;
      }}
      .step-label {{
        font-size: 12px;
        text-align: center;
        color: #666;
        max-width: 100px;
      }}
      .step.active .step-label {{
        color: #6c63ff;
        font-weight: 500;
      }}
      .required::after {{
        content: " *";
        color: #dc3545;
      }}
      .opportunity-card {{
        border-left: 4px solid;
        height: 100%;
      }}
      .opportunity-high {{
        border-left-color: #dc3545;
      }}
      .opportunity-medium {{
        border-left-color: #ffc107;
      }}
      .opportunity-low {{
        border-left-color: #28a745;
      }}
      .roi-badge {{
        font-size: 0.85em;
        padding: 4px 10px;
        border-radius: 20px;
      }}
      @media print {{
        .no-print {{
          display: none !important;
        }}
        body {{
          padding-top: 0;
        }}
        .card-compact {{
          box-shadow: none !important;
          border: 1px solid #ddd !important;
        }}
      }}
      .ai-badge {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 0.75em;
        padding: 2px 8px;
        border-radius: 12px;
        display: inline-block;
        margin-left: 5px;
      }}
      .loading-spinner {{
        display: none;
        width: 1.5rem;
        height: 1.5rem;
        border: 0.25em solid currentColor;
        border-right-color: transparent;
        border-radius: 50%;
        animation: spinner 0.75s linear infinite;
      }}
      @keyframes spinner {{
        to {{ transform: rotate(360deg); }}
      }}
    </style>
  </head>
  <body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top no-print">
      <div class="container-fluid">
        <a class="navbar-brand" href="/">
          <i class="bi bi-clipboard2-pulse me-2"></i>Diagnóstico 10 Dias
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navMenu">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <a class="nav-link" href="/">
                <i class="bi bi-house-door me-1"></i>Home
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/scope">
                <i class="bi bi-list-task me-1"></i>Escopo
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/map">
                <i class="bi bi-diagram-3 me-1"></i>Sistemas
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/roi">
                <i class="bi bi-currency-exchange me-1"></i>ROI
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/roadmap">
                <i class="bi bi-map me-1"></i>Roadmap
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/brief">
                <i class="bi bi-file-earmark-text me-1"></i>Brief
              </a>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <main class="container py-4">
      <!-- Step Indicator -->
      <div class="step-indicator no-print">
        <div class="step {step1}">
          <div class="step-number">1</div>
          <div class="step-label">Dados do Cliente</div>
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

      {content}
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
      // Função para gerar PDF (simplificada - usa impressão)
      function downloadPDF() {{
        window.print();
      }}

      // Validação básica do formulário
      document.addEventListener('DOMContentLoaded', function() {{
        const form = document.getElementById('clientForm');
        if (form) {{
          form.addEventListener('submit', function(e) {{
            let valid = true;
            const required = form.querySelectorAll('[required]');
            
            required.forEach(field => {{
              if (!field.value.trim()) {{
                valid = false;
                field.classList.add('is-invalid');
              }} else {{
                field.classList.remove('is-invalid');
              }}
            }});
            
            if (!valid) {{
              e.preventDefault();
              alert('Por favor, preencha todos os campos obrigatórios.');
            }}
          }});
        }}

        // Configurar botões de geração com Gemini
        const geminiButtons = document.querySelectorAll('.btn-gemini');
        geminiButtons.forEach(button => {{
          button.addEventListener('click', function(e) {{
            const spinner = this.querySelector('.loading-spinner');
            const icon = this.querySelector('i:not(.loading-spinner)');
            const originalText = this.innerHTML;
            
            // Mostrar spinner
            if (spinner) {{
              spinner.style.display = 'inline-block';
              if (icon) icon.style.display = 'none';
            }}
            this.disabled = true;
            this.innerHTML = this.innerHTML.replace('Gerar com Gemini', 'Gerando...');
            
            // Simular delay para feedback visual
            setTimeout(() => {{
              if (spinner) {{
                spinner.style.display = 'none';
                if (icon) icon.style.display = 'inline-block';
              }}
              this.innerHTML = originalText;
              this.disabled = false;
              this.classList.remove('btn-warning');
              this.classList.add('btn-success');
              this.innerHTML = this.innerHTML.replace('Gerar com Gemini', '<i class="bi bi-check-circle me-1"></i>Gerado');
            }}, 2000);
          }});
        }});
      }});
    </script>
  </body>
</html>
'''

# ---------- Helper Functions ----------

def get_step_classes(current_step):
    """Retorna classes CSS para o indicador de passos"""
    steps = ['home', 'scope', 'map', 'roi', 'roadmap', 'brief']
    current_index = steps.index(current_step) if current_step in steps else 0
    
    classes = {}
    for i in range(1, 7):  # steps 1 a 6
        if i <= (current_index + 1):
            classes[f'step{i}'] = 'active'
        else:
            classes[f'step{i}'] = ''
    
    return classes

def render_page(title, body_html, current_step='home'):
    """Renderiza uma página completa"""
    step_classes = get_step_classes(current_step)
    
    # Formatar a página completa
    html_content = BASE_HTML_TEMPLATE.format(
        bootstrap_cdn=BOOTSTRAP_CDN,
        icons_cdn=ICONS_CDN,
        content=body_html,
        **step_classes
    )
    
    return render_template_string(html_content)

def generate_with_gemini(prompt, temperature=0.7):
    """Gera conteúdo usando a API do Gemini AI"""
    if not GEMINI_ENABLED:
        return None
    
    try:
        response = gemini_model.generate_content(
            prompt,
            generation_config={
                'temperature': temperature,
                'top_p': 0.8,
                'top_k': 40,
            }
        )
        return response.text
    except Exception as e:
        print(f"Erro ao gerar com Gemini: {e}")
        return None

def generate_smart_goals(data):
    """Gera metas SMART personalizadas com Gemini"""
    prompt = f"""Como consultor especializado em diagnóstico empresarial, crie 5 metas SMART específicas para um cliente com as seguintes características:

Cliente: {data['client_name']}
Setor: {data['industry']}
Tamanho: {data['company_size']}
Área de foco: {data['area']}
Objetivo principal: {data['objective']}
Contexto: {data['context']}

As metas devem ser:
1. Específicas para o setor e problema mencionado
2. Mensuráveis com indicadores claros
3. Atingíveis dentro do prazo de {data['timeline']} dias
4. Relevantes para o objetivo principal
5. Temporizáveis com marcos claros

Formate a resposta como uma lista numerada, cada meta em uma linha, em português do Brasil."""
    
    result = generate_with_gemini(prompt)
    if result:
        return [goal.strip() for goal in result.split('\n') if goal.strip() and goal.strip()[0].isdigit()]
    else:
        # Fallback se Gemini não estiver disponível
        return [
            f"Identificar as 3 principais causas-raiz relacionadas a '{data['area']}' em 10 dias úteis",
            f"Quantificar o impacto financeiro atual do problema (em R$) até o 5º dia do diagnóstico",
            f"Definir métricas de sucesso claras para medir o progresso em {data['timeline']} dias",
            f"Entregar um roadmap acionável com priorização baseada em ROI até o 10º dia",
            f"Validar as hipóteses com stakeholders chave e ajustar recomendações conforme feedback"
        ]

def generate_systems_map(data):
    """Gera análise de sistemas com Gemini"""
    prompt = f"""Como arquiteto de sistemas, analise os possíveis sistemas envolvidos no problema do cliente:

Cliente: {data['client_name']}
Setor: {data['industry']}
Problema: {data['area']}
Contexto: {data['context']}

Faça uma análise incluindo:
1. Sistemas provavelmente envolvidos (CRM, ERP, etc.)
2. Pontos de integração críticos
3. Gargalos típicos do setor {data['industry']}
4. Recomendações de integração

Formate como HTML básico com títulos e listas."""
    
    result = generate_with_gemini(prompt, temperature=0.8)
    if result:
        return result
    else:
        return """
        <div class="alert alert-info">
          <h6><i class="bi bi-info-circle me-2"></i>Análise de Sistemas</h6>
          <p>Para uma análise detalhada dos sistemas, configure a chave da API Gemini no arquivo .env</p>
          <p>Setor identificado: <strong>{}</strong></p>
        </div>
        """.format(data['industry'])

def generate_roi_analysis(data):
    """Gera análise de ROI com Gemini"""
    prompt = f"""Como analista financeiro, crie uma análise de ROI (Return on Investment) para:

Cliente: {data['client_name']}
Setor: {data['industry']}
Problema: {data['area']}
Objetivo: {data['objective']}
Contexto: {data['context']}
Faturamento anual: {data.get('annual_revenue', 'Não informado')}

Forneça:
1. Oportunidades de economia/geração de receita
2. Estimativas de investimento necessário
3. ROI potencial em 12 meses
4. Impacto nos indicadores-chave do setor {data['industry']}

Formate como HTML com classes Bootstrap básicas."""
    
    result = generate_with_gemini(prompt, temperature=0.6)
    if result:
        return result
    else:
        return """
        <div class="alert alert-info">
          <h6><i class="bi bi-currency-exchange me-2"></i>Análise de ROI</h6>
          <p>Configure a API do Gemini para obter uma análise personalizada de ROI.</p>
        </div>
        """

def generate_roadmap(data):
    """Gera roadmap estratégico com Gemini"""
    prompt = f"""Como gerente de projetos, crie um roadmap 30-60-90 dias para:

Cliente: {data['client_name']}
Setor: {data['industry']}
Prazo desejado: {data['timeline']} dias
Objetivo: {data['objective']}
Contexto: {data['context']}

Estruture em:
1. Fase 1 (0-30 dias): Ações de diagnóstico e priorização
2. Fase 2 (31-60 dias): Implementações rápidas
3. Fase 3 (61-90 dias): Otimizações e escalabilidade
4. Métricas de sucesso para cada fase

Formate como HTML com timeline visual."""
    
    result = generate_with_gemini(prompt, temperature=0.7)
    if result:
        return result
    else:
        return """
        <div class="alert alert-info">
          <h6><i class="bi bi-map me-2"></i>Roadmap Estratégico</h6>
          <p>Roadmap personalizado disponível com a integração do Gemini AI.</p>
        </div>
        """

def generate_executive_brief(data):
    """Gera brief executivo com Gemini"""
    prompt = f"""Crie um brief executivo profissional para o diagnóstico:

CLIENTE: {data['client_name']}
SETOR: {data['industry']}
TAMANHO: {data['company_size']}
PROBLEMA PRINCIPAL: {data['area']}
OBJETIVO: {data['objective']}
CONTEXTO: {data['context']}
DATA: {datetime.now().strftime('%d de %B de %Y')}

Inclua:
1. Resumo executivo
2. Diagnóstico principal
3. Oportunidades identificadas
4. Recomendações prioritárias
5. Próximos passos

Formate como documento executivo em português do Brasil."""
    
    result = generate_with_gemini(prompt, temperature=0.5)
    if result:
        return result
    else:
        return f"""
        <h3>{data['client_name']} — Brief Executivo</h3>
        <p class="text-muted">Diagnóstico Estratégico de 10 Dias | {datetime.now().strftime('%d de %B de %Y')}</p>
        <div class="alert alert-warning">
          <h6><i class="bi bi-exclamation-triangle me-2"></i>Brief Base</h6>
          <p>Para um brief executivo personalizado com IA, configure a API do Gemini.</p>
        </div>
        """

# ---------- HOME_BODY ----------

HOME_BODY = '''
<div class="row">
  <div class="col-lg-8 mx-auto">
    <div class="card card-compact p-4 mb-4">
      <div class="text-center mb-4">
        <h4><i class="bi bi-clipboard2-plus text-primary me-2"></i>Novo Diagnóstico</h4>
        <p class="text-muted">Preencha os dados do cliente para gerar um diagnóstico completo</p>
        {% if GEMINI_ENABLED %}
        <span class="ai-badge"><i class="bi bi-cpu me-1"></i>Gemini AI Ativo</span>
        {% else %}
        <span class="badge bg-warning text-dark"><i class="bi bi-exclamation-triangle me-1"></i>Gemini AI Não Configurado</span>
        {% endif %}
      </div>
      
      <form method="post" action="/create" id="clientForm">
        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label required">Nome do Cliente</label>
            <input class="form-control" name="client_name" required 
                   placeholder="Empresa ABC Ltda">
          </div>
          
          <div class="col-md-6 mb-3">
            <label class="form-label">Contato Responsável</label>
            <input class="form-control" name="contact"
                   placeholder="Nome do gestor/diretor">
          </div>
        </div>
        
        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label required">Setor/Indústria</label>
            <select class="form-select" name="industry" required>
              <option value="">Selecione...</option>
              <option value="varejo">Varejo</option>
              <option value="servicos">Serviços</option>
              <option value="industria">Indústria</option>
              <option value="tecnologia">Tecnologia</option>
              <option value="saude">Saúde</option>
              <option value="educacao">Educação</option>
              <option value="financeiro">Financeiro</option>
            </select>
          </div>
          
          <div class="col-md-6 mb-3">
            <label class="form-label required">Tamanho da Empresa</label>
            <select class="form-select" name="company_size" required>
              <option value="">Selecione...</option>
              <option value="pequena">Pequena (1-50 funcionários)</option>
              <option value="media">Média (51-500 funcionários)</option>
              <option value="grande">Grande (501+ funcionários)</option>
            </select>
          </div>
        </div>
        
        <div class="mb-3">
          <label class="form-label required">Área Foco / Problema Principal</label>
          <input class="form-control" name="area" required
                 placeholder="ex: Otimização da cadeia de suprimentos, Redução de CAC...">
        </div>
        
        <div class="mb-3">
          <label class="form-label required">Contexto e Dados Relevantes</label>
          <textarea class="form-control" name="context" rows="4" required
                    placeholder="Informe dados quantitativos e qualitativos relevantes. Exemplo:
• Faturamento anual: R$ 5.000.000
• Custo atual com problema: R$ 500.000/ano
• Tempo médio do processo: 8 horas
• Principais gargalos: falta de integração entre sistemas"></textarea>
          <div class="form-text">
            <i class="bi bi-info-circle me-1"></i>
            Use marcadores (•) para separar os itens. Quanto mais específico, melhores as análises.
          </div>
        </div>
        
        <div class="mb-3">
          <label class="form-label required">Objetivo Principal</label>
          <input class="form-control" name="objective" required
                 placeholder="ex: Reduzir custo operacional em 15% nos próximos 6 meses">
          <div class="form-text">
            <i class="bi bi-lightning me-1"></i>
            Formule como objetivo SMART (Específico, Mensurável, Atingível, Relevante, Temporizável)
          </div>
        </div>
        
        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label">Faturamento Anual (opcional)</label>
            <div class="input-group">
              <span class="input-group-text">R$</span>
              <input type="number" class="form-control" name="annual_revenue" 
                     placeholder="5.000.000" step="1000">
              <span class="input-group-text">,00</span>
            </div>
          </div>
          
          <div class="col-md-6 mb-3">
            <label class="form-label">Prazo Desejado</label>
            <select class="form-select" name="timeline">
              <option value="30">30 dias</option>
              <option value="60" selected>60 dias</option>
              <option value="90">90 dias</option>
              <option value="180">6 meses</option>
            </select>
          </div>
        </div>
        
        <div class="alert alert-info mt-4">
          <h6><i class="bi bi-shield-check me-2"></i>Segurança dos Dados</h6>
          <p class="mb-0 small">Todas as informações são mantidas apenas durante sua sessão e não são armazenadas permanentemente.</p>
        </div>
        
        <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
          <button type="reset" class="btn btn-outline-secondary me-2">
            <i class="bi bi-arrow-clockwise"></i> Limpar
          </button>
          <button type="submit" class="btn btn-primary">
            <i class="bi bi-rocket-takeoff me-2"></i> Gerar Diagnóstico
          </button>
        </div>
      </form>
    </div>
    
    <div class="card card-compact p-4">
      <h5><i class="bi bi-question-circle text-primary me-2"></i>Como Funciona</h5>
      <div class="row">
        <div class="col-md-4 mb-3">
          <div class="text-center p-3">
            <div class="bg-primary bg-opacity-10 rounded-circle d-inline-flex p-3 mb-2">
              <i class="bi bi-clipboard-data text-primary fs-4"></i>
            </div>
            <h6>1. Dados</h6>
            <p class="small text-muted mb-0">Coleta de informações do cliente e contexto do problema</p>
          </div>
        </div>
        <div class="col-md-4 mb-3">
          <div class="text-center p-3">
            <div class="bg-primary bg-opacity-10 rounded-circle d-inline-flex p-3 mb-2">
              <i class="bi bi-bar-chart text-primary fs-4"></i>
            </div>
            <h6>2. Análise IA</h6>
            <p class="small text-muted mb-0">Gemini AI analisa dados e gera insights personalizados</p>
          </div>
        </div>
        <div class="col-md-4 mb-3">
          <div class="text-center p-3">
            <div class="bg-primary bg-opacity-10 rounded-circle d-inline-flex p-3 mb-2">
              <i class="bi bi-map text-primary fs-4"></i>
            </div>
            <h6>3. Plano</h6>
            <p class="small text-muted mb-0">Roadmap executivo com ações 30-60-90 dias</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
'''

@app.route('/')
def home():
    session.clear()
    # Passar variável para template saber se Gemini está ativo
    home_body_with_gemini = HOME_BODY.replace('{% if GEMINI_ENABLED %}', 
                                              f'{{% if {str(GEMINI_ENABLED).lower()} %}}')
    return render_page('Diagnóstico 10 Dias — Início', home_body_with_gemini, 'home')

@app.route('/create', methods=['POST'])
def create():
    required_fields = ['client_name', 'industry', 'company_size', 'area', 'context', 'objective']
    missing_fields = []
    
    for field in required_fields:
        if not request.form.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        error_html = f'''
        <div class="alert alert-danger">
          <h5><i class="bi bi-exclamation-triangle me-2"></i>Campos Obrigatórios</h5>
          <p>Os seguintes campos são obrigatórios:</p>
          <ul>
            {''.join(f'<li>{field.replace("_", " ").title()}</li>' for field in missing_fields)}
          </ul>
          <a href="/" class="btn btn-sm btn-outline-danger">Voltar ao Formulário</a>
        </div>
        '''
        return render_page('Erro de Validação', error_html, 'home')
    
    session['client_data'] = {
        'client_name': escape(request.form.get('client_name')),
        'contact': escape(request.form.get('contact', '')),
        'industry': request.form.get('industry'),
        'company_size': request.form.get('company_size'),
        'area': escape(request.form.get('area')),
        'context': escape(request.form.get('context')),
        'objective': escape(request.form.get('objective')),
        'annual_revenue': request.form.get('annual_revenue'),
        'timeline': request.form.get('timeline', '60'),
        'created_at': datetime.now().strftime('%d/%m/%Y %H:%M')
    }
    
    return redirect(url_for('scope'))

@app.route('/scope')
def scope():
    if 'client_data' not in session:
        return redirect('/')
    
    data = session['client_data']
    
    # Gerar metas SMART com Gemini
    smart_goals = generate_smart_goals(data)
    
    body = f"""
    <div class="mb-4">
      <div class="d-flex justify-content-between align-items-start">
        <div>
          <h5 class="mb-1">Escopo do Diagnóstico</h5>
          <p class="text-muted mb-0">Cliente: <strong>{data['client_name']}</strong></p>
        </div>
        <span class="badge bg-primary fs-6">{data['timeline']} dias</span>
      </div>
      <div class="mt-2">
        <button class="btn btn-sm btn-warning btn-gemini" id="regenerateScope">
          <i class="bi bi-arrow-clockwise me-1"></i>Regenerar com Gemini
          <span class="loading-spinner ms-1"></span>
        </button>
      </div>
    </div>
    
    <div class="card card-compact p-4 mb-4">
      <h6><i class="bi bi-check-circle me-2"></i>Metas SMART Geradas por IA</h6>
      <ol class="mb-0">
        {''.join(f'<li class="mb-2">{goal}</li>' for goal in smart_goals)}
      </ol>
    </div>
    
    <div class="d-flex justify-content-between no-print">
      <a href="/" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left me-1"></i> Voltar
      </a>
      <a href="/map" class="btn btn-primary">
        Próximo: Mapa de Sistemas <i class="bi bi-arrow-right ms-1"></i>
      </a>
    </div>
    """
    
    return render_page('Escopo do Diagnóstico', body, 'scope')

@app.route('/map')
def map_systems():
    if 'client_data' not in session:
        return redirect('/')
    
    data = session['client_data']
    
    # Gerar análise de sistemas com Gemini
    systems_analysis = generate_systems_map(data)
    
    body = f"""
    <div class="mb-4">
      <div class="d-flex justify-content-between align-items-start">
        <h5>Mapa de Sistemas Atual</h5>
        <button class="btn btn-sm btn-warning btn-gemini" id="regenerateSystems">
          <i class="bi bi-arrow-clockwise me-1"></i>Analisar com Gemini
          <span class="loading-spinner ms-1"></span>
        </button>
      </div>
      <p class="text-muted mb-0">Análise dos fluxos atuais e identificação de gargalos</p>
    </div>
    
    <div class="card card-compact p-4 mb-4">
      {systems_analysis}
    </div>
    
    <div class="d-flex justify-content-between mt-4 no-print">
      <a href="/scope" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left me-1"></i> Voltar
      </a>
      <a href="/roi" class="btn btn-primary">
        Próximo: Análise de ROI <i class="bi bi-arrow-right ms-1"></i>
      </a>
    </div>
    """
    
    return render_page('Mapa de Sistemas', body, 'map')

@app.route('/roi')
def roi():
    if 'client_data' not in session:
        return redirect('/')
    
    data = session['client_data']
    
    # Gerar análise de ROI com Gemini
    roi_analysis = generate_roi_analysis(data)
    
    body = f"""
    <div class="mb-4">
      <div class="d-flex justify-content-between align-items-start">
        <h5>Mapa de Calor de ROI</h5>
        <button class="btn btn-sm btn-warning btn-gemini" id="regenerateROI">
          <i class="bi bi-arrow-clockwise me-1"></i>Calcular com Gemini
          <span class="loading-spinner ms-1"></span>
        </button>
      </div>
      <p class="text-muted">Priorização de oportunidades baseada em impacto e viabilidade</p>
    </div>
    
    <div class="card card-compact p-4 mb-4">
      {roi_analysis}
    </div>
    
    <div class="d-flex justify-content-between mt-4 no-print">
      <a href="/map" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left me-1"></i> Voltar
      </a>
      <a href="/roadmap" class="btn btn-primary">
        Próximo: Roadmap <i class="bi bi-arrow-right ms-1"></i>
      </a>
    </div>
    """
    
    return render_page('Mapa de Calor (ROI)', body, 'roi')

@app.route('/roadmap')
def roadmap():
    if 'client_data' not in session:
        return redirect('/')
    
    data = session['client_data']
    
    # Gerar roadmap com Gemini
    roadmap_content = generate_roadmap(data)
    
    body = f"""
    <div class="mb-4">
      <div class="d-flex justify-content-between align-items-start">
        <h5>Roadmap Estratégico</h5>
        <button class="btn btn-sm btn-warning btn-gemini" id="regenerateRoadmap">
          <i class="bi bi-arrow-clockwise me-1"></i>Gerar com Gemini
          <span class="loading-spinner ms-1"></span>
        </button>
      </div>
      <p class="text-muted">Opções de implementação com diferentes níveis de investimento e risco</p>
    </div>
    
    <div class="card card-compact p-4 mb-4">
      {roadmap_content}
    </div>
    
    <div class="d-flex justify-content-between mt-4 no-print">
      <a href="/roi" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left me-1"></i> Voltar
      </a>
      <a href="/brief" class="btn btn-primary">
        Próximo: Brief Executivo <i class="bi bi-arrow-right ms-1"></i>
      </a>
    </div>
    """
    
    return render_page('Roadmap 30-60-90', body, 'roadmap')

@app.route('/brief')
def brief():
    if 'client_data' not in session:
        return redirect('/')
    
    data = session['client_data']
    
    # Gerar brief executivo com Gemini
    brief_content = generate_executive_brief(data)
    
    body = f"""
    <div class="mb-4">
      <div class="text-center">
        {brief_content}
      </div>
      <div class="text-center mt-3">
        <button class="btn btn-warning btn-gemini" id="regenerateBrief">
          <i class="bi bi-magic me-1"></i>Reescrever com Gemini
          <span class="loading-spinner ms-1"></span>
        </button>
      </div>
    </div>
    
    <div class="d-flex justify-content-between mt-4 no-print">
      <a href="/roadmap" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left me-1"></i> Voltar
      </a>
      <div>
        <button onclick="window.print()" class="btn btn-success me-2">
          <i class="bi bi-printer me-1"></i> Imprimir Brief
        </button>
        <a href="/" class="btn btn-primary">
          <i class="bi bi-plus-circle me-1"></i> Novo Diagnóstico
        </a>
      </div>
    </div>
    """
    
    return render_page('Brief Executivo', body, 'brief')

# ---------- API Endpoint para regeneração ----------
@app.route('/api/regenerate', methods=['POST'])
def api_regenerate():
    """Endpoint para regenerar conteúdo com Gemini"""
    if 'client_data' not in session:
        return {'error': 'Dados do cliente não encontrados'}, 400
    
    data = session['client_data']
    section = request.json.get('section')
    
    if not section:
        return {'error': 'Seção não especificada'}, 400
    
    if not GEMINI_ENABLED:
        return {'error': 'Gemini AI não configurado'}, 503
    
    try:
        if section == 'scope':
            content = generate_smart_goals(data)
            return {'content': '<ol>' + ''.join(f'<li>{goal}</li>' for goal in content) + '</ol>'}
        elif section == 'map':
            content = generate_systems_map(data)
            return {'content': content}
        elif section == 'roi':
            content = generate_roi_analysis(data)
            return {'content': content}
        elif section == 'roadmap':
            content = generate_roadmap(data)
            return {'content': content}
        elif section == 'brief':
            content = generate_executive_brief(data)
            return {'content': content}
        else:
            return {'error': 'Seção inválida'}, 400
    except Exception as e:
        return {'error': str(e)}, 500

# ---------- Run ----------
if __name__ == '__main__':
    app.run(debug=True, port=5000)