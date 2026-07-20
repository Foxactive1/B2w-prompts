"""
MVP Flask + Bootstrap — Diagnóstico de 10 Dias (InNovaIdeia)
Versão: MVP 1.5 - Migrado para a Groq API (Llama 3.3)

Instruções:
1. Execute: python app_final.py
"""

from flask import Flask, request, render_template_string, redirect, url_for, session, jsonify
from datetime import datetime
import os
from groq import Groq
from markupsafe import escape
from dotenv import load_dotenv

# ==========================================
# 1. CONFIGURAÇÃO INICIAL
# ==========================================

load_dotenv('.env')
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_change_in_production')

# ==========================================
# 2. CONFIGURAÇÃO DA GROQ API
# ==========================================

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_ENABLED = False
groq_client = None
GROQ_MODEL = None

# Modelos Groq em ordem de prioridade (do mais capaz ao mais rápido/barato).
MODEL_PRIORITY = [
    os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile'),
    'llama-3.3-70b-versatile',
    'llama-3.1-8b-instant',
    'openai/gpt-oss-20b',
]

if GROQ_API_KEY and GROQ_API_KEY.strip():
    try:
        print("🔄 Configurando Groq API...")
        groq_client = Groq(api_key=GROQ_API_KEY)

        # Tentar cada modelo na ordem de prioridade, ignorando duplicatas.
        for model_name in dict.fromkeys(MODEL_PRIORITY):
            try:
                print(f"   Testando: {model_name}...")
                test_response = groq_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "Teste de conexão"}],
                    max_tokens=8,
                )

                if test_response and test_response.choices:
                    GROQ_MODEL = model_name
                    GROQ_ENABLED = True
                    print(f"✅ Modelo selecionado: {model_name}")
                    break
                else:
                    print("   ⚠️ Modelo sem resposta")

            except Exception as model_error:
                error_msg = str(model_error)
                if "rate" in error_msg.lower() or "quota" in error_msg.lower():
                    print(f"   ⚠️ {model_name}: Limite de uso excedido (pulando)")
                elif "not found" in error_msg.lower() or "decommission" in error_msg.lower():
                    print(f"   ⚠️ {model_name}: Não encontrado")
                else:
                    print(f"   ⚠️ {model_name}: {error_msg[:60]}...")
                continue

        if not GROQ_ENABLED:
            print("❌ Nenhum modelo Groq disponível")
            print("💡 Dicas:")
            print("   - Verifique sua chave em https://console.groq.com/keys")
            print("   - Confira os modelos ativos em https://console.groq.com/docs/models")

    except Exception as e:
        print(f"❌ Erro na configuração: {str(e)[:100]}")
        GROQ_ENABLED = False
else:
    print("⚠️ Groq API Key não encontrada no .env")

# Instrução de sistema comum a todas as gerações.
SYSTEM_PROMPT = (
    "Você é um consultor sênior de transformação digital. "
    "Responda sempre em português do Brasil e retorne apenas HTML válido "
    "formatado com classes do Bootstrap 5, sem blocos de código markdown."
)

# ==========================================
# 3. CONFIGURAÇÃO DE FALLBACK (RESPOSTAS SIMULADAS)
# ==========================================

