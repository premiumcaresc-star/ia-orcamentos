import streamlit as st
from datetime import datetime

st.set_page_config(page_title="IA Orçamentos Climatização", page_icon="🌡️", layout="wide")

st.title("🌡️ IA Orçamentos Climatização - Direto x Terceiro")
st.caption(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
st.markdown("---")

with st.sidebar:
    st.header("📋 Dados do Projeto")
    cliente = st.text_input("Cliente", "Edifício Comercial")
    tipo_sistema = st.selectbox("Sistema", ["VRF/VRV", "Água Gelada"])
    area = st.number_input("Área (m²)", value=500)

col1, col2 = st.columns(2)

with col1:
    st.header("🎯 Modelo Direto")
    st.caption("Você → Cliente")
    
    equip = st.number_input("Equipamentos (R$)", value=89000, step=5000)
    insumos = st.number_input("Insumos (R$)", value=19200, step=1000)
    mao = st.number_input("Mão de obra (R$)", value=28000, step=2000)
    servicos = st.number_input("Serviços (R$)", value=7000, step=500)
    margem = st.slider("Margem (%)", 20, 60, 40)
    
    total_dir = equip + insumos + mao + servicos
    preco_dir = total_dir * (1 + margem/100)
    
    st.metric("Preço para Cliente", f"R$ {preco_dir:,.2f}")
    st.caption(f"Custo total: R$ {total_dir:,.2f}")

with col2:
    st.header("🎯 Modelo Terceiro")
    st.caption("Construtora → Você")
    
    fornece_equip = st.checkbox("Você fornece equipamentos?")
    if fornece_equip:
        valor_equip = st.number_input("Equipamentos (R$)", value=89000)
    else:
        valor_equip = 0
        st.info("✓ Cliente fornece equipamentos")
    
    mao_terc = st.number_input("Mão de obra (R$)", value=28000, step=2000)
    consumiveis = st.number_input("Consumíveis (R$)", value=2800, step=500)
    margem_terc = st.slider("Margem terceiro (%)", 10, 40, 25)
    
    total_terc = mao_terc + consumiveis + valor_equip
    preco_terc = total_terc * (1 + margem_terc/100)
    
    st.metric("Preço para Construtora", f"R$ {preco_terc:,.2f}")
    st.caption(f"Custo total: R$ {total_terc:,.2f}")

st.markdown("---")
col_comp1, col_comp2 = st.columns(2)
with col_comp1:
    lucro_dir = preco_dir - total_dir
    lucro_terc = preco_terc - total_terc
    st.metric("Lucro Direto", f"R$ {lucro_dir:,.2f}")
    st.metric("Lucro Terceiro", f"R$ {lucro_terc:,.2f}")
with col_comp2:
    if lucro_dir > lucro_terc:
        st.success(f"⭐ Direto é mais lucrativo: R$ {lucro_dir - lucro_terc:,.2f} a mais")
    else:
        st.info(f"⭐ Terceiro com menos risco e lucro de R$ {lucro_terc:,.2f}")

st.caption("💡 Ajuste os valores acima para calcular os dois modelos de negócio")
