import streamlit as st
import pandas as pd
import re
from datetime import datetime
import tempfile
import os

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

def extrair_info_dwg(arquivo_dwg):
    """Simula extração de informações do DWG (por enquanto baseado no nome)"""
    # Por enquanto, retorna uma mensagem orientativa
    return f"Arquivo DWG detectado: {arquivo_dwg.name}. Análise avançada disponível na versão profissional."

def analisar_descricao_projeto(descricao):
    """Extrai informações automáticas da descrição do projeto"""
    desc_lower = descricao.lower()
    
    resultados = {
        "sistema": "VRF/VRV",
        "area_m2": 500,
        "carga_tr": 20,
        "qtd_evaporadoras": 8,
        "metros_tubo": 150,
        "servicos_extras": [],
        "texto_original": descricao[:500]
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
    carga = analise["carga_tr"]
    qtd_evap = analise["qtd_evaporadoras"]
    metros_tubo = analise["metros_tubo"]
    
    if sistema == "VRF/VRV":
        equip_cond = carga * 3500  # R$ 3.500 por TR
        equip_evap = qtd_evap * 4200
        mao_tec = carga * 800
        tubulacao = metros_tubo * 63
        startup = 3500
    elif sistema == "Água Gelada":
        equip_cond = carga * 2800
        equip_evap = qtd_evap * 2500
        mao_tec = carga * 700
        tubulacao = metros_tubo * 82
        startup = 4500
    else:  # Split
        equip_cond = carga * 3000
        equip_evap = qtd_evap * 2000
        mao_tec = carga * 600
        tubulacao = metros_tubo * 50
        startup = 2500
    
    return {
        "equip_cond": equip_cond,
        "equip_evap": equip_evap,
        "ins_cobre": tubulacao,
        "mao_tec": mao_tec,
        "serv_startup": startup,
        "sistema": sistema,
        "carga_tr": carga,
        "qtd_evap": qtd_evap
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
    
    custo_equip = v['equip_cond'] + v['equip_evap'] + v['equip_bms']
    custo_insumos = v['ins_cobre'] + v['ins_drenos'] + v['ins_outros']
    custo_mao = v['mao_tec'] + v['mao_aux'] + v['mao_eng']
    custo_serv = v['serv_startup'] + v['serv_testes']
    custo_total_dir = custo_equip + custo_insumos + custo_mao + custo_serv
    
    preco_cliente = custo_total_dir * (1 + v['garantia']/100 + v['adm']/100) * (1 + v['margem_dir']/100)
    lucro_dir = preco_cliente - (custo_total_dir * (1 + v['garantia']/100 + v['adm']/100))
    
    custo_terc_base = v['mao_terc'] + v['consumiveis'] + v['startup_terc'] + v['valor_equip_terc'] + v['valor_insumos_terc']
    preco_terc = custo_terc_base * (1 + v['margem_terc']/100)
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
        st.info(f"📄 Arquivo carregado: {arquivo.name} ({arquivo.size} bytes)")
        
        # Processar baseado no tipo
        if arquivo.name.lower().endswith('.pdf'):
            st.info("🔄 Processando arquivo PDF...")
            texto_extraido = extrair_texto_pdf(arquivo)
            if texto_extraido:
                with st.spinner("Analisando PDF..."):
                    analise = analisar_descricao_projeto(texto_extraido)
                    precos_sugeridos = calcular_precos_por_analise(analise)
                    
                    st.session_state.valores['equip_cond'] = precos_sugeridos['equip_cond']
                    st.session_state.valores['equip_evap'] = precos_sugeridos['equip_evap']
                    st.session_state.valores['ins_cobre'] = precos_sugeridos['ins_cobre']
                    st.session_state.valores['mao_tec'] = precos_sugeridos['mao_tec']
                    st.session_state.valores['serv_startup'] = precos_sugeridos['serv_startup']
                    
                    st.success("✅ PDF processado com sucesso!")
                    
                    st.subheader("📊 Informações extraídas do PDF:")
                    col_a1, col_a2, col_a3 = st.columns(3)
                    with col_a1:
                        st.metric("Sistema", analise['sistema'])
                        st.metric("Área", f"{analise['area_m2']} m²")
                    with col_a2:
                        st.metric("Carga", f"{analise['carga_tr']} TR")
                        st.metric("Evaporadoras", f"{analise['qtd_evaporadoras']} un")
                    with col_a3:
                        st.metric("Tubulação", f"{analise['metros_tubo']} m")
                        if analise['servicos_extras']:
                            st.write("**Extras:**", ", ".join(analise['servicos_extras']))
                    
                    st.rerun()
            else:
                st.warning("Não foi possível extrair texto do PDF. Tente colar a descrição manualmente na aba abaixo.")
                st.text_area("Ou cole o texto do projeto aqui:", height=150, key="pdf_texto_alternativo")
                if st.button("Analisar texto colado", key="btn_pdf_alt"):
                    if st.session_state.pdf_texto_alternativo:
                        analise = analisar_descricao_projeto(st.session_state.pdf_texto_alternativo)
                        precos_sugeridos = calcular_precos_por_analise(analise)
                        st.session_state.valores['equip_cond'] = precos_sugeridos['equip_cond']
                        st.session_state.valores['equip_evap'] = precos_sugeridos['equip_evap']
                        st.session_state.valores['ins_cobre'] = precos_sugeridos['ins_cobre']
                        st.session_state.valores['mao_tec'] = precos_sugeridos['mao_tec']
                        st.session_state.valores['serv_startup'] = precos_sugeridos['serv_startup']
                        st.success("✅ Texto analisado!")
                        st.rerun()
        
        elif arquivo.name.lower().endswith(('.dwg', '.dxf')):
            st.info("📐 Arquivo CAD detectado (DWG/DXF)")
            st.warning("""
            **Análise de arquivos DWG:** 
            O Streamlit Cloud não suporta extração nativa de DWG. 
            
            **Soluções:**
            1. Descreva manualmente o projeto na aba "Preenchimento Manual"
            2. Exporte o DWG para PDF e faça upload novamente
            3. Cole as informações do projeto no campo abaixo
            """)
            
            texto_manual = st.text_area("Cole as informações do projeto (área, carga, equipamentos):", height=150, key="dwg_texto")
            if st.button("Analisar informações", key="btn_dwg"):
                if texto_manual:
                    analise = analisar_descricao_projeto(texto_manual)
                    precos_sugeridos = calcular_precos_por_analise(analise)
                    st.session_state.valores['equip_cond'] = precos_sugeridos['equip_cond']
                    st.session_state.valores['equip_evap'] = precos_sugeridos['equip_evap']
                    st.session_state.valores['ins_cobre'] = precos_sugeridos['ins_cobre']
                    st.session_state.valores['mao_tec'] = precos_sugeridos['mao_tec']
                    st.session_state.valores['serv_startup'] = precos_sugeridos['serv_startup']
                    st.success("✅ Informações aplicadas!")
                    st.rerun()
        
        elif arquivo.name.lower().endswith(('.csv', '.xlsx')):
            try:
                if arquivo.name.endswith('.csv'):
                    df = pd.read_csv(arquivo)
                else:
                    df = pd.read_excel(arquivo)
                st.success("✅ Planilha carregada! Use a aba 'Preenchimento Manual' para inserir os dados.")
                st.dataframe(df.head())
            except Exception as e:
                st.error(f"Erro ao ler planilha: {e}")
        
        else:  # TXT
            texto = arquivo.read().decode('utf-8')
            with st.spinner("Analisando arquivo de texto..."):
                analise = analisar_descricao_projeto(texto)
                precos_sugeridos = calcular_precos_por_analise(analise)
                
                st.session_state.valores['equip_cond'] = precos_sugeridos['equip_cond']
                st.session_state.valores['equip_evap'] = precos_sugeridos['equip_evap']
                st.session_state.valores['ins_cobre'] = precos_sugeridos['ins_cobre']
                st.session_state.valores['mao_tec'] = precos_sugeridos['mao_tec']
                st.session_state.valores['serv_startup'] = precos_sugeridos['serv_startup']
                
                st.success("✅ Arquivo de texto processado!")
                st.rerun()

with tab_manual:
    st.subheader("Preencha os dados manualmente")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        sistema_manual = st.selectbox("Sistema", ["VRF/VRV", "Água Gelada", "Split"])
        area_manual = st.number_input("Área (m²)", value=850)
        carga_manual = st.number_input("Carga (TR)", value=28.5)
    with col_m2:
        qtd_evap_manual = st.number_input("Quantidade de evaporadoras", value=12)
        metros_tubo_manual = st.number_input("Metros de tubulação", value=carga_manual * 15)
    
    if st.button("📊 Gerar orçamento baseado nestes dados", use_container_width=True):
        analise_manual = {
            "sistema": sistema_manual,
            "carga_tr": carga_manual,
            "qtd_evaporadoras": qtd_evap_manual,
            "metros_tubo": metros_tubo_manual,
            "area_m2": area_manual,
            "servicos_extras": []
        }
        precos = calcular_precos_por_analise(analise_manual)
        
        st.session_state.valores['equip_cond'] = precos['equip_cond']
        st.session_state.valores['equip_evap'] = precos['equip_evap']
        st.session_state.valores['ins_cobre'] = precos['ins_cobre']
        st.session_state.valores['mao_tec'] = precos['mao_tec']
        st.session_state.valores['serv_startup'] = precos['serv_startup']
        
        st.success("✅ Dados aplicados! Role para baixo para ver o orçamento.")
        st.rerun()

with tab_exemplo:
    st.subheader("📋 Exemplos de descrição que funcionam bem")
    
    ex1, ex2 = st.tabs(["VRF/VRV", "Água Gelada"])
    
    with ex1:
        st.code("""
Projeto de climatização para edifício comercial:
- Área total: 850 m²
- Sistema VRF/VRV
- Carga térmica: 28.5 TR
- 12 evaporadoras tipo cassete
- Tubulação de cobre com isolamento térmico
- Incluir startup e comissionamento do sistema
- Necessário integração com BMS
        """)
    
    with ex2:
        st.code("""
Sistema de água gelada para shopping center:
- Área climatizada: 2500 m²
- Chiller de 120 TR
- 45 fan coils tipo cassete
- Torre de resfriamento
- Comissionamento completo
        """)
    
    st.info("💡 **Dica:** Cole uma descrição similar e clique em 'Analisar Projeto' para preencher automaticamente os valores.")

# ========== LINHA DIVISÓRIA ==========
st.markdown("---")
st.header("💰 ORÇAMENTO (atualiza em tempo real)")

# ========== COLUNAS DE EDIÇÃO ==========
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 MODELO DIRETO")
    
    with st.expander("📦 Equipamentos", expanded=True):
        st.session_state.valores['equip_cond'] = st.number_input("Condensadoras/Chiller", value=st.session_state.valores['equip_cond'], step=5000.0)
        st.session_state.valores['equip_evap'] = st.number_input("Evaporadoras/Fan Coils", value=st.session_state.valores['equip_evap'], step=5000.0)
        st.session_state.valores['equip_bms'] = st.number_input("BMS/Controles", value=st.session_state.valores['equip_bms'], step=1000.0)
    
    with st.expander("🔩 Insumos", expanded=True):
        st.session_state.valores['ins_cobre'] = st.number_input("Cobre + Isolante", value=st.session_state.valores['ins_cobre'], step=1000.0)
        st.session_state.valores['ins_drenos'] = st.number_input("Drenos + Eletrodutos", value=st.session_state.valores['ins_drenos'], step=500.0)
        st.session_state.valores['ins_outros'] = st.number_input("Outros insumos", value=st.session_state.valores['ins_outros'], step=500.0)
    
    with st.expander("👷 Mão de Obra", expanded=True):
        st.session_state.valores['mao_tec'] = st.number_input("Técnicos", value=st.session_state.valores['mao_tec'], step=2000.0)
        st.session_state.valores['mao_aux'] = st.number_input("Auxiliares", value=st.session_state.valores['mao_aux'], step=1000.0)
        st.session_state.valores['mao_eng'] = st.number_input("Engenharia/Projeto", value=st.session_state.valores['mao_eng'], step=1000.0)
    
    with st.expander("⚙️ Serviços", expanded=True):
        st.session_state.valores['serv_startup'] = st.number_input("Startup/Comissionamento", value=st.session_state.valores['serv_startup'], step=500.0)
        st.session_state.valores['serv_testes'] = st.number_input("Testes + Carga de gás", value=st.session_state.valores['serv_testes'], step=500.0)
    
    col_perc1, col_perc2, col_perc3 = st.columns(3)
    with col_perc1:
        st.session_state.valores['garantia'] = st.number_input("Garantia %", value=st.session_state.valores['garantia'], step=0.5)
    with col_perc2:
        st.session_state.valores['adm'] = st.number_input("Adm/Frete %", value=st.session_state.valores['adm'], step=0.5)
    with col_perc3:
        st.session_state.valores['margem_dir'] = st.number_input("Margem %", value=st.session_state.valores['margem_dir'], step=1.0)

with col2:
    st.subheader("🎯 MODELO TERCEIRO")
    
    st.session_state.valores['fornece_equip'] = st.checkbox("Você fornece equipamentos?", value=st.session_state.valores['fornece_equip'])
    if st.session_state.valores['fornece_equip']:
        st.session_state.valores['valor_equip_terc'] = st.number_input("Valor equipamentos", value=st.session_state.valores['valor_equip_terc'] or (st.session_state.valores['equip_cond'] + st.session_state.valores['equip_evap']), step=5000.0)
    
    st.session_state.valores['fornece_insumos'] = st.checkbox("Você fornece insumos?", value=st.session_state.valores['fornece_insumos'])
    if st.session_state.valores['fornece_insumos']:
        st.session_state.valores['valor_insumos_terc'] = st.number_input("Valor insumos", value=st.session_state.valores['valor_insumos_terc'] or st.session_state.valores['ins_cobre'], step=2000.0)
    
    st.markdown("---")
    st.session_state.valores['mao_terc'] = st.number_input("Mão de obra", value=st.session_state.valores['mao_terc'], step=2000.0)
    st.session_state.valores['consumiveis'] = st.number_input("Consumíveis", value=st.session_state.valores['consumiveis'], step=500.0)
    st.session_state.valores['startup_terc'] = st.number_input("Startup", value=st.session_state.valores['startup_terc'], step=500.0)
    st.session_state.valores['margem_terc'] = st.number_input("Margem Terceiro %", value=st.session_state.valores['margem_terc'], step=1.0)

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
if resultados['lucro_dir'] > resultados['lucro_terc']:
    st.success(f"✅ **Recomendação:** Modelo DIRETO é R$ {resultados['lucro_dir'] - resultados['lucro_terc']:,.2f} mais lucrativo")
else:
    st.info(f"ℹ️ **Recomendação:** Modelo TERCEIRO tem lucro de R$ {resultados['lucro_terc']:,.2f} com menos risco")

st.caption("💡 **Qualquer alteração nos valores atualiza os preços automaticamente!**")
st.caption("📌 **PDF e DWG:** Para extração avançada de DWG, considere a versão profissional com integração CAD.") 