# Respostas simuladas para desenvolvimento (modo offline)
def _mock_response_for(prompt):
        """Gera HTML simulado com base no contexto do prompt."""
        def MockResponse(text):
            return text

        prompt_lower = prompt.lower()
        
        # Respostas simuladas baseadas no contexto
        if "metas smart" in prompt_lower or "scope" in prompt_lower:
            return MockResponse("""
            <div class="alert alert-info">
                <i class="bi bi-lightbulb"></i> <strong>5 Metas SMART para Transformação Digital</strong>
            </div>
            <ul class="list-group list-group-flush">
                <li class="list-group-item"><strong>Meta 1:</strong> Automatizar 80% dos processos manuais em 90 dias, aumentando eficiência em 40%</li>
                <li class="list-group-item"><strong>Meta 2:</strong> Reduzir tempo de resposta ao cliente de 48h para 4h até o final do trimestre</li>
                <li class="list-group-item"><strong>Meta 3:</strong> Implementar sistema integrado de CRM-ERP com ROI positivo em 6 meses</li>
                <li class="list-group-item"><strong>Meta 4:</strong> Aumentar satisfação do cliente de 75% para 90% em 120 dias</li>
                <li class="list-group-item"><strong>Meta 5:</strong> Reduzir custos operacionais em 25% através da digitalização em 180 dias</li>
            </ul>
            """)
        elif "tabela html" in prompt_lower or "sistema" in prompt_lower or "map" in prompt_lower:
            return MockResponse("""
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th><i class="bi bi-gear"></i> Sistema</th>
                            <th><i class="bi bi-cpu"></i> Função</th>
                            <th><i class="bi bi-exclamation-triangle"></i> Gargalo Atual</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>ERP Legado</strong></td>
                            <td>Gestão financeira e operacional</td>
                            <td><span class="badge bg-warning">Integração limitada</span></td>
                        </tr>
                        <tr>
                            <td><strong>CRM Básico</strong></td>
                            <td>Gestão de relacionamento com cliente</td>
                            <td><span class="badge bg-danger">Dados desatualizados</span></td>
                        </tr>
                        <tr>
                            <td><strong>Sistema de Vendas</strong></td>
                            <td>Processamento de pedidos e cobrança</td>
                            <td><span class="badge bg-info">Processo manual intensivo</span></td>
                        </tr>
                        <tr>
                            <td><strong>BI & Analytics</strong></td>
                            <td>Análise de dados e relatórios</td>
                            <td><span class="badge bg-secondary">Falta de integração em tempo real</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """)
        elif "roi" in prompt_lower:
            return MockResponse("""
            <div class="roi-analysis">
                <h4 class="text-success"><i class="bi bi-graph-up-arrow"></i> Estimativa de Retorno sobre Investimento</h4>
                <div class="alert alert-success">
                    <h5 class="alert-heading">💰 Potencial Financeiro</h5>
                    <p><strong>Economia Anual Estimada:</strong> R$ 180.000 - R$ 320.000</p>
                    <p><strong>ROI Esperado:</strong> 45% no primeiro ano, 120% em 3 anos</p>
                    <p><strong>Payback:</strong> 8-14 meses</p>
                </div>
                <h5>📈 Benefícios Intangíveis:</h5>
                <ul>
                    <li><i class="bi bi-check-circle text-success"></i> Redução de 60% em erros manuais</li>
                    <li><i class="bi bi-check-circle text-success"></i> Aumento de 30% na produtividade da equipe</li>
                    <li><i class="bi bi-check-circle text-success"></i> Melhoria de 40% na tomada de decisão</li>
                    <li><i class="bi bi-check-circle text-success"></i> Redução de 70% no tempo de processamento</li>
                </ul>
            </div>
            """)
        elif "roadmap" in prompt_lower:
            return MockResponse("""
            <div class="roadmap-container">
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <div class="card h-100 border-primary">
                            <div class="card-header bg-primary text-white">
                                <h6><i class="bi bi-lightning"></i> Fase 1: Quick Wins (0-30 dias)</h6>
                            </div>
                            <div class="card-body">
                                <ul class="small">
                                    <li>Diagnóstico detalhado de processos</li>
                                    <li>Automatização de relatórios manuais</li>
                                    <li>Integração básica CRM-ERP</li>
                                    <li>Treinamento inicial da equipe</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <div class="card h-100 border-success">
                            <div class="card-header bg-success text-white">
                                <h6><i class="bi bi-rocket"></i> Fase 2: Transformação (31-90 dias)</h6>
                            </div>
                            <div class="card-body">
                                <ul class="small">
                                    <li>Implementação do sistema principal</li>
                                    <li>Migração de dados históricos</li>
                                    <li>Automação de fluxos críticos</li>
                                    <li>Dashboard de KPIs em tempo real</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <div class="card h-100 border-info">
                            <div class="card-header bg-info text-white">
                                <h6><i class="bi bi-stars"></i> Fase 3: Otimização (91-180 dias)</h6>
                            </div>
                            <div class="card-body">
                                <ul class="small">
                                    <li>IA para previsão e análise</li>
                                    <li>Otimização contínua de processos</li>
                                    <li>Expansão para novas áreas</li>
                                    <li>Sistema de aprendizado organizacional</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """)
        elif "brief" in prompt_lower:
            return MockResponse("""
            <div class="brief-executive">
                <h2 class="border-bottom pb-2">📋 Brief Executivo - Transformação Digital</h2>
                
                <div class="alert alert-light border">
                    <h4><i class="bi bi-building"></i> Cliente: [Nome da Empresa]</h4>
                    <p><strong>Setor:</strong> [Indústria] | <strong>Data:</strong> """ + datetime.now().strftime('%d/%m/%Y') + """</p>
                </div>
                
                <h3><i class="bi bi-clipboard2-pulse"></i> Diagnóstico Atual</h3>
                <p>A empresa enfrenta desafios significativos em [área do problema], resultando em [impactos negativos]. 
                Nossa análise identificou processos manuais excessivos, falta de integração sistêmica e oportunidades 
                claras para automação inteligente.</p>
                
                <h3><i class="bi bi-bullseye"></i> Objetivo Principal</h3>
                <p>[Objetivo específico do cliente] através da implementação de soluções tecnológicas estratégicas 
                que otimizem operações, reduzam custos e aumentem a competitividade no mercado.</p>
                
                <h3><i class="bi bi-map"></i> Abordagem Proposta</h3>
                <p>Roadmap de 180 dias dividido em 3 fases: Quick Wins (0-30 dias), Transformação (31-90 dias) 
                e Otimização (91-180 dias), garantindo resultados incrementais e ROI progressivo.</p>
                
                <h3><i class="bi bi-graph-up"></i> Impacto Esperado</h3>
                <ul>
                    <li><strong>Econômico:</strong> Economia anual de R$ 180K-320K</li>
                    <li><strong>Operacional:</strong> Aumento de 40% na eficiência</li>
                    <li><strong>Estratégico:</strong> Posicionamento competitivo fortalecido</li>
                    <li><strong>Humano:</strong> Equipe mais focada em valor agregado</li>
                </ul>
                
                <div class="alert alert-primary mt-3">
                    <h5><i class="bi bi-check-circle"></i> Próximos Passos Recomendados</h5>
                    <p>1. Workshop de alinhamento estratégico<br>
                    2. Prototipação rápida das soluções<br>
                    3. Plano de implementação detalhado<br>
                    4. Métricas de sucesso e acompanhamento</p>
                </div>
            </div>
            """)
        else:
            return MockResponse("""
            <div class="alert alert-info">
                <h5><i class="bi bi-robot"></i> Análise Gerada por IA</h5>
                <p>Esta é uma análise estratégica baseada nos dados fornecidos. Para personalização completa, 
                configure sua chave GROQ_API_KEY no arquivo .env</p>
                <small class="text-muted">Modo de desenvolvimento: respostas simuladas para demonstração</small>
            </div>
            """)


