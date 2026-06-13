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
    texto = texto.lower()
    dados = {}
    
    match = re.search(r'(\d+)\s*m[²2]', texto)
    if match:
        dados['area'] = int(match.group(1))
    
    match = re.search(r'(\d+(?:\.\d+)?)\s*tr', texto)
    if match:
        dados['carga'] = float(match.group(1))
    
    match = re.search(r'(\d+)\s*evap', texto)
    if match:
        dados['evap'] = int(match.group(1))
    
    if 'agua gelada' in texto or 'chiller' in texto:
        dados['sistema'] = 'Agua Gelada'
    elif 'vrf' in texto or 'vrv' in texto:
        dados['sistema'] = 'VRF/VRV'
    
    return dados

def calcular():
    v = st.session_state.valores
    
    custo_equip = v['equip_cond'] + v['equip_evap'] + v['equip_bms']
    custo_insumos = v['ins_cobre'] + v['ins_drenos'] + v['ins_outros']
    custo_mao = v['mao_tec'] + v['mao_aux'] + v['mao_eng']
    custo_serv = v['serv_startup'] + v['serv_testes']
    custo_dir = custo_equip + custo_insumos + custo_mao + custo_serv
    
    preco_cliente = custo_dir * (1 + v['garantia']/100 + v['adm']/100) * (1 + v['margem_dir']/100)
    lucro_dir = preco_cliente - (custo_dir * (1 + v['garantia']/100 + v['adm']/100))
    
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

aba1, aba2 = st.tabs(["Descricao do Projeto", "Ajustes"])

with aba1:
    st.subheader("Cole a descricao do projeto")
    
    exemplo = """Projeto para edificio comercial de 850m2.
Sistema VRF com 28.5 TR de carga.
12 evaporadoras tipo cassete.
Incluir startup."""
    
    descricao = st.text_area("Descricao:", height=150, placeholder=exemplo)
    
    if st.button("Analisar e Aplicar"):
        if descricao:
            dados = extrair_dados(descricao)
            
            if dados:
                st.success("Dados extraidos com sucesso!")
                
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
                
                if 'carga' in dados:
                    carga = dados['carga']
                    qtd_evap = dados.get('evap', 8)
                    
                    st.session_state.valores['equip_cond'] = carga * 3500
                    st.session_state.valores['equip_evap'] = qtd_evap * 4200
                    st.session_state.valores['ins_cobre'] = carga * 15 * 63
                    st.session_state.valores['mao_tec'] = carga * 800
                    st.session_state.valores['serv_startup'] = 3500.0
                    
                    st.rerun()
            else:
                st.warning("Nao foi possivel extrair dados. Use o formato de exemplo.")

with aba2:
    st.subheader("Ajustes Manuais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Equipamentos**")
        st.session_state.valores['equip_cond'] = st.number_input("Condensadoras", value=st.session_state.valores['equip_cond'], step=5000.0)
        st.session_state.valores['equip_evap'] = st.number_input("Evaporadoras", value=st.session_state.valores['equip_evap'], step=5000.0)
        st.session_state.valores['equip_bms'] = st.number_input("BMS", value=st.session_state.valores['equip_bms'], step=1000.0)
        
        st.markdown("**Insumos**")
        st.session_state.valores['ins_cobre'] = st.number_input("Cobre + Isolante", value=st.session_state.valores['ins_cobre'], step=1000.0)
        st.session_state.valores['ins_drenos'] = st.number_input("Drenos", value=st.session_state.valores['ins_drenos'], step=500.0)
        st.session_state.valores['ins_outros'] = st.number_input("Outros", value=st.session_state.valores['ins_outros'], step=500.0)
        
        st.markdown("**Percentuais**")
        st.session_state.valores['garantia'] = st.number_input("Garantia %", value=st.session_state.valores['garantia'], step=0.5)
        st.session_state.valores['adm'] = st.number_input("Adm/Frete %", value=st.session_state.valores['adm'], step=0.5)
        st.session_state.valores['margem_dir'] = st.number_input("Margem Direto %", value=st.session_state.valores['margem_dir'], step=1.0)
    
    with col2:
        st.markdown("**Mao de Obra**")
        st.session_state.valores['mao_tec'] = st.number_input("Tecnicos", value=st.session_state.valores['mao_tec'], step=2000.0)
        st.session_state.valores['mao_aux'] = st.number_input("Auxiliares", value=st.session_state.valores['mao_aux'], step=1000.0)
        st.session_state.valores['mao_eng'] = st.number_input("Engenharia", value=st.session_state.valores['mao_eng'], step=1000.0)
        
        st.markdown("**Servicos**")
        st.session_state.valores['serv_startup'] = st.number_input("Startup", value=st.session_state.valores['serv_startup'], step=500.0)
        st.session_state.valores['serv_testes'] = st.number_input("Testes", value=st.session_state.valores['serv_testes'], step=500.0)
        
        st.markdown("**Modelo Terceiro**")
        st.session_state.valores['fornece_equip'] = st.checkbox("Fornece equipamentos?")
        if st.session_state.valores['fornece_equip']:
            st.session_state.valores['valor_equip_terc'] = st.number_input("Valor equipamentos", value=st.session_state.valores['equip_cond'] + st.session_state.valores['equip_evap'], step=5000.0)
        
        st.session_state.valores['mao_terc'] = st.number_input("Mao de obra terc", value=st.session_state.valores['mao_terc'], step=2000.0)
        st.session_state.valores['consumiveis'] = st.number_input("Consumiveis", value=st.session_state.valores['consumiveis'], step=500.0)
        st.session_state.valores['margem_terc'] = st.number_input("Margem Terceiro %", value=st.session_state.valores['margem_terc'], step=1.0)

# Resultados
resultados = calcular()

st.markdown("---")
st.header("Orcamento")

colR1, colR2 = st.columns(2)

with colR1:
    st.subheader("Modelo Direto")
    st.metric("Custo Total", f"R$ {resultados['custo_dir']:,.2f}")
    st.metric("Preco Cliente", f"R$ {resultados['preco_cliente']:,.2f}")
    st.metric("Lucro", f"R$ {resultados['lucro_dir']:,.2f}")

with colR2:
    st.subheader("Modelo Terceiro")
    st.metric("Custo Total", f"R$ {resultados['custo_terc']:,.2f}")
    st.metric("Preco Construtora", f"R$ {resultados['preco_terc']:,.2f}")
    st.metric("Lucro", f"R$ {resultados['lucro_terc']:,.2f}")

st.markdown("---")
if resultados['lucro_dir'] > resultados['lucro_terc']:
    st.success(f"Modelo DIRETO e R$ {resultados['lucro_dir'] - resultados['lucro_terc']:,.2f} mais lucrativo")
else:
    st.success(f"Modelo TERCEIRO com lucro de R$ {resultados['lucro_terc']:,.2f}")

st.caption("Digite a descricao do projeto na primeira aba.")
