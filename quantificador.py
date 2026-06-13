import streamlit as st
import pandas as pd

def criar_tabela_quantificacao(sistema):
    """Cria interface para quantificação de equipamentos"""
    
    st.subheader("📊 Quantificação de Equipamentos")
    
    if sistema == "VRF/VRV":
        equipamentos = {
            "Condensadoras VRF/VRV (TR)": {
                "unidade": "TR",
                "valor_padrao": 28.5,
                "preco_referencia": 3500,
                "descricao": "Total de TR do sistema"
            },
            "Evaporadoras Cassete": {
                "unidade": "unidades",
                "valor_padrao": 8,
                "preco_referencia": 4200,
                "descricao": "Unidades tipo cassete"
            },
            "Evaporadoras Duto": {
                "unidade": "unidades",
                "valor_padrao": 4,
                "preco_referencia": 3800,
                "descricao": "Unidades tipo duto"
            },
            "Evaporadoras Piso/Teto": {
                "unidade": "unidades",
                "valor_padrao": 2,
                "preco_referencia": 4500,
                "descricao": "Unidades tipo piso/teto"
            },
            "Controladores Individuais": {
                "unidade": "unidades",
                "valor_padrao": 14,
                "preco_referencia": 500,
                "descricao": "Controles para cada evaporadora"
            },
            "BMS Central": {
                "unidade": "sistema",
                "valor_padrao": 1,
                "preco_referencia": 8500,
                "descricao": "Sistema de automação predial"
            }
        }
    
    elif sistema == "Água Gelada":
        equipamentos = {
            "Chiller (TR)": {
                "unidade": "TR",
                "valor_padrao": 30,
                "preco_referencia": 2800,
                "descricao": "Capacidade total do chiller"
            },
            "Fan Coils Cassete": {
                "unidade": "unidades",
                "valor_padrao": 10,
                "preco_referencia": 2500,
                "descricao": "Fan coils tipo cassete"
            },
            "Fan Coils Duto": {
                "unidade": "unidades",
                "valor_padrao": 5,
                "preco_referencia": 2200,
                "descricao": "Fan coils tipo duto"
            },
            "Fan Coils High Wall": {
                "unidade": "unidades",
                "valor_padrao": 5,
                "preco_referencia": 2000,
                "descricao": "Fan coils tipo parede"
            },
            "Torre de Resfriamento (TR)": {
                "unidade": "TR",
                "valor_padrao": 30,
                "preco_referencia": 800,
                "descricao": "Torre para rejeição de calor"
            },
            "Bombas d'Áua": {
                "unidade": "conjunto",
                "valor_padrao": 2,
                "preco_referencia": 5000,
                "descricao": "Bombas primárias/secundárias"
            }
        }
    
    else:  # Split
        equipamentos = {
            "Split 9000 BTU": {
                "unidade": "unidades",
                "valor_padrao": 4,
                "preco_referencia": 1800,
                "descricao": "9.000 BTU/h"
            },
            "Split 12000 BTU": {
                "unidade": "unidades",
                "valor_padrao": 6,
                "preco_referencia": 2200,
                "descricao": "12.000 BTU/h"
            },
            "Split 18000 BTU": {
                "unidade": "unidades",
                "valor_padrao": 3,
                "preco_referencia": 2800,
                "descricao": "18.000 BTU/h"
            },
            "Split 24000 BTU": {
                "unidade": "unidades",
                "valor_padrao": 2,
                "preco_referencia": 3500,
                "descricao": "24.000 BTU/h"
            },
            "MultiSplit Evaporadoras": {
                "unidade": "unidades",
                "valor_padrao": 0,
                "preco_referencia": 1500,
                "descricao": "Para sistemas MultiSplit"
            },
            "Condensadoras MultiSplit": {
                "unidade": "unidades",
                "valor_padrao": 0,
                "preco_referencia": 3000,
                "descricao": "Para sistemas MultiSplit"
            }
        }
    
    return equipamentos

