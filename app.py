import streamlit as st
import pandas as pd
import re
from datetime import datetime
import tempfile
import os

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

def calcular_precos_por_analise(analise):
    """Calcula valores sugeridos baseados na analise"""
    sistema = analise["sistema"]
    carga = analise["carga_tr"] if analise["carga_tr"] else 20.0
    qtd_evap = analise["qtd_evaporadoras"] if analise["qtd_evaporadoras"] else 8
    metros_tubo = analise["metros_tubo"] if analise["metros_tubo"] else int(carga * 15)
    
    if sistema == "VRF/VRV":
        equip_cond = float(carga * 3500)
        equip_evap = float(qtd_evap * 4200)
        mao_tec = float(carga * 800)
        tubulacao = float(metros_tubo * 63)
        startup = 3500.0
    elif sistema == "Agua Gelada":
        equip_cond = float(carga * 2800)
        equip_evap = float(qtd_evap * 2500)
        mao_tec = float(carga * 700)
        tubulacao = float(metros_tubo * 82)
        startup = 4500.0
    else:
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

# Inicializar session state
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

# Interface principal
st.header("Upload do Projeto para Analise Automatica")

tab_upload, tab_manual, tab_info = st.tabs(["Upload de Arquivo", "Preenchimento Manual", "Informacoes"])

with tab_upload:
    st.subheader("Faça upload do arquivo do projeto")
    
    arquivo = st.file_uploader(
        "Selecione o arquivo",
        type=['txt', 'pdf', 'csv', 'xlsx'],
        help="Formatos suportados: TXT, PDF, CSV, XLSX"
    )
    
    if arquivo:
        st.info(f"Arquivo: {arquivo.name}")
        texto_extraido = None
        
        try:
            if arquivo.name.endswith('.txt'):
                texto_extraido = arquivo.read().decode('utf-8')
                st.success("Arquivo TXT carregado com sucesso!")
            
            elif arquivo.name.endswith('.pdf'):
                try:
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(arquivo)
                    texto_extraido = ""
                    for pagina in pdf_reader.pages:
                        texto_pagina = pagina.extract_text()
                        if texto_pagina:
                            texto_extraido += texto_pagina + " "
                    st.success("PDF processado com sucesso!")
                except ImportError:
                    st.error("Biblioteca PDF nao disponivel. Use arquivo TXT.")
                except Exception as e:
                    st.error(f"Erro ao ler PDF: {str(e)[:100]}")
            
            elif arquivo.name.endswith('.csv'):
                try:
                    df = pd.read_csv(arquivo)
                    texto_extraido = df.to_string()
                    st.success("CSV processado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao ler CSV: {str(e)[:100]}")
            
            elif arquivo.name.endswith('.xlsx'):
                try:
                    df = pd.read_excel(arquivo, engine='openpyxl')
                    texto_extraido = df.to_string()
                    st.success("Excel processado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao ler Excel: {str(e)[:100]}. Verifique se o arquivo nao esta corrompido.")
            
            if texto_extraido and st.button("Extrair informacoes", use_container_width=True):
                with st.spinner("Analisando dados..."):
                    analise = extrair_informacoes(texto_extraido)
                    
                    if analise:
                        st.subheader("Informacoes extraidas:")
                        col_a1, col_a2 = st.columns(2)
                        with col_a1:
                            st.metric("Sistema", analise["sistema"])
                            st.metric("Area (m²)", analise["area_m2"] if analise["area_m2"] else "nao detectado")
                            st.metric("Carga (TR)", analise["carga_tr"] if analise["carga_tr"] else "nao detectado")
                        with col_a2:
                            st.metric("Evaporadoras", analise["qtd_evaporadoras"] if analise["qtd_evaporadoras"] else "nao detectado")
                            st.metric("Tubulacao (m)", analise["metros_tubo"] if analise["metros_tubo"] else "nao detectado")
                            if analise["servicos_extras"]:
                                st.write("Servicos:", ", ".join(analise["servicos_extras"]))
                        
                        if analise["carga_tr"] or analise["area_m2"]:
                            precos = calcular_precos_por_analise(analise)
                            st.session_state.valores['equip_cond'] = precos['equip_cond']
                            st.session_state.valores['equip_evap'] = precos['equip_evap']
                            st.session_state.valores['ins_cobre'] = precos['ins_cobre']
                            st.session_state.valores['mao_tec'] = precos['mao_tec']
                            st.session_state.valores['serv_startup'] = precos['serv_startup']
                            
                            st.success("Valores sugeridos aplicados ao orcamento!")
                            st.rerun()
                    else:
                        st.warning("Nao foi possivel extrair dados. Use preenchimento manual.")
        
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {str(e)[:200]}")

with tab_manual:
    st.subheader("Preencha os dados manualmente")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        sistema_manual = st.selectbox("Sistema", ["VRF/VRV", "Agua Gelada", "Split"])
        area_manual = st.number_input("Area (m²)", value=850, step=50)
        carga_manual = st.number_input("Carga (TR)", value=28.5, step=1.0)
    with col_m2:
        qtd_evap_manual = st.number_input("Quantidade de evaporadoras", value=12, step=1)
        metros_tubo_manual = st.number_input("Metros de tubulacao", value=int(carga_manual * 15), step=50)
    
    if st.button("Aplicar dados manuais", use_container_width=True):
        analise_manual = {
            "sistema": sistema_manual,
            "carga_tr": float(carga_manual),
            "qtd_evaporadoras": int(qtd_evap_manual),
            "metros_tubo": int(metros_tubo_manual),
            "area_m2": int(area_manual),
            "servicos_extras": []
        }
        precos = calcular_precos_por_analise(analise_manual)
        
        st.session_state.valores['equip_cond'] = precos['equip_cond']
        st.session_state.valores['equip_evap'] = precos['equip_evap']
        st.session_state.valores['ins_cobre'] = precos['ins_cobre']
        st.session_state.valores['mao_tec'] = precos['mao_tec']
        st.session_state.valores['serv_startup'] = precos['serv_startup']
        
        st.success("Dados aplicados!")
        st.rerun()

with tab_info:
    st.subheader("Formatos suportados")
    st.markdown("""
    **Formatos de arquivo:**
    - **TXT:** Texto puro com descricao do projeto
    - **PDF:** Extrai texto automaticamente
    - **CSV:** Leitura de planilhas CSV
    - **XLSX:** Leitura de Excel
    
    **O sistema procura por:**
    - Sistema: VRF, Agua Gelada, Split
    - Area: numeros seguidos de m2
    - Carga: numeros seguidos de TR ou BTU
    - Evaporadoras: numeros seguidos de evaporadoras
    
    **Exemplo de descricao:**