class _MockMessage:
    def __init__(self, content):
        self.content = content


class _MockChoice:
    def __init__(self, content):
        self.message = _MockMessage(content)


class _MockCompletion:
    def __init__(self, content):
        self.choices = [_MockChoice(content)]


class _MockCompletionsAPI:
    def create(self, model=None, messages=None, temperature=None, max_tokens=None, **kwargs):
        prompt = " ".join(m.get("content", "") for m in (messages or []))
        return _MockCompletion(_mock_response_for(prompt))


class _MockChatAPI:
    def __init__(self):
        self.completions = _MockCompletionsAPI()


class MockGroqClient:
    """Cliente Groq simulado, usado quando não há GROQ_API_KEY válida."""
    def __init__(self):
        self.chat = _MockChatAPI()


# Usar cliente mock se o real não estiver disponível
if not GROQ_ENABLED:
    print("🔧 Usando modo de desenvolvimento com respostas simuladas")
    groq_client = MockGroqClient()
    GROQ_MODEL = "mock"
    GROQ_ENABLED = True  # Para a interface funcionar

# ==========================================
# 4. FUNÇÕES AUXILIARES
# ==========================================

BOOTSTRAP_CDN = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
ICONS_CDN = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"

def clean_ai_response(text):
    """Limpa resposta da IA mantendo HTML seguro"""
    if not text:
        return "<p>Resposta vazia da IA</p>"
    
    # Converter para string se for objeto
    if hasattr(text, 'text'):
        text = text.text
    
    text = str(text)
    
    # Limpar marcas de código desnecessárias
    text = text.replace("```html", "").replace("```", "").strip()
    
    # Remover HTML malformado
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    
    # Garantir que o texto não seja vazio
    if not text or len(text.strip()) < 10:
        return "<div class='alert alert-warning'>Resposta muito curta da IA. Tente novamente.</div>"
    
    return text

