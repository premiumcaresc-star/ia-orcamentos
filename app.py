import streamlit as st
import re
from datetime import datetime

st.set_page_config(page_title="IA Orçamentos Climatização", page_icon="🌡️", layout="wide")

st.title("🌡️ IA Orçamentos Climatização")
st.caption(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
st.markdown("---")

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

def extrair_dados(texto):
    """Extrai dados do texto"""
    texto = texto.lower()
    dados = {}
    
    # Area
    match = re.search(r'(\d+)\s*m[²2]', texto)
    if match:
        dados['area'] = int(match.group(1))
    
    # Carga
    match = re.search(r'(\d+(?:\.\d+)?)\s*tr', texto)
    if match:
        dados['carga'] = float(match.group(1))
    
    # Evaporadoras
    match = re.search(r'(\d+)\s*evap', texto)
    if match:
        dados['evap'] = int(match.group(1))
    
    # Sistema
    if 'agua gelada' in texto or 'chiller' in texto:
        dados['sistema'] = 'Agua Gelada'
    elif 'vrf' in texto or 'vrv' in texto:
        dados['sistema'] = 'VRF/VRV'
    else:
        dados['sistema'] = 'VRF/VRV'
    
    return dados

# Função para calcular resultados
def calcular():
    v = st.session_state.valores
    
    # Direto
    custo_equip = v['equip_cond'] + v['equip_evap'] + v['equip_bms']
    custo_insumos = v['ins_cobre'] + v['ins_drenos'] + v['ins_outros']
    custo_mao = v['mao_tec'] + v['mao_aux'] + v['mao_eng']
    custo_serv = v['serv_startup'] + v['serv_testes']
    custo_dir = custo_equip + custo_insumos + custo_mao + custo_serv
    
    preco_cliente = custo_dir * (1 + v['garantia']/100 + v['adm']/100) * (1 + v['margem_dir']/100)
    lucro_dir = preco_cliente - (custo_dir * (1 + v['garantia']/100 + v['adm']/100))
    
    # Terceiro
    custo_terc = v['mao_terc'] + v['consumiveis'] + v['startup_terc'] + v['valor_equip_terc'] + v['valor_insumos_terc']
    preco_terc = custo_terc * (1 + v['margem_terc']/100)
    lucro_terc = preco_terc - custo_terc
    
    return {
        'custo_dir': custo_dir,
        'preco_cliente': preco_cliente,
        'lucro_dir': lucro_dir,
        'custo_terc': custo_terc,
        'preco_terc': preco_terc,
        'lucro_terc': lucro_terc
    }

# Interface
st.header("Analise do Projeto")

aba1, aba2 = st.tabs(["Digitar Descricao", "Editar Valores"])

with aba1:
    st.subheader("Cole a descricao do projeto")
    
    exemplo = """Projeto para edificio comercial de 850m2.
Sistema VRF com 28.5 TR de carga.
12 evaporadoras tipo cassete.
Incluir startup."""
    
    descricao = st.text_area("Descricao:", height=150, placeholder=exemplo)
    
    if st.button("Analisar e Aplicar", use_container_width=True):
        if descricao:
            dados = extrair_dados(descricao)
            
            if dados:
                st.success("Dados extraidos!")
                
                col1, col2 = st.columns(2)
                with col1:
                    if 'area' in dados:
                        st.metric("Area", f"{dados['area']} m2")
                    if 'carga' in dados:
                        st.metric("Carga", f"{dados['carga']} TR")
                with col2:
                    if 'evap' in dados:
                        st.metric("Evaporadoras", f"{dados['evap']} un")
                    if 'sistema' in dados:
                        st.metric("Sistema", dados['sistema'])
                
                # Aplicar valores sugeridos
                if 'carga' in dados:
                    carga = dados['carga']
                    qtd_evap = dados.get('evap', 8)
                    
                    st.session_state.valores['equip_cond'] = float(carga * 3500)
                    st.session_state.valores['equip_evap'] = float(qtd_evap * 4200)
                    st.session_state.valores['ins_cobre'] = float(carga * 15 * 63)
                    st.session_state.valores['mao_tec'] = float(carga * 800)
                    st.session_state.valores['serv_startup'] = 3500.0
                    
                    st.success("Valores sugeridos aplicados! Vá para a aba Editar Valores para ajustar.")
                    st.rerun()
            else:
                st.warning("Nao foi possivel extrair dados. Use o formato de exemplo.")
        else:
            st.warning("Digite uma descricao")

with aba2:
    st.subheader("Ajuste os valores manualmente")
    
    colA, colB = st.columns(2)
    
    with colA:
        st.markdown("**Equipamentos**")
        st.session_state.valores['equip_cond'] = st.number_input("Condensadoras", value=st.session_state.valores['equip_cond'], step=5000.0, key="eq1")
        st.session_state.valores['equip_evap'] = st.number_input("Evaporadoras", value=st.session_state.valores['equip_evap'], step=5000.0, key="eq2")
        st.session_state.valores['equip_bms'] = st.number_input("BMS/Controles", value=st.session_state.valores['equip_bms'], step=1000.0, key="eq3")
        
        st.markdown("**Insumos**")
        st.session_state.valores['ins_cobre'] = st.number_input("Cobre + Isolante", value=st.session_state.valores['ins_cobre'], step=1000.0, key="in1")
        st.session_state.valores['ins_drenos'] = st.number_input("Drenos + Eletrodutos", value=st.session_state.valores['ins_drenos'], step=500.0, key="in2")
        st.session_state.valores['ins_outros'] = st.number_input("Outros insumos", value=st.session_state.valores['ins_outros'], step=500.0, key="in3")
    
    with colB:
        st.markdown("**Mao de Obra**")
        st.session_state.valores['mao_tec'] = st.number_input("Tecnicos", value=st.session_state.valores['mao_tec'], step=2000.0, key="mo1")
        st.session_state.valores['mao_aux'] = st.number_input("Auxiliares", value=st.session_state.valores['mao_aux'], step=1000.0, key="mo2")
        st.session_state.valores['mao_eng'] = st.number_input("Engenharia", value=st.session_state.valores['mao_eng'], step=1000.0, key="mo3")
        
        st.markdown("**Servicos**")
        st.session_state.valores['serv_startup'] = st.number_input("Startup", value=st.session_state.valores['serv_startup'], step=500.0, key="se1")
        st.session_state.valores['serv_testes'] = st.number_input("Testes", value=st.session_state.valores['serv_testes'], step=500.0, key="se2")
    
    st.markdown("---")
    
    colP1, colP2, colP3 = st.columns(3)
    with colP1:
        st.session_state.valores['garantia'] = st.number_input("Garantia %", value=st.session_state.valores['garantia'], step=0.5, key="pc1")
    with colP2:
        st.session_state.valores['adm'] = st.number_input("Adm/Frete %", value=st.session_state.valores['adm'], step=0.5, key="pc2")
    with colP3:
        st.session_state.valores['margem_dir'] = st.number_input("Margem Direto %", value=st.session_state.valores['margem_dir'], step=1.0, key="pc3")
    
    st.markdown("---")
    st.markdown("**Modelo Terceiro**")
    
    colT1, colT2 = st.columns(2)
    with colT1:
        st.session_state.valores['fornece_equip'] = st.checkbox("Fornece equipamentos?", value=st.session_state.valores['fornece_equip'], key="te1")
        if st.session_state.valores['fornece_equip']:
            st.session_state.valores['valor_equip_terc'] = st.number_input("Valor equipamentos", value=st.session_state.valores['equip_cond'] + st.session_state.valores['equip_evap'], step=5000.0, key="te2")
    
    with colT2:
        st.session_state.valores['fornece_insumos'] = st.checkbox("Fornece insumos?", value=st.session_state.valores['fornece_insumos'], key="te3")
        if st.session_state.valores['fornece_insumos']:
            st.session_state.valores['valor_insumos_terc'] = st.number_input("Valor insumos", value=st.session_state.valores['ins_cobre'], step=2000.0, key="te4")
    
    colT3, colT4 = st.columns(2)
    with colT3:
        st.session_state.valores['mao_terc'] = st.number_input("Mao de obra", value=st.session_state.valores['mao_terc'], step=2000.0, key="te5")
        st.session_state.valores['consumiveis'] = st.number_input("Consumiveis", value=st.session_state.valores['consumiveis'], step=500.0, key="te6")
    with colT4:
        st.session_state.valores['startup_terc'] = st.number_input("Startup", value=st.session_state.valores['startup_terc'], step=500.0, key="te7")
        st.session_state.valores['margem_terc'] = st.number_input("Margem Terceiro %", value=st.session_state.valores['margem_terc'], step=1.0, key="te8")

# Resultados
resultados = calcular()

st.markdown("---")
st.header("Resultados")

colR1, colR2 = st.columns(2)

with colR1:
    st.subheader("Modelo Direto")
    st.metric("Custo Total", f"R$ {resultados['custo_dir']:,.2f}")
    st.metric("Preco ao Cliente", f"R$ {resultados['preco_cliente']:,.2f}")
    st.metric("Lucro", f"R$ {resultados['lucro_dir']:,.2f}")

with colR2:
    st.subheader("Modelo Terceiro")
    st.metric("Custo Total", f"R$ {resultados['custo_terc']:,.2f}")
    st.metric("Preco a Construtora", f"R$ {resultados['preco_terc']:,.2f}")
    st.metric("Lucro", f"R$ {resultados['lucro_terc']:,.2f}")

st.markdown("---")
if resultados['lucro_dir'] > resultados['lucro_terc']:
    st.success(f"Recomendacao: Modelo DIRETO e R$ {resultados['lucro_dir'] - resultados['lucro_terc']:,.2f} mais lucrativo")
else:
    st.success(f"Recomendacao: Modelo TERCEIRO com lucro de R$ {resultados['lucro_terc']:,.2f}")

st.caption("Digite a descricao do projeto na primeira aba para extracao automatica dos dados.")
