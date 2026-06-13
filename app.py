import streamlit as st
from datetime import datetime

st.set_page_config(page_title="IA Orçamentos Climatização", page_icon="🌡️", layout="wide")

st.title("🌡️ IA Orçamentos Climatização")
st.caption(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
st.markdown("---")

# ========== FUNÇÃO PARA CALCULAR PREÇOS DINAMICAMENTE ==========
def calcular_precos(equip_cond, equip_evap, equip_bms, ins_cobre, ins_drenos, ins_outros,
                    mao_tec, mao_aux, mao_eng, serv_startup, serv_testes,
                    garantia_pct, adm_pct, margem_pct,
                    fornece_equip, fornece_insumos, valor_equip_terc, valor_insumos_terc,
                    mao_terc, consumiveis, startup_terc, margem_terc_pct):
    
    # Cálculos Modelo Direto
    custo_equip = equip_cond + equip_evap + equip_bms
    custo_insumos = ins_cobre + ins_drenos + ins_outros
    custo_mao = mao_tec + mao_aux + mao_eng
    custo_serv = serv_startup + serv_testes
    custo_total_dir = custo_equip + custo_insumos + custo_mao + custo_serv
    
    preco_cliente = custo_total_dir * (1 + garantia_pct/100 + adm_pct/100) * (1 + margem_pct/100)
    lucro_dir = preco_cliente - (custo_total_dir * (1 + garantia_pct/100 + adm_pct/100))
    
    # Cálculos Modelo Terceiro
    custo_terc_base = mao_terc + consumiveis + startup_terc + valor_equip_terc + valor_insumos_terc
    preco_construtora = custo_terc_base * (1 + margem_terc_pct/100)
    lucro_terc = preco_construtora - custo_terc_base
    
    return {
        'custo_total_dir': custo_total_dir,
        'preco_cliente': preco_cliente,
        'lucro_dir': lucro_dir,
        'custo_total_terc': custo_terc_base,
        'preco_construtora': preco_construtora,
        'lucro_terc': lucro_terc,
        'custo_equip': custo_equip,
        'custo_insumos': custo_insumos,
        'custo_mao': custo_mao,
        'custo_serv': custo_serv
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

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("📋 Dados do Projeto")
    cliente = st.text_input("Cliente", "Edifício Comercial Paulista")
    tipo_sistema = st.selectbox("Sistema", ["VRF/VRV", "Água Gelada", "Split"])
    area = st.number_input("Área (m²)", min_value=0.0, value=850.0, step=50.0)
    carga_tr = st.number_input("Carga (TR)", min_value=0.0, value=28.5, step=1.0)
    
    st.markdown("---")
    
    # Botão para valores sugeridos por sistema
    if st.button("🔧 Valores sugeridos para este sistema"):
        if tipo_sistema == "VRF/VRV":
            st.session_state.valores['equip_cond'] = 89000.0
            st.session_state.valores['equip_evap'] = 45000.0
            st.session_state.valores['mao_tec'] = 28000.0
        elif tipo_sistema == "Água Gelada":
            st.session_state.valores['equip_cond'] = 85000.0
            st.session_state.valores['equip_evap'] = 35000.0
            st.session_state.valores['mao_tec'] = 32000.0
        else:  # Split
            st.session_state.valores['equip_cond'] = 40000.0
            st.session_state.valores['equip_evap'] = 15000.0
            st.session_state.valores['mao_tec'] = 15000.0
        st.rerun()

# ========== COLUNAS PRINCIPAIS ==========
col1, col2 = st.columns(2)

# ========== COLUNA 1 - MODELO DIRETO ==========
with col1:
    st.header("🎯 MODELO DIRETO")
    st.caption("Você → Cliente Final")
    
    with st.expander("📦 Equipamentos", expanded=True):
        equip_cond = st.number_input("Condensadoras/Chiller (R$)", 
                                      value=st.session_state.valores['equip_cond'], 
                                      step=5000.0, key="eq_cond",
                                      on_change=lambda: st.session_state.valores.update({'equip_cond': equip_cond}))
        equip_evap = st.number_input("Evaporadoras/Fan Coils (R$)", 
                                      value=st.session_state.valores['equip_evap'], 
                                      step=5000.0, key="eq_evap")
        equip_bms = st.number_input("BMS / Controles (R$)", 
                                     value=st.session_state.valores['equip_bms'], 
                                     step=1000.0, key="eq_bms")
        
        # Atualizar session state
        st.session_state.valores['equip_cond'] = equip_cond
        st.session_state.valores['equip_evap'] = equip_evap
        st.session_state.valores['equip_bms'] = equip_bms
    
    with st.expander("🔩 Insumos", expanded=True):
        ins_cobre = st.number_input("Cobre + Isolante (R$)", 
                                     value=st.session_state.valores['ins_cobre'], 
                                     step=1000.0, key="ins_cobre")
        ins_drenos = st.number_input("Drenos + Eletrodutos (R$)", 
                                      value=st.session_state.valores['ins_drenos'], 
                                      step=500.0, key="ins_drenos")
        ins_outros = st.number_input("Outros insumos (R$)", 
                                      value=st.session_state.valores['ins_outros'], 
                                      step=500.0, key="ins_outros")
        
        st.session_state.valores['ins_cobre'] = ins_cobre
        st.session_state.valores['ins_drenos'] = ins_drenos
        st.session_state.valores['ins_outros'] = ins_outros
    
    with st.expander("👷 Mão de Obra", expanded=True):
        mao_tec = st.number_input("Técnicos (R$)", 
                                   value=st.session_state.valores['mao_tec'], 
                                   step=2000.0, key="mao_tec")
        mao_aux = st.number_input("Auxiliares (R$)", 
                                   value=st.session_state.valores['mao_aux'], 
                                   step=1000.0, key="mao_aux")
        mao_eng = st.number_input("Engenharia/Projeto (R$)", 
                                   value=st.session_state.valores['mao_eng'], 
                                   step=1000.0, key="mao_eng")
        
        st.session_state.valores['mao_tec'] = mao_tec
        st.session_state.valores['mao_aux'] = mao_aux
        st.session_state.valores['mao_eng'] = mao_eng
    
    with st.expander("⚙️ Serviços", expanded=True):
        serv_startup = st.number_input("Startup/Comissionamento (R$)", 
                                        value=st.session_state.valores['serv_startup'], 
                                        step=500.0, key="serv_start")
        serv_testes = st.number_input("Testes + Carga de gás (R$)", 
                                       value=st.session_state.valores['serv_testes'], 
                                       step=500.0, key="serv_test")
        
        st.session_state.valores['serv_startup'] = serv_startup
        st.session_state.valores['serv_testes'] = serv_testes
    
    st.markdown("---")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        garantia = st.number_input("Garantia (%)", value=st.session_state.valores['garantia'], step=0.5, key="gar")
    with col_p2:
        adm = st.number_input("Adm/Frete (%)", value=st.session_state.valores['adm'], step=0.5, key="adm")
    with col_p3:
        margem_dir = st.number_input("Margem + BDI (%)", value=st.session_state.valores['margem_dir'], step=1.0, key="marg_dir")
    
    st.session_state.valores['garantia'] = garantia
    st.session_state.valores['adm'] = adm
    st.session_state.valores['margem_dir'] = margem_dir

# ========== COLUNA 2 - MODELO TERCEIRO ==========
with col2:
    st.header("🎯 MODELO TERCEIRO")
    st.caption("Construtora → Você")
    
    st.subheader("📋 Quem fornece?")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fornece_equip = st.checkbox("Você fornece equipamentos?", 
                                     value=st.session_state.valores['fornece_equip'], 
                                     key="for_eq")
        st.session_state.valores['fornece_equip'] = fornece_equip
        
        if fornece_equip:
            valor_equip_terc = st.number_input("Valor equipamentos (R$)", 
                                                value=st.session_state.valores['valor_equip_terc'] if st.session_state.valores['valor_equip_terc'] > 0 else equip_cond + equip_evap + equip_bms,
                                                step=5000.0, key="val_eq")
            st.session_state.valores['valor_equip_terc'] = valor_equip_terc
        else:
            valor_equip_terc = 0.0
            st.caption("✓ Cliente/Construtora fornece")
    
    with col_f2:
        fornece_insumos = st.checkbox("Você fornece insumos?", 
                                       value=st.session_state.valores['fornece_insumos'], 
                                       key="for_ins")
        st.session_state.valores['fornece_insumos'] = fornece_insumos
        
        if fornece_insumos:
            valor_insumos_terc = st.number_input("Valor insumos (R$)", 
                                                  value=st.session_state.valores['valor_insumos_terc'] if st.session_state.valores['valor_insumos_terc'] > 0 else ins_cobre,
                                                  step=2000.0, key="val_ins")
            st.session_state.valores['valor_insumos_terc'] = valor_insumos_terc
        else:
            valor_insumos_terc = 0.0
            st.caption("✓ Cliente/Construtora fornece")
    
    st.markdown("---")
    
    mao_terc = st.number_input("Mão de obra (R$)", 
                                value=st.session_state.valores['mao_terc'], 
                                step=2000.0, key="mao_terc")
    consumiveis = st.number_input("Consumíveis (R$)", 
                                   value=st.session_state.valores['consumiveis'], 
                                   step=500.0, key="cons")
    startup_terc = st.number_input("Startup (R$)", 
                                    value=st.session_state.valores['startup_terc'], 
                                    step=500.0, key="start_terc")
    margem_terc = st.number_input("Margem Terceiro (%)", 
                                   value=st.session_state.valores['margem_terc'], 
                                   step=1.0, key="marg_terc")
    
    st.session_state.valores['mao_terc'] = mao_terc
    st.session_state.valores['consumiveis'] = consumiveis
    st.session_state.valores['startup_terc'] = startup_terc
    st.session_state.valores['margem_terc'] = margem_terc

# ========== CALCULAR E EXIBIR RESULTADOS ==========
resultados = calcular_precos(
    equip_cond, equip_evap, equip_bms,
    ins_cobre, ins_drenos, ins_outros,
    mao_tec, mao_aux, mao_eng,
    serv_startup, serv_testes,
    garantia, adm, margem_dir,
    fornece_equip, fornece_insumos, valor_equip_terc, valor_insumos_terc,
    mao_terc, consumiveis, startup_terc, margem_terc
)

st.markdown("---")

# ========== EXIBIR RESULTADOS ==========
col_r1, col_r2 = st.columns(2)

with col_r1:
    st.subheader("📊 RESULTADO DIRETO")
    st.metric("💰 Seu Custo Total", f"R$ {resultados['custo_total_dir']:,.2f}")
    st.metric("🏷️ Preço para Cliente", f"R$ {resultados['preco_cliente']:,.2f}")
    st.metric("📈 Seu Lucro Direto", f"R$ {resultados['lucro_dir']:,.2f}", 
              delta=f"Margem: {(resultados['lucro_dir']/resultados['custo_total_dir']*100):.1f}%")

with col_r2:
    st.subheader("📊 RESULTADO TERCEIRO")
    st.metric("💰 Seu Custo Total", f"R$ {resultados['custo_total_terc']:,.2f}")
    st.metric("🏷️ Preço para Construtora", f"R$ {resultados['preco_construtora']:,.2f}")
    st.metric("📈 Seu Lucro Terceiro", f"R$ {resultados['lucro_terc']:,.2f}",
              delta=f"Margem: {(resultados['lucro_terc']/resultados['custo_total_terc']*100):.1f}%")

# ========== COMPARAÇÃO ==========
st.markdown("---")
col_c1, col_c2 = st.columns(2)

with col_c1:
    st.subheader("💡 Comparação")
    diferenca = resultados['lucro_dir'] - resultados['lucro_terc']
    if diferenca > 0:
        st.success(f"✅ Modelo DIRETO é R$ {diferenca:,.2f} mais lucrativo")
    else:
        st.info(f"ℹ️ Modelo TERCEIRO tem R$ {abs(diferenca):,.2f} de lucro com menos risco")

with col_c2:
    st.subheader("⚡ Resumo")
    st.write(f"**Custo Direto:** R$ {resultados['custo_total_dir']:,.2f}")
    st.write(f"**Custo Terceiro:** R$ {resultados['custo_total_terc']:,.2f}")
    st.write(f"**Diferença:** R$ {resultados['custo_total_dir'] - resultados['custo_total_terc']:,.2f}")

st.markdown("---")
st.caption("💡 **Qualquer alteração nos valores acima atualiza automaticamente os preços e lucros em tempo real!**")
