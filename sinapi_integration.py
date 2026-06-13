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
    # Inicializar session state
    if 'uf_sinapi' not in st.session_state:
        st.session_state.uf_sinapi = "SP"
    
    if 'precos_sinapi' not in st.session_state:
        st.session_state.precos_sinapi = carregar_precos_sinapi(st.session_state.uf_sinapi)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Tabela SINAPI")
    
    ufs = listar_ufs_disponiveis()
    
    uf_selecionada = st.sidebar.selectbox(
        "Selecione o Estado:",
        options=ufs,
        index=ufs.index(st.session_state.uf_sinapi) if st.session_state.uf_sinapi in ufs else 0,
        help="Selecione a UF para os preços de referência da SINAPI"
    )
    
    if uf_selecionada != st.session_state.uf_sinapi:
        st.session_state.uf_sinapi = uf_selecionada
        st.session_state.precos_sinapi = carregar_precos_sinapi(uf_selecionada)
        st.rerun()
    
    # Exibir data de referência
    st.sidebar.caption(f"Referência: {st.session_state.precos_sinapi.get('data_referencia', 'N/A')}")
    st.sidebar.caption("💡 Preços baseados na tabela SINAPI/Caixa")

def exibir_info_sinapi():
    """Exibe informações sobre a origem dos preços no rodapé"""
    if 'precos_sinapi' in st.session_state:
        precos = st.session_state.precos_sinapi
    else:
        precos = carregar_precos_sinapi("SP")
    
    st.markdown("---")
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.caption(f"📊 **Fonte:** {precos.get('fonte', 'SINAPI')}")
    with col_info2:
        st.caption(f"📍 **UF:** {precos.get('uf', 'SP')}")
    with col_info3:
        st.caption(f"📅 **Referência:** {precos.get('data_referencia', 'Atual')}")

def get_precos_sinapi():
    """Retorna os preços SINAPI atuais"""
    if 'precos_sinapi' not in st.session_state:
        uf = st.session_state.get('uf_sinapi', 'SP')
        st.session_state.precos_sinapi = carregar_precos_sinapi(uf)
    return st.session_state.precos_sinapi

def get_precos_equipamentos(uf="SP"):
    """Retorna preços médios de equipamentos por UF"""
    
    # Mapeamento de preços por UF
    precos_equipamentos = {
        "VRF/VRV": {
            "condensadora_por_tr": {"SP": 3500, "RJ": 3800, "MG": 3400, "RS": 3600, "default": 3500},
            "evaporadora_cassete": {"SP": 4200, "RJ": 4500, "MG": 4100, "RS": 4300, "default": 4200},
            "evaporadora_duto": {"SP": 3800, "RJ": 4100, "MG": 3700, "RS": 3900, "default": 3800},
            "evaporadora_piso_teto": {"SP": 4500, "RJ": 4800, "MG": 4400, "RS": 4600, "default": 4500},
        },
        "Água Gelada": {
            "chiller_por_tr": {"SP": 2800, "RJ": 3100, "MG": 2700, "RS": 2900, "default": 2800},
            "fan_coil_cassete": {"SP": 2500, "RJ": 2700, "MG": 2400, "RS": 2600, "default": 2500},
            "fan_coil_duto": {"SP": 2200, "RJ": 2400, "MG": 2100, "RS": 2300, "default": 2200},
            "fan_coil_high_wall": {"SP": 2000, "RJ": 2200, "MG": 1900, "RS": 2100, "default": 2000},
            "torre_resfriamento_por_tr": {"SP": 800, "RJ": 880, "MG": 780, "RS": 820, "default": 800},
        },
        "Split": {
            "split_9000_btu": {"SP": 1800, "RJ": 2000, "MG": 1750, "RS": 1850, "default": 1800},
            "split_12000_btu": {"SP": 2200, "RJ": 2400, "MG": 2100, "RS": 2250, "default": 2200},
            "split_18000_btu": {"SP": 2800, "RJ": 3100, "MG": 2700, "RS": 2900, "default": 2800},
            "split_24000_btu": {"SP": 3500, "RJ": 3800, "MG": 3400, "RS": 3600, "default": 3500},
            "multisplit_evaporadora": {"SP": 1500, "RJ": 1650, "MG": 1450, "RS": 1550, "default": 1500},
        }
    }
    
    resultado = {}
    for sistema, equipamentos in precos_equipamentos.items():
        resultado[sistema] = {}
        for equipamento, precos_por_uf in equipamentos.items():
            valor = precos_por_uf.get(uf, precos_por_uf["default"])
            resultado[sistema][equipamento] = valor
    
    return resultado