def generate_with_groq(prompt, temperature=0.7):
    """Gera conteúdo usando a Groq API ou o fallback simulado."""
    if not GROQ_ENABLED or not groq_client:
        return "<div class='alert alert-danger'>IA não disponível</div>"

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )

        return clean_ai_response(response.choices[0].message.content)

    except Exception as e:
        error_msg = str(e)
        print(f"⚠️ Erro na geração: {error_msg[:100]}")

        # Se for erro de limite de uso, mostra mensagem específica
        if "rate" in error_msg.lower() or "quota" in error_msg.lower():
            return '''
            <div class="alert alert-warning">
                <h5><i class="bi bi-coin"></i> Limite da API Excedido</h5>
                <p>O limite de uso do modelo Groq foi atingido.</p>
                <ul class="small">
                    <li>Verifique seu uso no <a href="https://console.groq.com/" target="_blank">Groq Console</a></li>
                    <li>Aguarde alguns instantes ou troque de modelo (GROQ_MODEL)</li>
                    <li>Esta aplicação continuará funcionando em modo de demonstração</li>
                </ul>
            </div>
            '''

        return f'''
        <div class="alert alert-danger">
            <i class="bi bi-exclamation-triangle"></i> Erro: {error_msg[:80]}...
            <br><small>Clique em "Regenerar" para tentar novamente</small>
        </div>
        '''


# ==========================================
# 5. RESTANTE DO CÓDIGO (MANTIDO IGUAL)
# ==========================================