def calcular_custo_equipamentos(quantidades, precos_referencia, sistema):
    """Calcula o custo total baseado nas quantidades informadas"""
    
    custo_total = 0
    detalhes = {}
    
    for equipamento, dados in quantidades.items():
        quantidade = dados["quantidade"]
        preco_unitario = precos_referencia.get(equipamento, 0)
        
        if "TR" in equipamento or "tr" in equipamento.lower():
            # Para equipamentos baseados em TR
            if sistema == "Água Gelada" and "Chiller" in equipamento:
                preco_total = quantidade * preco_unitario
            elif sistema == "VRF/VRV" and "Condensadoras" in equipamento:
                preco_total = quantidade * preco_unitario
            else:
                preco_total = quantidade * preco_unitario
        else:
            preco_total = quantidade * preco_unitario
        
        custo_total += preco_total
        detalhes[equipamento] = {
            "quantidade": quantidade,
            "preco_unitario": preco_unitario,
            "preco_total": preco_total
        }
    
    return custo_total, detalhes

def criar_interface_quantificacao(sistema, uf="SP"):
    """Cria interface completa de quantificação"""
    
    from sinapi_integration import get_precos_equipamentos
    
    st.markdown("---")
    st.header("🔧 Dimensionamento do Projeto")
    
    # Tabela de equipamentos
    equipamentos = criar_tabela_quantificacao(sistema)
    
    # Carregar preços de referência
    precos_uf = get_precos_equipamentos(uf)
    precos_sistema = precos_uf.get(sistema, {})
    
    # Criar formulário de quantidades
    quantidades = {}
    
    col1, col2 = st.columns(2)
    
    for i, (equipamento, dados) in enumerate(equipamentos.items()):
        with col1 if i % 2 == 0 else col2:
            with st.container():
                st.markdown(f"**{equipamento}**")
                st.caption(f"{dados['descricao']}")
                
                quantidade = st.number_input(
                    f"Quantidade ({dados['unidade']})",
                    min_value=0,
                    value=dados['valor_padrao'],
                    step=1,
                    key=f"qtd_{equipamento}"
                )
                
                preco_unitario = precos_sistema.get(equipamento.split('(')[0].strip().replace(" ", "_").lower(), dados['preco_referencia'])
                
                col_q1, col_q2 = st.columns(2)
                with col_q1:
                    st.caption(f"Preço unitário: R$ {preco_unitario:,.2f}")
                with col_q2:
                    st.caption(f"Subtotal: R$ {quantidade * preco_unitario:,.2f}")
                
                quantidades[equipamento] = {
                    "quantidade": quantidade,
                    "preco_unitario": preco_unitario,
                    "unidade": dados["unidade"]
                }
    
    # Calcular total
    custo_equipamentos, detalhes = calcular_custo_equipamentos(quantidades, {}, sistema)
    
    # Recalcular com os preços corretos
    custo_equipamentos = 0
    for equipamento, dados in quantidades.items():
        chave_equip = equipamento.split('(')[0].strip().replace(" ", "_").lower()
        preco = precos_sistema.get(chave_equip, 0)
        if preco == 0:
            # Tentar mapeamento alternativo
            for k, v in precos_sistema.items():
                if k.lower() in equipamento.lower():
                    preco = v
                    break
        if preco == 0:
            preco = equipamentos[equipamento]["preco_referencia"]
        
        custo_equipamentos += dados["quantidade"] * preco
    
    st.markdown("---")
    
    # Resumo
    with st.expander("📋 Resumo da Quantificação", expanded=True):
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("Custo Total Equipamentos", f"R$ {custo_equipamentos:,.2f}")
        with col_r2:
            st.metric("Total de Itens", f"{sum(d['quantidade'] for d in quantidades.values())} unidades")
        with col_r3:
            st.metric("Sistema", sistema)
    
    return custo_equipamentos, quantidades
