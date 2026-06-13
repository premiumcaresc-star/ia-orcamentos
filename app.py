import streamlit as st
import pandas as pd
import re
from datetime import datetime
import tempfile 
import os

# Tentar importar bibliotecas para PDF
try:
    import PyPDF2
    PDF_SUPORTE = True
except ImportError:
    PDF_SUPORTE = False

# Tentar importar bibliotecas para DWG
try:
    import ezdxf
    DWG_SUPORTE = True
except ImportError:
    DWG_SUPORTE = False

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
    
    # Detectar sistema
    if "agua gelada" in texto_lower or "chiller" in texto_lower:
        resultado["sistema"] = "Agua Gelada"
    elif "vrf" in texto_lower or "vrv" in texto_lower:
        resultado["sistema"] = "VRF/VRV"
    elif "split" in texto_lower:
        resultado["sistema"] = "Split"
    
    # Extrair area
    area_match = re.search(r'(\d+)\s*m[²2]', texto_lower)
    if area_match:
        resultado["area_m2"] = int(area_match.group(1))
    
    # Extrair carga
    tr_match = re.search(r'(\d+(?:\.\d+)?)\s*tr', texto_lower)
    if tr_match:
        resultado["carga_tr"] = float(tr_match.group(1))
    
    btu_match = re.search(r'(\d+)\s*btu', texto_lower)
    if btu_match and not resultado["carga_tr"]:
        resultado["carga_tr"] = round(int(btu_match.group(1)) / 12000, 1)
    
    # Extrair evaporadoras
    evap_match = re.search(r'(\d+)\s*evaporadoras?', texto_lower)
    if evap_match:
        resultado["qtd_evaporadoras"] = int(evap_match.group(1))
    
    # Extrair tubulacao
    tubo_match = re.search(r'(\d+)\s*metros?\s*de\s*tubula', texto_lower)
    if tubo_match:
        resultado["metros_tubo"] = int(tubo_match.group(1))
    
    # Servicos extras
    if "startup" in texto_lower or "comissionamento" in texto_lower:
        resultado["servicos_extras"].append("Startup/Comissionamento")
    if "bms" in texto_lower:
        resultado["servicos_extras"].append("BMS/Automacao")
    if "solda" in texto_lower:
        resultado["servicos_extras"].append("Solda Especializada")
    
    return resultado

def extrair_de_pdf(arquivo):
    """Extrai texto de arquivo PDF"""
    try:
        if not PDF_SUPORTE:
            return None
        pdf_reader = PyPDF2.PdfReader(arquivo)
        texto_completo = ""
        for pagina in pdf_reader.pages:
            texto = pagina.extract_text()
            if texto:
                texto_completo += texto + " "
        return texto_completo if texto_completo else None
    except Exception as e:
        st.warning(f"Erro ao ler PDF: {str(e)[:100]}")
        return None

def extrair_de_dwg(arquivo):
    """Extrai informacoes de arquivo DWG/DXF"""
    try:
        if not DWG_SUPORTE:
            return None
        
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp_file:
            tmp_file.write(arquivo.getvalue())
            tmp_path = tmp_file.name
        
        # Ler arquivo DXF
        doc = ezdxf.readfile(tmp_path)
        
        # Extrair texto do DWG
        textos_encontrados = []
        for entity in doc.modelspace().query('TEXT'):
            if entity.dxf.text:
                textos_encontrados.append(entity.dxf.text)
        for entity in doc.modelspace().query('MTEXT'):
            if entity.text:
                textos_encontrados.append(entity.text)
        
        # Limpar arquivo temporario
        os.unlink(tmp_path)
        
        texto_completo = " ".join(textos_encontrados)
        return texto_completo if texto_completo else None
    except Exception as e:
        st.warning(f"Erro ao ler DWG/DXF: {str(e)[:100]}")
        return None