# [BASE_HTML_TEMPLATE mantido igual da versão anterior]
# [get_step_classes mantido igual]
# [render_page mantido igual]
# [Rotas mantidas iguais da versão anterior]
# [API endpoint mantido igual]

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
      async function regenerateContent(sectionId, targetDivId, btnElement) {{
        const originalText = btnElement.innerHTML;
        
        btnElement.disabled = true;
        btnElement.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Gerando...';

        try {{
            const response = await fetch('/api/regenerate', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ section: sectionId }})
            }});

            const data = await response.json();

            if (response.ok) {{
                const target = document.getElementById(targetDivId);
                target.style.opacity = '0';
                setTimeout(() => {{
                    target.innerHTML = data.content;
                    target.style.opacity = '1';
                }}, 200);
            }} else {{
                alert('Erro: ' + (data.error || 'Tente novamente'));
            }}

        }} catch (error) {{
            console.error('Erro:', error);
            alert('Erro de conexão');
        }} finally {{
            btnElement.disabled = false;
            btnElement.innerHTML = originalText;
        }}
      }}

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
    
    # Status da IA
    ai_status = ""
    if GROQ_MODEL == "mock":
        ai_status = '''<div class="alert alert-info">
            <i class="bi bi-info-circle"></i> <strong>Modo de Demonstração</strong>
            <p class="mb-0 small">Usando respostas simuladas. Configure sua chave GROQ_API_KEY no arquivo .env para IA real.</p>
        </div>'''
    
    body = f'''
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card card-compact p-5">
          <div class="text-center mb-4">
            <h2 class="fw-bold text-primary">Diagnóstico Empresarial 10 Dias</h2>
            <p class="text-muted">Transformação digital acelerada com IA estratégica</p>
            {ai_status}
          </div>
          
          <form method="post" action="/create" class="needs-validation" novalidate>
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label fw-bold"><i class="bi bi-person-badge"></i> Nome do Cliente</label>
                <input type="text" class="form-control" name="client_name" required placeholder="Ex: TechSolutions Ltda">
              </div>
              <div class="col-md-6">
                <label class="form-label fw-bold"><i class="bi bi-building"></i> Setor</label>
                <select class="form-select" name="industry" required>
                  <option value="">Selecione...</option>
                  <option value="Varejo">Varejo</option>
                  <option value="Serviços">Serviços</option>
                  <option value="Indústria">Indústria</option>
                  <option value="Tecnologia">Tecnologia</option>
                  <option value="Saúde">Saúde</option>
                  <option value="Logística">Logística</option>
                  <option value="Educação">Educação</option>
                  <option value="Finanças">Finanças</option>
                </select>
              </div>
              
              <div class="col-12">
                <label class="form-label fw-bold"><i class="bi bi-exclamation-triangle"></i> Problema Principal (A "Dor")</label>
                <textarea class="form-control" name="area" rows="2" required 
                  placeholder="Ex: Processo de vendas lento, falta de integração entre sistemas, alta taxa de erros manuais..."></textarea>
                <div class="form-text">Descreva o principal desafio que precisa ser resolvido</div>
              </div>

              <div class="col-12">
                <label class="form-label fw-bold"><i class="bi bi-clipboard-data"></i> Contexto & Dados</label>
                <textarea class="form-control" name="context" rows="3" 
                  placeholder="Ex: Empresa com 50 funcionários, faturamento de R$ 5M/ano, 3 sistemas desconectados, perda de 20% de eficiência..."></textarea>
                <div class="form-text">Quanto mais detalhes, melhor a análise da IA</div>
              </div>
              
               <div class="col-12">
                <label class="form-label fw-bold"><i class="bi bi-bullseye"></i> Objetivo Esperado</label>
                <input type="text" class="form-control" name="objective" required placeholder="Ex: Aumentar conversão em 15% em 3 meses, reduzir custos em 25%">
                <div class="form-text">Seja específico e mensurável</div>
              </div>
            </div>

            <div class="d-grid gap-2 mt-5">
              <button type="submit" class="btn btn-primary btn-lg py-3">
                <i class="bi bi-play-circle me-2"></i>Iniciar Diagnóstico Completo
              </button>
              <small class="text-muted text-center mt-2">6 etapas para um plano de transformação completo</small>
            </div>
          </form>
        </div>
        
        <div class="text-center mt-4">
          <small class="text-muted">
            <i class="bi bi-shield-check"></i> Suas informações são usadas apenas para gerar o diagnóstico e não são armazenadas permanentemente.
          </small>
        </div>
      </div>
    </div>
    '''
    return render_page(body, 'home')

@app.route('/create', methods=['POST'])
def create():
    session['client_data'] = {
        'client_name': escape(request.form.get('client_name', 'Cliente')),
        'industry': request.form.get('industry', 'Indústria'),
        'area': escape(request.form.get('area', 'Processos ineficientes')),
        'context': escape(request.form.get('context', 'Contexto não fornecido')),
        'objective': escape(request.form.get('objective', 'Melhorar eficiência')),
        'timeline': '60'
    }
    return redirect(url_for('scope'))

@app.route('/scope')
def scope():
    if 'client_data' not in session: 
        return redirect('/')
    
    data = session['client_data']
    
    # Prompt otimizado para a Groq API
    prompt = f"""
    Como consultor sênior de transformação digital, crie 5 metas SMART específicas para:
    
    EMPRESA: {data['client_name']}
    SETOR: {data['industry']}
    PROBLEMA: {data['area']}
    OBJETIVO: {data['objective']}
    CONTEXTO: {data['context']}
    
    Formato de resposta:
    1. Use apenas HTML válido
    2. Comece com um título <h4>Metas SMART para Transformação</h4>
    3. Crie uma lista <ul> com 5 itens <li>
    4. Cada item deve ter: <strong>Meta X:</strong> [descrição específica e mensurável]
    5. Inclua prazos claros e métricas
    6. Termine com uma nota motivacional
    
    Exemplo de estrutura:
    <h4>Metas SMART para Transformação</h4>
    <ul>
    <li><strong>Meta 1:</strong> Reduzir tempo de processamento de pedidos de 48h para 4h até Dezembro/2024</li>
    </ul>
    <p class="text-muted"><small>Nota: Estas metas são alcançáveis com a estratégia proposta.</small></p>
    """
    
    content = generate_with_groq(prompt)
    
    body = f"""
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3><i class="bi bi-bullseye me-2"></i>Escopo e Metas SMART</h3>
        <button class="btn btn-outline-primary btn-sm" onclick="regenerateContent('scope', 'scope-content', this)">
            <i class="bi bi-stars me-1"></i> Regenerar com IA
        </button>
    </div>
    
    <div class="card card-compact p-4 mb-4">
        <div class="card-body">
            <h5 class="card-title"><i class="bi bi-building me-2"></i>{data['client_name']}</h5>
            <p class="card-text"><strong>Setor:</strong> {data['industry']} | <strong>Foco:</strong> {data['area']}</p>
            <p class="card-text"><strong>Objetivo:</strong> {data['objective']}</p>
        </div>
    </div>
    
    <div class="card card-compact p-4">
        <div id="scope-content">
            {content}
        </div>
    </div>
    
    <div class="d-flex justify-content-between mt-4 no-print">
        <a href="/" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-left me-1"></i>Voltar
        </a>
        <a href="/map" class="btn btn-primary">
            Próximo: Mapeamento de Sistemas <i class="bi bi-arrow-right ms-1"></i>
        </a>
    </div>
    """
    return render_page(body, 'scope')

