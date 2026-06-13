import streamlit as st
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="IA Orçamentos Climatização", page_icon="🌡️", layout="wide")

# Título
st.title("🌡️ IA Orçamentos Climatização")
st.caption(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📋 Dados do Projeto")
    cliente = st.text_input("Cliente", "Edifício Comercial Paulista")
    tipo_sistema = st.selectbox("Sistema", ["VRF/VRV", "Água Gelada", "Split"])
    area = st.number_input("Área (m²)", min_value=0, value=850, step=50)
    carga_tr = st.number_input("Carga (TR)", min_value=0.0, value=28.5, step=1.0)
    st.markdown("---")
    st.caption("💡 Todos os valores são editáveis")

# Colunas principais
col1, col2 = st.columns(2)

# ========== COLUNA 1 - MODELO DIRETO ==========
with col1:
    st.header("🎯 MODELO 1 - EXECUÇÃO DIRETA")
    st.caption("Você → Cliente Final")
    
    with st.expander("📦 Equipamentos", expanded=True):
        equip_cond = st.number_input("Condensadoras/Chiller (R$)", value=89000.0, step=5000.0, key="eq_cond")
        equip_evap = st.number_input("Evaporadoras/Fan Coils (R$)", value=45000.0, step=5000.0, key="eq_evap")
        equip_bms = st.number_input("BMS / Controles (R$)", value=8500.0, step=1000.0, key="eq_bms")
    
    with st.expander("🔩 Insumos", expanded=True):
        ins_cobre = st.number_input("Cobre + Isolante (R$)", value=19200.0, step=1000.0, key="ins_cobre")
        ins_drenos = st.number_input("Drenos + Eletrodutos (R$)", value=3500.0, step=500.0, key="ins_drenos")
        ins_outros = st.number_input("Outros insumos (R$)", value=2500.0, step=500.0, key="ins_outros")
    
    with st.expander("👷 Mão de Obra", expanded=True):
        mao_tec = st.number_input("Técnicos (R$)", value=28000.0, step=2000.0, key="mao_tec")
        mao_aux = st.number_input("Auxiliares (R$)", value=8000.0, step=1000.0, key="mao_aux")
        mao_eng = st.number_input("Engenharia/Projeto (R$)", value=5000.0, step=1000.0, key="mao_eng")
    
    with st.expander("⚙️ Serviços Especializados", expanded=True):
        serv_startup = st.number_input("Startup/Comissionamento (R$)", value=4500.0, step=500.0, key="serv_start")
        serv_testes = st.number_input("Testes + Carga de gás (R$)", value=2500.0, step=500.0, key="serv_test")
    
    # Cálculos
    custo_equip = equip_cond + equip_evap + equip_bms
    custo_insumos = ins_cobre + ins_drenos + ins_outros
    custo_mao = mao_tec + mao_aux + mao_eng
    custo_serv = serv_startup + serv_testes
    custo_total_direto = custo_equip + custo_insumos + custo_mao + custo_serv
    
    st.markdown("---")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        garantia = st.number_input("Garantia (%)", value=2.0, step=0.5, key="gar")
    with col_p2:
        adm = st.number_input("Adm/Frete (%)", value=2.5, step=0.5, key="adm")
    with col_p3:
        margem = st.number_input("Margem + BDI (%)", value=40.0, step=1.0, key="marg")
    
    preco_cliente = custo_total_direto * (1 + garantia/100 + adm/100) * (1 + margem/100)
    
    st.markdown("---")
    st.metric("💰 SEU CUSTO TOTAL", f"R$ {custo_total_direto:,.2f}")
    st.metric("🏷️ PREÇO PARA CLIENTE", f"R$ {preco_cliente:,.2f}")

# ========== COLUNA 2 - MODELO TERCEIRO ==========
with col2:
    st.header("🎯 MODELO 2 - EXECUÇÃO COMO TERCEIRO")
    st.caption("Construtora → Você")
    
    st.subheader("📋 Quem fornece o quê?")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fornece_equip = st.checkbox("Você fornece equipamentos?", key="for_eq")
        if fornece_equip:
            valor_equip = st.number_input("Valor equipamentos (R$)", value=custo_equip, step=5000.0, key="val_eq")
        else:
            valor_equip = 0.0
            st.caption("✓ Cliente/Construtora fornece")
    with col_f2:
        fornece_insumos = st.checkbox("Você fornece cobre/isolante?", key="for_ins")
        if fornece_insumos:
            valor_insumos = st.number_input("Valor insumos (R$)", value=ins_cobre, step=2000.0, key="val_ins")
        else:
            valor_insumos = 0.0
            st.caption("✓ Cliente/Construtora fornece")
    
    st.markdown("---")
    
    mao_terc = st.number_input("Mão de obra (R$)", value=custo_mao, step=2000.0, key="mao_terc")
    consumiveis = st.number_input("Consumíveis (gás, solda, abraçadeiras - R$)", value=2800.0, step=500.0, key="cons")
    startup_terc = st.number_input("Startup/Comissionamento (R$)", value=serv_startup, step=500.0, key="start_terc")
    
    custo_terceiro_base = mao_terc + consumiveis + startup_terc + valor_equip + valor_insumos
    margem_terc = st.number_input("Margem para terceiro (%)", value=25.0, step=1.0, key="marg_terc")
    preco_construtora = custo_terceiro_base * (1 + margem_terc/100)
    
    st.markdown("---")
    st.metric("💰 SEU CUSTO TOTAL", f"R$ {custo_terceiro_base:,.2f}")
    st.metric("🏷️ PREÇO PARA CONSTRUTORA", f"R$ {preco_construtora:,.2f}")

# ========== RODAPÉ ==========
st.markdown("---")

col_comp1, col_comp2 = st.columns(2)

with col_comp1:
    st.subheader("📊 Comparação de Lucro")
    lucro_direto = preco_cliente - (custo_total_direto * (1 + garantia/100 + adm/100))
    lucro_terceiro = preco_construtora - custo_terceiro_base
    
    st.metric("Lucro Modelo Direto", f"R$ {lucro_direto:,.2f}")
    st.metric("Lucro Modelo Terceiro", f"R$ {lucro_terceiro:,.2f}")

with col_comp2:
    st.subheader("💡 Recomendação")
    if lucro_direto > lucro_terceiro:
        st.success(f"⭐ Modelo DIRETO é R$ {lucro_direto - lucro_terceiro:,.2f} mais lucrativo")
    else:
        st.success(f"⭐ Modelo TERCEIRO tem lucro de R$ {lucro_terceiro:,.2f} com menos risco")

st.caption("💡 Dica: Todos os valores são editáveis. O aplicativo calcula automaticamente os preços finais em tempo real.")
