import streamlit as st

def criar_tabela_quantificacao(sistema):
    """Cria interface para quantificação de equipamentos"""
    
    st.subheader("📊 Quantificação de Equipamentos")
    
    if sistema == "VRF/VRV":
        equipamentos = {
            "Condensadoras VRF (TR)": {
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
            "Bombas d'Água": {
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
            }
        }
    
    return equipamentos

def criar_interface_quantificacao(sistema, uf="SP"):
    """Cria interface completa de quantificação"""
    
    from sinapi_integration import get_precos_equipamentos
    
    st.markdown("---")
    st.header("🔧 Dimensionamento do Projeto")
    
    equipamentos = criar_tabela_quantificacao(sistema)
    
    try:
        precos_uf = get_precos_equipamentos(uf)
        precos_sistema = precos_uf.get(sistema, {})
    except:
        precos_sistema = {}
    
    quantidades = {}
    custo_equipamentos = 0
    
    col1, col2 = st.columns(2)
    
    for i, (equipamento, dados) in enumerate(equipamentos.items()):
        with col1 if i % 2 == 0 else col2:
            with st.container(border=True):
                st.markdown(f"**{equipamento}**")
                st.caption(dados['descricao'])
                
                quantidade = st.number_input(
                    f"Quantidade ({dados['unidade']})",
                    min_value=0.0,
                    value=float(dados['valor_padrao']),
                    step=1.0,
                    key=f"qtd_{equipamento}"
                )
                
                # Buscar preço unitário
                chave_busca = equipamento.split('(')[0].strip().replace(" ", "_").lower()
                preco_unitario = dados['preco_referencia']
                
                for k, v in precos_sistema.items():
                    if k.lower() in chave_busca or chave_busca in k.lower():
                        preco_unitario = v
                        break
                
                subtotal = quantidade * preco_unitario
                custo_equipamentos += subtotal
                
                col_q1, col_q2 = st.columns(2)
                with col_q1:
                    st.caption(f"Preço unitário: R$ {preco_unitario:,.2f}")
                with col_q2:
                    st.caption(f"Subtotal: R$ {subtotal:,.2f}")
                
                quantidades[equipamento] = {
                    "quantidade": quantidade,
                    "preco_unitario": preco_unitario,
                    "subtotal": subtotal,
                    "unidade": dados["unidade"]
                }
    
    st.markdown("---")
    
    with st.expander("📋 Resumo da Quantificação", expanded=True):
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("Custo Total Equipamentos", f"R$ {custo_equipamentos:,.2f}")
        with col_r2:
            total_itens = sum(d['quantidade'] for d in quantidades.values())
            st.metric("Total de Itens", f"{total_itens:.0f} unidades")
        with col_r3:
            st.metric("Sistema", sistema)
    
    return custo_equipamentos, quantidades
