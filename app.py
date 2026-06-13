import streamlit as st
import pandas as pd
import re
from datetime import datetime

# Tentar importar bibliotecas para PDF (opcionais)
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

st.set_page_config(page_title="IA Orçamentos Climatização", page_icon="🌡️", layout="wide")

st.title("🌡️ IA Orçamentos Climatização - Análise de Projetos")
st.caption(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
st.markdown("---")

# ========== FUNÇÕES DE ANÁLISE DE ARQUIVOS ==========

def extrair_texto_pdf(arquivo_pdf):
    """Extrai texto de arquivo PDF"""
    try:
        if not PDF_SUPPORT:
            return None
        pdf_reader = PyPDF2.PdfReader(arquivo_pdf)
        texto_completo = ""
        for pagina in pdf_reader.pages:
            texto = pagina.extract_text()
            if texto:
                texto_completo += texto + " "
        return texto_completo
    except Exception as e:
        return None

def analisar_descricao_projeto(descricao):
    """Extrai informações automáticas da descrição do projeto"""
    if not descricao:
        descricao = ""
    desc_lower = descricao.lower()
    
    resultados = {
        "sistema": "VRF/VRV",
        "area_m2": 500,
        "carga_tr": 20.0,
        "qtd_evaporadoras": 8,
        "metros_tubo": 150,
        "servicos_extras": [],
        "texto_original": descricao[:500] if descricao else ""
    }
    
    # Detectar sistema
    if "água gelada" in desc_lower or "chiller" in desc_lower:
        resultados["sistema"] = "Água Gelada"
    elif "vrf" in desc_lower or "vrv" in desc_lower:
        resultados["sistema"] = "VRF/VRV"
    elif "split" in desc_lower:
        resultados["sistema"] = "Split"
    
    # Extrair área
    padroes_area = [r'(\d+)\s*m[²2]', r'(\d+)\s*metros quadrados', r'área[:\s]*(\d+)']
    for padrao in padroes_area:
        area_match = re.search(padrao, desc_lower)
        if area_match:
            resultados["area_m2"] = int(area_match.group(1))
            break
    
    # Extrair carga térmica
    tr_match = re.search(r'(\d+(?:\.\d+)?)\s*tr', desc_lower)
    if tr_match:
        resultados["carga_tr"] = float(tr_match.group(1))
    
    btu_match = re.search(r'(\d+)\s*btu', desc_lower)
    if btu_match:
        resultados["carga_tr"] = round(int(btu_match.group(1)) / 12000, 1)
    
    # Extrair evaporadoras
    evap_match = re.search(r'(\d+)\s*evaporadoras?', desc_lower)
    if evap_match:
        resultados["qtd_evaporadoras"] = int(evap_match.group(1))
    else:
        if resultados["area_m2"] > 0:
            resultados["qtd_evaporadoras"] = max(4, round(resultados["area_m2"] / 70))
    
    # Estimar tubulação
    if resultados["carga_tr"] > 0:
        resultados["metros_tubo"] = int(resultados["carga_tr"] * 15)
    else:
        resultados["metros_tubo"] = int(resultados["area_m2"] * 0.3)
    
    # Detectar serviços extras
    if "startup" in desc_lower or "comissionamento" in desc_lower:
        resultados["servicos_extras"].append("Startup/Comissionamento")
    if "bms" in desc_lower or "automação" in desc_lower:
        resultados["servicos_extras"].append("BMS/Automação")
    if "garantia" in desc_lower:
        resultados["servicos_extras"].append("Garantia Estendida")
    if "solda" in desc_lower:
        resultados["servicos_extras"].append("Solda Especializada")
    
    return resultados

def calcular_precos_por_analise(analise):
    """Calcula valores sugeridos baseados na análise"""
    sistema = analise["sistema"]
    carga = float(analise["carga_tr"])
    qtd_evap = int(analise["qtd_evaporadoras"])
    metros_tubo = int(analise["metros_tubo"])
    
    if sistema == "VRF/VRV":
        equip_cond = float(carga * 3500)  # R$ 3.500 por TR
        equip_evap = float(qtd_evap * 4200)
        mao_tec = float(carga * 800)
        tubulacao = float(metros_tubo * 63)
        startup = 3500.0
    elif sistema == "Água Gelada":
        equip_cond = float(carga * 2800)
        equip_evap = float(qtd_evap * 2500)
        mao_tec = float(carga * 700)
        tubulacao = float(metros_tubo * 82)
        startup = 4500.0
    else:  # Split
        equip_cond = float(carga * 3000)
        equip_evap = float(qtd_evap * 2000)
        mao_tec = float(carga * 600)
        tubulacao = float(metros_tubo * 50)
        startup = 2500.0
    
    return {
        "equip_cond": equip_cond,
        "equip_evap": equip_evap,
        "ins_cobre": tubulacao,
        "mao_tec": mao_tec,
        "serv_startup": startup
    }

# ========== INICIALIZAR SESSION STATE ==========
if 'valores' not in st.session_state:
    st.session_state.valores = {
        'equip_cond': 89000.0,
        'equip_evap': 45000.0,
        'equip_bms': 8500.0,
        'ins_cobre': 19200.0,
        'ins_drenos': 3500.0,
        'ins_outros': 2500.0,
        'mao_tec': 28000.0,
        'mao_aux': 8000.0,
        'mao_eng': 5000.0,
        'serv_startup': 4500.0,
        'serv_testes': 2500.0,
        'garantia': 2.0,
        'adm': 2.5,
        'margem_dir': 40.0,
        'fornece_equip': False,
        'fornece_insumos': False,
        'valor_equip_terc': 0.0,
        'valor_insumos_terc': 0.0,
        'mao_terc': 28000.0,
        'consumiveis': 2800.0,
        'startup_terc': 4500.0,
        'margem_terc': 25.0
    }

# ========== FUNÇÃO DE CÁLCULO ==========
def calcular_tudo():
    v = st.session_state.valores
    
    custo_equip = float(v['equip_cond']) + float(v['equip_evap']) + float(v['equip_bms'])
    custo_insumos = float(v['ins_cobre']) + float(v['ins_drenos']) + float(v['ins_outros'])
    custo_mao = float(v['mao_tec']) + float(v['mao_aux']) + float(v['mao_eng'])
    custo_serv = float(v['serv_startup']) + float(v['serv_testes'])
    custo_total_dir = custo_equip + custo_insumos + custo_mao + custo_serv
    
    garantia = float(v['garantia'])
    adm = float(v['adm'])
    margem_dir = float(v['margem_dir'])
    
    preco_cliente = custo_total_dir * (1 + garantia/100 + adm/100) * (1 + margem_dir/100)
    lucro_dir = preco_cliente - (custo_total_dir * (1 + garantia/100 + adm/100))
    
    mao_terc = float(v['mao_terc'])
    consumiveis = float(v['consumiveis'])
    startup_terc = float(v['startup_terc'])
    valor_equip_terc = float(v['valor_equip_terc'])
    valor_insumos_terc = float(v['valor_insumos_terc'])
    margem_terc = float(v['margem_terc'])
    
    custo_terc_base = mao_terc + consumiveis + startup_terc + valor_equip_terc + valor_insumos_terc
    preco_terc = custo_terc_base * (1 + margem_terc/100)
    lucro_terc = preco_terc - custo_terc_base
    
    return {
        'custo_total_dir': custo_total_dir,
        'preco_cliente': preco_cliente,
        'lucro_dir': lucro_dir,
        'custo_total_terc': custo_terc_base,
        'preco_terc': preco_terc,
        'lucro_terc': lucro_terc
    }

# ========== ABA DE UPLOAD E ANÁLISE ==========
st.header("📁 ANÁLISE AUTOMÁTICA DO PROJETO")

tab_upload, tab_manual, tab_exemplo = st.tabs(["📤 Upload de Arquivo (PDF/DWG)", "✏️ Preenchimento Manual", "📖 Exemplos"])

with tab_upload:
    st.subheader("Faça upload do projeto")
    
    arquivo = st.file_uploader(
        "Selecione o arquivo do projeto",
        type=['pdf', 'dwg', 'dxf', 'txt', 'csv', 'xlsx'],
        help="Formatos suportados: PDF, DWG, DXF, TXT, CSV, XLSX"
    )
    
    if arquivo:
        st.info(f"📄 Arquivo carregado: {arquivo.name}")
        
        if arquivo.name.lower().endswith('.pdf'):
            st.info("🔄 Processando arquivo PDF...")
            if PDF_SUPPORT:
                texto_extraido = extrair_texto_pdf(arquivo)
                if texto_extraido:
                    with st.spinner("Analisando PDF..."):
                        analise = analisar_descricao_projeto(texto_extraido)
                        precos = calcular_precos_por_analise(analise)
                        
                        st.session_state.valores['equip_cond'] = float(precos['equip_cond'])
                        st.session_state.valores['equip_evap'] = float(precos['equip_evap'])
                        st.session_state.valores['ins_cobre'] = float(precos['ins_cobre'])
                        st.session_state.valores['mao_tec'] = float(precos['mao_tec'])
                        st.session_state.valores['serv_startup'] = float(precos['serv_startup'])
                        
                        st.success("✅ PDF processado com sucesso!")
                        
                        st.subheader("📊 Informações extraídas:")
                        col_a1, col_a2 = st.columns(2)
                        with col_a1:
                            st.metric("Sistema", analise['sistema'])
                            st.metric("Área", f"{analise['area_m2']} m²")
                            st.metric("Carga", f"{analise['carga_tr']} TR")
                        with col_a2:
                            st.metric("Evaporadoras", f"{analise['qtd_evaporadoras']} un")
                            st.metric("Tubulação", f"{analise['metros_tubo']} m")
                            if analise['servicos_extras']:
                                st.write("**Extras:**", ", ".join(analise['servicos_extras']))
                        
                        st.rerun()
                    else:
                        st.warning("Não foi possível extrair texto do PDF.")
                else:
                    st.warning("PDF parece não conter texto editável.")
            else:
                st.warning("Biblioteca PDF não disponível. Tente colar o texto manualmente.")
                
        elif arquivo.name.lower().endswith(('.dwg', '.dxf')):
            st.info("📐 Arquivo CAD detectado")
            st.warning("Para arquivos DWG/DXF, descreva o projeto manualmente na aba 'Preenchimento Manual'")
            
        elif arquivo.name.lower().endswith(('.txt', '.csv', '.xlsx')):
            st.info(f"Arquivo {arquivo.name} carregado. Use a aba 'Preenchimento Manual' para inserir os dados.")

with tab_manual:
    st.subheader("Preencha os dados manualmente")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        sistema_manual = st.selectbox("Sistema", ["VRF/VRV", "Água Gelada", "Split"])
        area_manual = st.number_input("Área (m²)", value=850, step=50)
        carga_manual = st.number_input("Carga (TR)", value=28.5, step=1.0, format="%.1f")
    with col_m2:
        qtd_evap_manual = st.number_input("Quantidade de evaporadoras", value=12, step=1)
        metros_tubo_manual = st.number_input("Metros de tubulação", value=int(carga_manual * 15), step=50)
    
    if st.button("📊 Gerar orçamento baseado nestes dados", use_container_width=True):
        analise_manual = {
            "sistema": sistema_manual,
            "carga_tr": float(carga_manual),
            "qtd_evaporadoras": int(qtd_evap_manual),
            "metros_tubo": int(metros_tubo_manual),
            "area_m2": int(area_manual),
            "servicos_extras": []
        }
        precos = calcular_precos_por_analise(analise_manual)
        
        st.session_state.valores['equip_cond'] = float(precos['equip_cond'])
        st.session_state.valores['equip_evap'] = float(precos['equip_evap'])
        st.session_state.valores['ins_cobre'] = float(precos['ins_cobre'])
        st.session_state.valores['mao_tec'] = float(precos['mao_tec'])
        st.session_state.valores['serv_startup'] = float(precos['serv_startup'])
        
        st.success("✅ Dados aplicados! Role para baixo para ver o orçamento.")
        st.rerun()

with tab_exemplo:
    st.subheader("📋 Exemplo de descrição")
    st.code("""
Projeto de climatização para edifício comercial:
- Área total: 850 m²
- Sistema VRF/VRV
- Carga térmica: 28.5 TR
- 12 evaporadoras tipo cassete
- Incluir startup e comissionamento
    """)

# ========== LINHA DIVISÓRIA ==========
st.markdown("---")
st.header("💰 ORÇAMENTO (atualiza em tempo real)")

# ========== COLUNAS DE EDIÇÃO ==========
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 MODELO DIRETO")
    
    with st.expander("📦 Equipamentos", expanded=True):
        st.session_state.valores['equip_cond'] = float(st.number_input("Condensadoras/Chiller", value=float(st.session_state.valores['equip_cond']), step=5000.0, format="%.2f"))
        st.session_state.valores['equip_evap'] = float(st.number_input("Evaporadoras/Fan Coils", value=float(st.session_state.valores['equip_evap']), step=5000.0, format="%.2f"))
        st.session_state.valores['equip_bms'] = float(st.number_input("BMS/Controles", value=float(st.session_state.valores['equip_bms']), step=1000.0, format="%.2f"))
    
    with st.expander("🔩 Insumos", expanded=True):
        st.session_state.valores['ins_cobre'] = float(st.number_input("Cobre + Isolante", value=float(st.session_state.valores['ins_cobre']), step=1000.0, format="%.2f"))
        st.session_state.valores['ins_drenos'] = float(st.number_input("Drenos + Eletrodutos", value=float(st.session_state.valores['ins_drenos']), step=500.0, format="%.2f"))
        st.session_state.valores['ins_outros'] = float(st.number_input("Outros insumos", value=float(st.session_state.valores['ins_outros']), step=500.0, format="%.2f"))
    
    with st.expander("👷 Mão de Obra", expanded=True):
        st.session_state.valores['mao_tec'] = float(st.number_input("Técnicos", value=float(st.session_state.valores['mao_tec']), step=2000.0, format="%.2f"))
        st.session_state.valores['mao_aux'] = float(st.number_input("Auxiliares", value=float(st.session_state.valores['mao_aux']), step=1000.0, format="%.2f"))
        st.session_state.valores['mao_eng'] = float(st.number_input("Engenharia/Projeto", value=float(st.session_state.valores['mao_eng']), step=1000.0, format="%.2f"))
    
    with st.expander("⚙️ Serviços", expanded=True):
        st.session_state.valores['serv_startup'] = float(st.number_input("Startup/Comissionamento", value=float(st.session_state.valores['serv_startup']), step=500.0, format="%.2f"))
        st.session_state.valores['serv_testes'] = float(st.number_input("Testes + Carga de gás", value=float(st.session_state.valores['serv_testes']), step=500.0, format="%.2f"))
    
    col_perc1, col_perc2, col_perc3 = st.columns(3)
    with col_perc1:
        st.session_state.valores['garantia'] = float(st.number_input("Garantia %", value=float(st.session_state.valores['garantia']), step=0.5, format="%.1f"))
    with col_perc2:
        st.session_state.valores['adm'] = float(st.number_input("Adm/Frete %", value=float(st.session_state.valores['adm']), step=0.5, format="%.1f"))
    with col_perc3:
        st.session_state.valores['margem_dir'] = float(st.number_input("Margem %", value=float(st.session_state.valores['margem_dir']), step=1.0, format="%.1f"))

with col2:
    st.subheader("🎯 MODELO TERCEIRO")
    
    st.session_state.valores['fornece_equip'] = st.checkbox("Você fornece equipamentos?", value=st.session_state.valores['fornece_equip'])
    if st.session_state.valores['fornece_equip']:
        valor_padrao = float(st.session_state.valores['equip_cond'] + st.session_state.valores['equip_evap'])
        st.session_state.valores['valor_equip_terc'] = float(st.number_input("Valor equipamentos", value=float(st.session_state.valores['valor_equip_terc']) if st.session_state.valores['valor_equip_terc'] > 0 else valor_padrao, step=5000.0, format="%.2f"))
    
    st.session_state.valores['fornece_insumos'] = st.checkbox("Você fornece insumos?", value=st.session_state.valores['fornece_insumos'])
    if st.session_state.valores['fornece_insumos']:
        st.session_state.valores['valor_insumos_terc'] = float(st.number_input("Valor insumos", value=float(st.session_state.valores['valor_insumos_terc']) if st.session_state.valores['valor_insumos_terc'] > 0 else st.session_state.valores['ins_cobre'], step=2000.0, format="%.2f"))
    
    st.markdown("---")
    st.session_state.valores['mao_terc'] = float(st.number_input("Mão de obra", value=float(st.session_state.valores['mao_terc']), step=2000.0, format="%.2f"))
    st.session_state.valores['consumiveis'] = float(st.number_input("Consumíveis", value=float(st.session_state.valores['consumiveis']), step=500.0, format="%.2f"))
    st.session_state.valores['startup_terc'] = float(st.number_input("Startup", value=float(st.session_state.valores['startup_terc']), step=500.0, format="%.2f"))
    st.session_state.valores['margem_terc'] = float(st.number_input("Margem Terceiro %", value=float(st.session_state.valores['margem_terc']), step=1.0, format="%.1f"))

# ========== CALCULAR E EXIBIR RESULTADOS ==========
resultados = calcular_tudo()

st.markdown("---")
col_res1, col_res2 = st.columns(2)

with col_res1:
    st.subheader("📊 RESULTADO DIRETO")
    st.metric("💰 Seu Custo Total", f"R$ {resultados['custo_total_dir']:,.2f}")
    st.metric("🏷️ Preço para Cliente", f"R$ {resultados['preco_cliente']:,.2f}")
    st.metric("📈 Seu Lucro", f"R$ {resultados['lucro_dir']:,.2f}")

with col_res2:
    st.subheader("📊 RESULTADO TERCEIRO")
    st.metric("💰 Seu Custo Total", f"R$ {resultados['custo_total_terc']:,.2f}")
    st.metric("🏷️ Preço para Construtora", f"R$ {resultados['preco_terc']:,.2f}")
    st.metric("📈 Seu Lucro", f"R$ {resultados['lucro_terc']:,.2f}")

# Comparação
st.markdown("---")
diferenca = resultados['lucro_dir'] - resultados['lucro_terc']
if diferenca > 0:
    st.success(f"✅ **Recomendação:** Modelo DIRETO é R$ {diferenca:,.2f} mais lucrativo")
else:
    st.info(f"ℹ️ **Recomendação:** Modelo TERCEIRO tem lucro de R$ {resultados['lucro_terc']:,.2f} com menos risco")

st.caption("💡 **Qualquer alteração nos valores atualiza os preços automaticamente!**")
