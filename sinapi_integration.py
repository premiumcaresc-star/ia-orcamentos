import json
import os
import streamlit as st
from datetime import datetime

def carregar_precos_sinapi():
    """Carrega os preços da SINAPI para o aplicativo"""
    
    valores_padrao = {
        "cobre_por_metro": 52.00,
        "isolante_por_metro": 22.00,
        "eletroduto_por_metro": 6.50,
        "fio_por_metro": 3.50,
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
                
                precos = {
                    "cobre_por_metro": dados["insumos"].get("cobre_5_8", {}).get("valor", valores_padrao["cobre_por_metro"]),
                    "isolante_por_metro": dados["insumos"].get("isolante_12mm", {}).get("valor", valores_padrao["isolante_por_metro"]),
                    "eletroduto_por_metro": dados["insumos"].get("eletroduto_25", {}).get("valor", valores_padrao["eletroduto_por_metro"]),
                    "fio_por_metro": dados["insumos"].get("fio_2_5mm", {}).get("valor", valores_padrao["fio_por_metro"]),
                    "gas_r410a_kg": dados["insumos"].get("gas_r410a", {}).get("valor", valores_padrao["gas_r410a_kg"]),
                    "solda_prata_kg": dados["insumos"].get("solda_prata", {}).get("valor", valores_padrao["solda_prata_kg"]),
                    "mao_obra_tecnico_mes": dados["mao_de_obra"].get("tecnico_mes", {}).get("valor", valores_padrao["mao_obra_tecnico_mes"]),
                    "mao_obra_ajudante_mes": dados["mao_de_obra"].get("ajudante_mes", {}).get("valor", valores_padrao["mao_obra_ajudante_mes"]),
                    "engenheiro_hora": dados["mao_de_obra"].get("engenheiro_hora", {}).get("valor", valores_padrao["engenheiro_hora"]),
                    "data_referencia": dados["referencias"].get("competencia", valores_padrao["data_referencia"]),
                    "uf": dados["referencias"].get("uf", "SP"),
                    "fonte": dados["referencias"].get("fonte", "SINAPI")
                }
                
                return precos
    except Exception as e:
        print(f"Erro ao carregar preços SINAPI: {e}")
    
    return valores_padrao

def exibir_info_sinapi():
    """Exibe informações sobre a origem dos preços no rodapé"""
    precos = carregar_precos_sinapi()
    
    st.markdown("---")
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.caption(f"📊 **Fonte:** {precos.get('fonte', 'SINAPI')}")
    with col_info2:
        st.caption(f"📍 **UF:** {precos.get('uf', 'SP')}")
    with col_info3:
        st.caption(f"📅 **Referência:** {precos.get('data_referencia', 'Atual')}")

@st.cache_data(ttl=3600)
def get_precos_sinapi():
    return carregar_precos_sinapi()
