import streamlit as st
from datetime import datetime
from sinapi_integration import get_precos_sinapi, exibir_info_sinapi, criar_seletor_sinapi
from quantificador import criar_interface_quantificacao

st.set_page_config(page_title="IA Orçamentos Climatização", page_icon="🌡️", layout="wide")

st.title("🌡️ IA Orçamentos Climatização")
st.caption(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
st.markdown("---")

# Criar seletor SINAPI na sidebar
criar_seletor_sinapi()

# Carregar preços
precos_sinapi = get_precos_sinapi()

# Interface do projeto
st.header("📋 Dados do Projeto")

col1, col2, col3 = st.columns(3)
with col1:
    tipo_projeto = st.selectbox("Tipo de Projeto", ["Novo", "Retrofit", "Ampliação"])
with col2:
    sistema = st.selectbox("Sistema", ["VRF/VRV", "Água Gelada", "Split"])
with col3:
    uf_projeto = st.selectbox("Localização", ["SP", "RJ", "MG", "RS", "BA", "PR", "SC", "GO", "PE", "CE", "DF"])

# Quantificação de equipamentos
custo_equipamentos, quantidades = criar_interface_quantificacao(sistema, uf_projeto)

# Orçamento base
st.header("💰 Orçamento")

st.metric("Custo Total Equipamentos", f"R$ {custo_equipamentos:,.2f}")

# Exibir informações SINAPI
exibir_info_sinapi()
