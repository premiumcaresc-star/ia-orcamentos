import streamlit as st
import re
from datetime import datetime

st.set_page_config(page_title="IA Orçamentos", page_icon="🌡️", layout="wide")

st.title("🌡️ IA Orçamentos Climatização")
st.caption(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
st.markdown("---")

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
st.header("Orcamento")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Modelo Direto")
    st.session_state.valores['equip_cond'] = st.number_input("Condensadoras", value=st.session_state.valores['equip_cond'], step=5000.0)
    st.session_state.valores['equip_evap'] = st.number_input("Evaporadoras", value=st.session_state.valores['equip_evap'], step=5000.0)
    st.session_state.valores['ins_cobre'] = st.number_input("Cobre + Isolante", value=st.session_state.valores['ins_cobre'], step=1000.0)
    st.session_state.valores['mao_tec'] = st.number_input("Mao de Obra", value=st.session_state.valores['mao_tec'], step=2000.0)
    st.session_state.valores['garantia'] = st.number_input("Garantia %", value=st.session_state.valores['garantia'], step=0.5)
    st.session_state.valores['margem_dir'] = st.number_input("Margem %", value=st.session_state.valores['margem_dir'], step=1.0)

with col2:
    st.subheader("Modelo Terceiro")
    st.session_state.valores['mao_terc'] = st.number_input("Mao de obra", value=st.session_state.valores['mao_terc'], step=2000.0)
    st.session_state.valores['consumiveis'] = st.number_input("Consumiveis", value=st.session_state.valores['consumiveis'], step=500.0)
    st.session_state.valores['margem_terc'] = st.number_input("Margem %", value=st.session_state.valores['margem_terc'], step=1.0)

resultados = calcular()

st.markdown("---")
st.header("Resultados")

colR1, colR2 = st.columns(2)

with colR1:
    st.metric("Direto - Preco Cliente", f"R$ {resultados['preco_cliente']:,.2f}")
    st.metric("Direto - Lucro", f"R$ {resultados['lucro_dir']:,.2f}")

with colR2:
    st.metric("Terceiro - Preco Construtora", f"R$ {resultados['preco_terc']:,.2f}")
    st.metric("Terceiro - Lucro", f"R$ {resultados['lucro_terc']:,.2f}")

if resultados['lucro_dir'] > resultados['lucro_terc']:
    st.success(f"Direto e R$ {resultados['lucro_dir'] - resultados['lucro_terc']:,.2f} mais lucrativo")
else:
    st.success(f"Terceiro tem lucro de R$ {resultados['lucro_terc']:,.2f}")
