import streamlit as st
import re
from datetime import datetime

st.set_page_config(page_title="IA Orçamentos Climatização", page_icon="🌡️", layout="wide")

st.title("🌡️ IA Orçamentos Climatização - Análise de Projetos")
st.caption(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
st.markdown("---")

def extrair_informacoes(texto):
    """Extrai informações do texto do projeto"""
    if not texto:
        return None
    
    texto_lower = texto.lower()
    
    resultado = {
        "sistema": "VRF/VRV",
        "area_m2": None,
        "carga_tr": None,
        "qtd_evaporadoras": None,
        "metros_tubo": None,
        "servicos_extras": []
    }
    
    if "agua gelada" in texto_lower or "chiller" in texto_lower:
        resultado["sistema"] = "Agua Gelada"
    elif "vrf" in texto_lower or "vrv" in texto_lower:
        resultado["sistema"] = "VRF/VRV"
    elif "split" in texto_lower:
        resultado["sistema"] = "Split"
    
    area_match = re.search(r'(\d+)\s*m[²2]', texto_lower)
    if area_match:
        resultado["area_m2"] = int(area_match.group(1))
    
    tr_match = re.search(r'(\d+(?:\.\d+)?)\s*tr', texto_lower)
    if tr_match:
        resultado["carga_tr"] = float(tr_match.group(1))
    
    btu_match = re.search(r'(\d+)\s*btu', texto_lower)
    if btu_match and not resultado["carga_tr"]:
        resultado["carga_tr"] = round(int(btu_match.group(1)) / 12000, 1)
    
    evap_match = re.search(r'(\d+)\s*evaporadoras?', texto_lower)
    if evap_match:
        resultado["qtd_evaporadoras"] = int(evap_match.group(1))
    
    tubo_match = re.search(r'(\d+)\s*metros?\s*de\s*tubula', texto_lower)
    if tubo_match:
        resultado["metros_tubo"] = int(tubo_match.group(1))
    
    if "startup" in texto_lower or "comissionamento" in texto_lower:
        resultado["servicos_extras"].append("Startup/Comissionamento")
    if "bms" in texto_lower:
        resultado["servicos_extras"].append("BMS/Automacao")
    
    return resultado

def calcular_precos_sugeridos(analise):
    sistema = analise["sistema"]
    carga = analise["carga_tr"] if analise["carga_tr"] else 20.0
    qtd_evap = analise["qtd_evaporadoras"] if analise["qtd_evaporadoras"] else 8
    metros_tubo = analise["metros_tubo"] if analise["metros_tubo"] else int(carga * 15)
    
    if sistema == "VRF/VRV":
        equip_cond = carga * 3500
        equip_evap = qtd_evap * 4200
        mao_tec = carga * 800
        tubulacao = metros_tubo * 63
        startup = 3500
    elif sistema == "Agua Gelada":
        equip_cond = carga * 2800
        equip_evap = qtd_evap * 2500
        mao_tec = carga * 700
        tubulacao = metros_tubo * 82
        startup = 4500
    else:
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
        "serv_startup": startup
    }

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

st.header("Analise Automatica do Projeto")

tab1, tab2, tab3 = st.tabs(["Digitar Descricao", "Preenchimento Manual", "Ajuda"])

with tab1:
    st.subheader("Cole a descricao do projeto")
    
    descricao = st.text_area(
        "Descricao:",
        height=150,
        placeholder="Exemplo: Projeto para escritorio de 850m2. Sistema VRF com 28.5 TR. 12 evaporadoras. Incluir startup."
    )
    
    if st.button("Analisar Projeto", use_container_width=True):
        if descricao:
            with st.spinner("Analisando..."):
                analise = extrair_informacoes(descricao)
                if analise:
                    st.success("Projeto analisado!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Sistema", analise["sistema"])
                        st.metric("Area", f"{analise['area_m2']} m2" if analise["area_m2"] else "nao detectado")
                    with col2:
                        st.metric("Carga", f"{analise['carga_tr']} TR" if analise["carga_tr"] else "nao detectado")
                        st.metric("Evaporadoras", analise["qtd_evaporadoras"] if analise["qtd_evaporadoras"] else "nao detectado")
                    
                    if analise["carga_tr"] or analise["area_m2"]:
                        precos = calcular_precos_sugeridos(analise)
                        st.session_state.valores['equip_cond'] = float(precos['equip_cond'])
                        st.session_state.valores['equip_evap'] = float(precos['equip_evap'])
                        st.session_state.valores['ins_cobre'] = float(precos['ins_cobre'])
                        st.session_state.valores['mao_tec'] = float(precos['mao_tec'])
                        st.session_state.valores['serv_startup'] = float(precos['serv_startup'])
                        st.success("Valores sugeridos aplicados!")
                        st.rerun()
        else:
            st.warning("Digite uma descricao")

with tab2:
    st.subheader("Preenchimento Manual")
    
    col_a, col_b = st.columns(2)
    with col_a:
        sistema_manual = st.selectbox("Sistema", ["VRF/VRV", "Agua Gelada", "Split"])
        area_manual = st.number_input("Area (m2)", value=850, step=50)
    with col_b:
        carga_manual = st.number_input("Carga (TR)", value=28.5, step=1.0)
        qtd_manual = st.number_input("Evaporadoras", value=12, step=1)
    
    if st.button("Aplicar Dados", use_container_width=True):
        analise = {
            "sistema": sistema_manual,
            "carga_tr": float(carga_manual),
            "qtd_evaporadoras": int(qtd_manual),
            "area_m2": int(area_manual),
            "metros_tubo": int(carga_manual * 15),
            "servicos_extras": []
        }
        precos = calcular_precos_sugeridos(analise)
        st.session_state.valores['equip_cond'] = float(precos['equip_cond'])
        st.session_state.valores['equip_evap'] = float(precos['equip_evap'])
        st.session_state.valores['ins_cobre'] = float(precos['ins_cobre'])
        st.session_state.valores['mao_tec'] = float(precos['mao_tec'])
        st.session_state.valores['serv_startup'] = float(precos['serv_startup'])
        st.success("Dados aplicados!")
        st.rerun()

with tab3:
    st.markdown("""
    **Como usar:**
    
    1. Digite a descricao do projeto na primeira aba
    2. O sistema extrai automaticamente as informacoes
    3. Ajuste os valores no orcamento abaixo
    
    **Exemplo de descricao:**