@app.route('/map')
def map_systems():
    if 'client_data' not in session: 
        return redirect('/')
    
    data = session['client_data']
    
    prompt = f"""
    Para uma empresa do setor {data['industry']} com o problema: '{data['area']}',
    
    Crie uma análise de sistemas em formato HTML de tabela com as seguintes colunas:
    1. Sistema Atual/Necessário
    2. Função Principal
    3. Gargalo/Oportunidade
    4. Prioridade (Alta/Média/Baixa)
    
    Use:
    - <table class="table table-hover">
    - <thead> com <tr> e <th>
    - <tbody> com pelo menos 4-5 linhas
    - Use badges para prioridades: <span class="badge bg-danger">Alta</span>
    - Inclua sistemas comuns do setor {data['industry']}
    """
    
    content = generate_with_groq(prompt)
    
    body = f"""
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3><i class="bi bi-diagram-3 me-2"></i>Mapa de Sistemas e Gargalos</h3>
        <button class="btn btn-outline-primary btn-sm" onclick="regenerateContent('map', 'map-content', this)">
            <i class="bi bi-stars me-1"></i> Reanalisar
        </button>
    </div>
    
    <div class="card card-compact p-4">
        <div class="card-header">
            <h5 class="mb-0"><i class="bi bi-info-circle me-2"></i>Análise de Arquitetura de Sistemas</h5>
        </div>
        <div class="card-body">
            <p>Identificação dos sistemas atuais e necessários, com foco nos gargalos que impactam <strong>{data['area']}</strong>.</p>
            <div id="map-content">
                {content}
            </div>
        </div>
    </div>
    
    <div class="d-flex justify-content-between mt-4 no-print">
        <a href="/scope" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-left me-1"></i>Voltar
        </a>
        <a href="/roi" class="btn btn-primary">
            Próximo: Análise de ROI <i class="bi bi-arrow-right ms-1"></i>
        </a>
    </div>
    """
    return render_page(body, 'map')

@app.route('/roi')
def roi():
    if 'client_data' not in session: 
        return redirect('/')
    
    data = session['client_data']
    
    prompt = f"""
    Para resolver o problema '{data['area']}' na empresa {data['client_name']} ({data['industry']}),
    
    Crie uma análise de ROI em HTML que inclua:
    
    1. Título: <h4>Análise Financeira e ROI</h4>
    2. Um resumo executivo em <div class="alert alert-success">
    3. Tabela com: Investimento x Economia x Payback
    4. Lista de benefícios tangíveis e intangíveis
    5. Estimativa conservadora e otimista
    
    Dados do contexto: {data['context']}
    Objetivo: {data['objective']}
    
    Use formatação Bootstrap e seja realista com o setor {data['industry']}.
    """
    
    content = generate_with_groq(prompt)
    
    body = f"""
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3><i class="bi bi-calculator me-2"></i>Análise de Retorno (ROI)</h3>
        <button class="btn btn-outline-primary btn-sm" onclick="regenerateContent('roi', 'roi-content', this)">
            <i class="bi bi-stars me-1"></i> Recalcular
        </button>
    </div>
    
    <div class="card card-compact p-4">
        <div class="card-header">
            <h5 class="mb-0"><i class="bi bi-graph-up-arrow me-2"></i>Impacto Financeiro da Transformação</h5>
        </div>
        <div class="card-body">
            <p class="text-muted">Análise baseada no problema: <strong>{data['area']}</strong></p>
            <div id="roi-content">
                {content}
            </div>
        </div>
    </div>
    
    <div class="d-flex justify-content-between mt-4 no-print">
        <a href="/map" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-left me-1"></i>Voltar
        </a>
        <a href="/roadmap" class="btn btn-primary">
            Próximo: Roadmap de Execução <i class="bi bi-arrow-right ms-1"></i>
        </a>
    </div>
    """
    return render_page(body, 'roi')