def processar_arquivo(arquivo):
    """Processa arquivo e extrai informações"""
    nome = arquivo.name.lower()
    texto = ""
    
    # Arquivos de texto
    if nome.endswith('.txt'):
        texto = arquivo.read().decode('utf-8')
    
    # Arquivos PDF
    elif nome.endswith('.pdf'):
        with st.spinner("Extraindo texto do PDF..."):
            texto = extrair_de_pdf(arquivo)
            if not texto:
                st.warning("Nao foi possivel extrair texto do PDF. Use arquivo TXT.")
                return None
    
    # Arquivos DWG/DXF
    elif nome.endswith(('.dwg', '.dxf')):
        with st.spinner("Extraindo informacoes do DWG/DXF..."):
            texto = extrair_de_dwg(arquivo)
            if not texto:
                st.warning("Nao foi possivel extrair texto do DWG. Use descricao manual.")
                return None
    
    # Planilhas
    elif nome.endswith(('.csv', '.xlsx')):
        try:
            if nome.endswith('.csv'):
                df = pd.read_csv(arquivo)
            else:
                df = pd.read_excel(arquivo)
            texto = df.to_string()
        except Exception as e:
            st.warning(f"Erro ao ler planilha: {e}")
            return None
    
    if texto:
        return extrair_informacoes(texto)
    return None

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
        type=['pdf', 'dwg', 'dxf', 'txt', 'csv', 'xlsx'],
        help="Formatos suportados: PDF, DWG, DXF, TXT, CSV, XLSX"
    )
    
    if arquivo:
        st.info(f"Arquivo: {arquivo.name} ({arquivo.size} bytes)")
        
        if st.button("Extrair informacoes automaticamente", use_container_width=True):
            with st.spinner("Processando arquivo..."):
                analise = processar_arquivo(arquivo)
                
                if analise:
                    st.success("Arquivo processado com sucesso!")
                    
                    st.subheader("Informacoes extraidas:")
                    col_a1, col_a2, col_a3 = st.columns(3)
                    with col_a1:
                        st.metric("Sistema", analise["sistema"])
                        area_str = str(analise["area_m2"]) if analise["area_m2"] else "nao detectado"
                        st.metric("Area (m²)", area_str)
                    with col_a2:
                        carga_str = str(analise["carga_tr"]) if analise["carga_tr"] else "nao detectado"
                        st.metric("Carga (TR)", carga_str)
                        evap_str = str(analise["qtd_evaporadoras"]) if analise["qtd_evaporadoras"] else "nao detectado"
                        st.metric("Evaporadoras", evap_str)
                    with col_a3:
                        tubo_str = str(analise["metros_tubo"]) if analise["metros_tubo"] else "nao detectado"
                        st.metric("Tubulacao (m)", tubo_str)
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
                    st.error("Nao foi possivel extrair dados do arquivo.")

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
    **PDF:** Extrai texto automaticamente de arquivos PDF.
    
    **DWG/DXF:** Extrai textos de arquivos CAD (camadas TEXT e MTEXT).
    
    **TXT:** Leitura direta de arquivos de texto.
    
    **CSV/XLSX:** Leitura de planilhas Excel/CSV.
    
    **O sistema procura por:**
    - Sistema: VRF, Agua Gelada, Split
    - Area: numeros seguidos de m2
    - Carga: numeros seguidos de TR ou BTU
    - Evaporadoras: numeros seguidos de evaporadoras
    """)

# Orcamento
st.markdown("---")
st.header("Orcamento (atualiza em tempo real)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Modelo Direto")
    
    with st.expander("Equipamentos", expanded=True):
        st.session_state.valores['equip_cond'] = st.number_input("Condensadoras/Chiller", value=st.session_state.valores['equip_cond'], step=5000.0)
        st.session_state.valores['equip_evap'] = st.number_input("Evaporadoras/Fan Coils", value=st.session_state.valores['equip_evap'], step=5000.0)
        st.session_state.valores['equip_bms'] = st.number_input("BMS/Controles", value=st.session_state.valores['equip_bms'], step=1000.0)
    
    with st.expander("Insumos", expanded=True):
        st.session_state.valores['ins_cobre'] = st.number_input("Cobre + Isolante", value=st.session_state.valores['ins_cobre'], step=1000.0)
        st.session_state.valores['ins_drenos'] = st.number_input("Drenos + Eletrodutos", value=st.session_state.valores['ins_drenos'], step=500.0)
        st.session_state.valores['ins_outros'] = st.number_input("Outros insumos", value=st.session_state.valores['ins_outros'], step=500.0)
    
    with st.expander("Mao de Obra", expanded=True):
        st.session_state.valores['mao_tec'] = st.number_input("Tecnicos", value=st.session_state.valores['mao_tec'], step=2000.0)
        st.session_state.valores['mao_aux'] = st.number_input("Auxiliares", value=st.session_state.valores['mao_aux'], step=1000.0)
        st.session_state.valores['mao_eng'] = st.number_input("Engenharia/Projeto", value=st.session_state.valores['mao_eng'], step=1000.0)
    
    with st.expander("Servicos", expanded=True):
        st.session_state.valores['serv_startup'] = st.number_input("Startup/Comissionamento", value=st.session_state.valores['serv_startup'], step=500.0)
        st.session_state.valores['serv_testes'] = st.number_input("Testes + Carga de gas", value=st.session_state.valores['serv_testes'], step=500.0)
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.session_state.valores['garantia'] = st.number_input("Garantia %", value=st.session_state.valores['garantia'], step=0.5)
    with col_p2:
        st.session_state.valores['adm'] = st.number_input("Adm/Frete %", value=st.session_state.valores['adm'], step=0.5)
    with col_p3:
        st.session_state.valores['margem_dir'] = st.number_input("Margem %", value=st.session_state.valores['margem_dir'], step=1.0)

with col2:
    st.subheader("Modelo Terceiro")
    
    st.session_state.valores['fornece_equip'] = st.checkbox("Voce fornece equipamentos?", value=st.session_state.valores['fornece_equip'])
    if st.session_state.valores['fornece_equip']:
        valor_padrao = st.session_state.valores['equip_cond'] + st.session_state.valores['equip_evap']
        st.session_state.valores['valor_equip_terc'] = st.number_input("Valor equipamentos", value=valor_padrao, step=5000.0)
    
    st.session_state.valores['fornece_insumos'] = st.checkbox("Voce fornece insumos?", value=st.session_state.valores['fornece_insumos'])
    if st.session_state.valores['fornece_insumos']:
        st.session_state.valores['valor_insumos_terc'] = st.number_input("Valor insumos", value=st.session_state.valores['ins_cobre'], step=2000.0)
    
    st.markdown("---")
    st.session_state.valores['mao_terc'] = st.number_input("Mao de obra", value=st.session_state.valores['mao_terc'], step=2000.0)
    st.session_state.valores['consumiveis'] = st.number_input("Consumiveis", value=st.session_state.valores['consumiveis'], step=500.0)
    st.session_state.valores['startup_terc'] = st.number_input("Startup", value=st.session_state.valores['startup_terc'], step=500.0)
    st.session_state.valores['margem_terc'] = st.number_input("Margem Terceiro %", value=st.session_state.valores['margem_terc'], step=1.0)

resultados = calcular_tudo()

st.markdown("---")
col_res1, col_res2 = st.columns(2)

with col_res1:
    st.subheader("Resultado Direto")
    st.metric("Seu Custo Total", f"R$ {resultados['custo_total_dir']:,.2f}")
    st.metric("Preco para Cliente", f"R$ {resultados['preco_cliente']:,.2f}")
    st.metric("Seu Lucro", f"R$ {resultados['lucro_dir']:,.2f}")

with col_res2:
    st.subheader("Resultado Terceiro")
    st.metric("Seu Custo Total", f"R$ {resultados['custo_total_terc']:,.2f}")
    st.metric("Preco para Construtora", f"R$ {resultados['preco_terc']:,.2f}")
    st.metric("Seu Lucro", f"R$ {resultados['lucro_terc']:,.2f}")

st.markdown("---")
diferenca = resultados['lucro_dir'] - resultados['lucro_terc']
if diferenca > 0:
    st.success(f"Recomendacao: Modelo DIRETO e R$ {diferenca:,.2f} mais lucrativo")
else:
    st.info(f"Recomendacao: Modelo TERCEIRO tem lucro de R$ {resultados['lucro_terc']:,.2f} com menos risco")

st.caption("Upload de PDF, DWG, DXF, TXT ou planilhas - O sistema extrai automaticamente as informacoes do projeto!")
