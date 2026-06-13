import json
import os
import streamlit as st
from datetime import datetime

def listar_ufs_disponiveis():
    """Retorna lista de UFs com dados disponíveis"""
    ufs_padrao = ["SP", "RJ", "MG", "RS", "BA", "PR", "SC", "GO", "PE", "CE", "DF", "BR"]
    
    try:
        if os.path.exists("data/precos_sinapi.json"):
            with open("data/precos_sinapi.json", "r", encoding="utf-8") as f:
                dados = json.load(f)
                ufs = [k for k in dados.keys() if k not in ["ultima_atualizacao", "uf_selecionada"]]
                if ufs:
                    return sorted(ufs)
    except:
        pass
    
    return ufs_padrao

def carregar_precos_sinapi(uf_selecionada="SP"):
    """Carrega os preços da SINAPI para a UF selecionada"""
    
    valores_padrao = {
        "cobre_por_metro": 52.00,
        "isolante_por_metro": 22.00,
        "eletroduto_por_metro": 6.50,
        "fio_por_metro": 3.50,
        "dreno_por_metro": 8.50,
        "gas_r410a_kg": 85.00,
        "solda_prata_kg": 450.00,
        "mao_obra_tecnico_mes": 2800.00,
        "mao_obra_ajudante_mes": 1800.00,
        "engenheiro_hora": 85.00,
        "data_referencia": datetime.now().strftime("%B/%Y")
    }
    
    try:
        if os.path.exists("data/precos_sinapi.json"):
            with open("data/precos_sinapi.json", "r", encoding="utf-8") as f:
                dados = json.load(f)
                
                if uf_selecionada in dados:
                    dados_uf = dados[uf_selecionada]
                    
                    precos = {
                        "cobre_por_metro": dados_uf["insumos"].get("cobre_5_8", {}).get("valor", valores_padrao["cobre_por_metro"]),
                        "isolante_por_metro": dados_uf["insumos"].get("isolante_12mm", {}).get("valor", valores_padrao["isolante_por_metro"]),
                        "eletroduto_por_metro": dados_uf["insumos"].get("eletroduto_25", {}).get("valor", valores_padrao["eletroduto_por_metro"]),
                        "fio_por_metro": dados_uf["insumos"].get("fio_2_5mm", {}).get("valor", valores_padrao["fio_por_metro"]),
                        "dreno_por_metro": dados_uf["insumos"].get("dreno_25mm", {}).get("valor", valores_padrao["dreno_por_metro"]),
                        "gas_r410a_kg": dados_uf["insumos"].get("gas_r410a", {}).get("valor", valores_padrao["gas_r410a_kg"]),
                        "solda_prata_kg": dados_uf["insumos"].get("solda_prata", {}).get("valor", valores_padrao["solda_prata_kg"]),
                        "mao_obra_tecnico_mes": dados_uf["mao_de_obra"].get("tecnico_mes", {}).get("valor", valores_padrao["mao_obra_tecnico_mes"]),
                        "mao_obra_ajudante_mes": dados_uf["mao_de_obra"].get("ajudante_mes", {}).get("valor", valores_padrao["mao_obra_ajudante_mes"]),
                        "engenheiro_hora": dados_uf["mao_de_obra"].get("engenheiro_hora", {}).get("valor", valores_padrao["engenheiro_hora"]),
                        "data_referencia": dados_uf["referencias"].get("competencia", valores_padrao["data_referencia"]),
                        "uf": dados_uf.get("uf", uf_selecionada),
                        "fonte": dados_uf["referencias"].get("fonte", "SINAPI")
                    }
                    
                    return precos
    except Exception as e:
        print(f"Erro ao carregar preços SINAPI: {e}")
    
    return valores_padrao

def criar_seletor_sinapi():
    """Cria um seletor de UF na sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Tabela SINAPI")
    
    ufs = listar_ufs_disponiveis()
    
    uf_padrao = st.session_state.get("uf_sinapi", "SP")
    uf_selecionada = st.sidebar.selectbox(
        "Selecione o Estado:",
        options=ufs,
        index=ufs.index(uf_padrao) if uf_padrao in ufs else 0,
        help="Selecione a UF para os preços de referência da SINAPI"
    )
    
    if uf_selecionada != st.session_state.get("uf_sinapi", "SP"):
        st.session_state.uf_sinapi = uf_selecionada
        st.session_state.precos_sinapi = carregar_precos_sinapi(uf_selecionada)
        st.rerun()
    
    # Botão para atualizar
    if st.sidebar.button("🔄 Atualizar Dados SINAPI", use_container_width=True):
        with st.spinner("Atualizando preços..."):
            # Aqui você pode chamar uma função para forçar atualização
            pass
    
    # Exibir data de referência
    if "precos_sinapi" in st.session_state:
        st.sidebar.caption(f"Referência: {st.session_state.precos_sinapi.get('data_referencia', 'N/A')}")
    
    st.sidebar.caption("💡 Preços baseados na tabela SINAPI/Caixa")

def exibir_info_sinapi():
    """Exibe informações sobre a origem dos preços no rodapé"""
    precos = st.session_state.get("precos_sinapi", {})
    
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.caption(f"📊 **Fonte:** {precos.get('fonte', 'SINAPI')}")
    with col_info2:
        st.caption(f"📍 **UF:** {precos.get('uf', 'SP')}")
    with col_info3:
        st.caption(f"📅 **Referência:** {precos.get('data_referencia', 'Atual')}")

def get_precos_sinapi():
    """Retorna os preços SINAPI atuais"""
    if "precos_sinapi" not in st.session_state:
        uf = st.session_state.get("uf_sinapi", "SP")
        st.session_state.precos_sinapi = carregar_precos_sinapi(uf)
    return st.session_state.precos_sinapi