@app.route('/roadmap')
def roadmap():
    if 'client_data' not in session: 
        return redirect('/')
    
    data = session['client_data']
    
    prompt = f"""
    Crie um Roadmap de implementação em 3 fases para: {data['objective']}
    
    Empresa: {data['client_name']}
    Setor: {data['industry']}
    Problema: {data['area']}
    
    Formato HTML com:
    1. Layout em 3 colunas (Fase 1, 2, 3)
    2. Cada fase como um card Bootstrap com:
       - Título da fase e duração
       - Principais entregas
       - Marcos importantes
       - Recursos necessários
    3. Timeline visual
    4. Métricas de sucesso por fase
    
    Use classes Bootstrap como: row, col-md-4, card, card-header, card-body
    """
    
    content = generate_with_groq(prompt)
    
    body = f"""
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3><i class="bi bi-map me-2"></i>Roadmap de Execução</h3>
        <button class="btn btn-outline-primary btn-sm" onclick="regenerateContent('roadmap', 'roadmap-content', this)">
            <i class="bi bi-stars me-1"></i> Regenerar
        </button>
    </div>
    
    <div class="card card-compact p-4">
        <div class="card-header">
            <h5 class="mb-0"><i class="bi bi-calendar-check me-2"></i>Plano de Implementação em 180 Dias</h5>
        </div>
        <div class="card-body">
            <p>Planejamento estratégico para alcançar: <strong>{data['objective']}</strong></p>
            <div id="roadmap-content">
                {content}
            </div>
        </div>
    </div>
    
    <div class="d-flex justify-content-between mt-4 no-print">
        <a href="/roi" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-left me-1"></i>Voltar
        </a>
        <a href="/brief" class="btn btn-primary">
            Próximo: Brief Final <i class="bi bi-arrow-right ms-1"></i>
        </a>
    </div>
    """
    return render_page(body, 'roadmap')

@app.route('/brief')
def brief():
    if 'client_data' not in session: 
        return redirect('/')
    
    data = session['client_data']
    
    prompt = f"""
    Escreva um Brief Executivo Profissional para {data['client_name']} que resume toda a análise.
    
    ESTRUTURA:
    1. Cabeçalho com logo e data
    2. Resumo Executivo (1 parágrafo)
    3. Diagnóstico Atual (problema e contexto)
    4. Solução Proposta (visão geral)
    5. Benefícios Esperados (quantitativos e qualitativos)
    6. Investimento e ROI
    7. Próximos Passos
    8. Assinatura
    
    Use:
    - HTML semântico
    - Classes Bootstrap para formatação
    - Tom profissional e persuasivo
    - Destaque para dados importantes
    - Data atual: {datetime.now().strftime('%d/%m/%Y')}
    
    Inclua {data['industry']}, {data['area']}, {data['objective']} no contexto.
    """
    
    content = generate_with_groq(prompt, temperature=0.5)
    
    body = f"""
    <div class="d-flex justify-content-between align-items-center mb-4 no-print">
        <h3><i class="bi bi-file-earmark-text me-2"></i>Brief Executivo Final</h3>
        <div>
            <button class="btn btn-outline-primary btn-sm me-2" onclick="regenerateContent('brief', 'brief-content', this)">
                <i class="bi bi-stars me-1"></i> Reescrever
            </button>
            <button onclick="window.print()" class="btn btn-success btn-sm">
                <i class="bi bi-printer me-1"></i> Imprimir/PDF
            </button>
        </div>
    </div>
    
    <div class="card card-compact p-5 mb-5 border-0 shadow-none print-area">
        <div class="text-center mb-5 border-bottom pb-4">
            <h1 class="display-4">Diagnóstico Estratégico</h1>
            <h3 class="text-primary">{data['client_name']}</h3>
            <p class="lead">Plano de Transformação Digital em 180 Dias</p>
            <small class="text-muted">Emitido em {datetime.now().strftime('%d/%m/%Y')} | InNovaIdeia Consulting</small>
        </div>
        
        <div id="brief-content">
            {content}
        </div>
        
        <div class="mt-5 pt-4 border-top">
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="bi bi-shield-check"></i> Confidencialidade</h6>
                    <p class="small text-muted">Este documento contém informações confidenciais destinadas exclusivamente a {data['client_name']}.</p>
                </div>
                <div class="col-md-6 text-end">
                    <h6><i class="bi bi-person-circle"></i> Consultor Responsável</h6>
                    <p class="small text-muted">Equipe InNovaIdeia AI Diagnosis</p>
                    <p class="small text-muted">diagnostico@innovaideia.com.br</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="text-center mb-5 no-print">
        <a href="/" class="btn btn-outline-secondary me-2">
            <i class="bi bi-house me-1"></i> Início
        </a>
        <a href="/" class="btn btn-primary">
            <i class="bi bi-plus-circle me-1"></i> Novo Diagnóstico
        </a>
    </div>
    """
    return render_page(body, 'brief')

@app.route('/api/regenerate', methods=['POST'])
def api_regenerate():
    if 'client_data' not in session:
        return jsonify({'error': 'Sessão expirada. Recarregue a página.'}), 401
    
    data = request.json
    section = data.get('section')
    client = session['client_data']
    
    prompts = {
        'scope': f"""Reescreva as 5 Metas SMART para {client['client_name']} ({client['industry']}) 
        focando especificamente em {client['objective']}. 
        Contexto: {client['context']}. 
        Problema: {client['area']}.
        Use HTML formatado com listas e destaques.""",
        
        'map': f"""Reanalise os sistemas e gargalos para uma empresa de {client['industry']} 
        que enfrenta: {client['area']}. 
        Inclua sistemas específicos do setor {client['industry']} e priorize por impacto.
        Formato: tabela HTML com Bootstrap.""",
        
        'roi': f"""Recalcule o ROI para {client['client_name']} considerando: 
        Objetivo: {client['objective']}
        Contexto: {client['context']}
        Seja mais detalhado nos cálculos e inclua cenários conservador e otimista.
        Use HTML com alertas e tabelas.""",
        
        'roadmap': f"""Crie um roadmap alternativo para {client['client_name']} 
        com foco em resultados rápidos (Quick Wins) para: {client['objective']}.
        Divida em fases com entregas concretas e prazos realistas.
        Use layout de 3 colunas com cards Bootstrap.""",
        
        'brief': f"""Reescreva o Brief Executivo para {client['client_name']} 
        com tom mais urgente e foco em ação imediata.
        Destaque: {client['area']} como oportunidade crítica.
        Objetivo principal: {client['objective']}.
        Formato HTML profissional."""
    }
    
    if section not in prompts:
        return jsonify({'error': 'Seção inválida'}), 400
        
    content = generate_with_groq(prompts[section])
    
    if content and "alert alert-danger" not in content:
        return jsonify({'content': content})
    else:
        return jsonify({'error': 'Falha na geração. Tente novamente.'}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 DIAGNÓSTICO EMPRESARIAL 10 DIAS - MVP 1.4")
    print("="*60)
    
    if GROQ_ENABLED and GROQ_MODEL != "mock":
        print("✅ IA Groq disponível")
        print(f"📊 Modelo ativo: {GROQ_MODEL}")
    else:
        print("🔧 Modo de desenvolvimento ativo")
        print("💡 Para IA real, configure sua chave GROQ_API_KEY no arquivo .env")
    
    print(f"\n🌐 Acesse: http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    # Configurações para desenvolvimento
    app.run(
        debug=True, 
        port=5000,
        host='0.0.0.0'  # Permite acesso de outros dispositivos na rede
    )