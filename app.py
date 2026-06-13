""")

st.markdown("---")
st.header("💰 ORÇAMENTO (atualiza em tempo real)")

col1, col2 = st.columns(2)

with col1:
st.subheader("🎯 MODELO DIRETO")

with st.expander("📦 Equipamentos", expanded=True):
    st.session_state.valores['equip_cond'] = st.number_input("Condensadoras/Chiller", value=st.session_state.valores['equip_cond'], step=5000.0)
    st.session_state.valores['equip_evap'] = st.number_input("Evaporadoras/Fan Coils", value=st.session_state.valores['equip_evap'], step=5000.0)
    st.session_state.valores['equip_bms'] = st.number_input("BMS/Controles", value=st.session_state.valores['equip_bms'], step=1000.0)

with st.expander("🔩 Insumos", expanded=True):
    st.session_state.valores['ins_cobre'] = st.number_input("Cobre + Isolante", value=st.session_state.valores['ins_cobre'], step=1000.0)
    st.session_state.valores['ins_drenos'] = st.number_input("Drenos + Eletrodutos", value=st.session_state.valores['ins_drenos'], step=500.0)
    st.session_state.valores['ins_outros'] = st.number_input("Outros insumos", value=st.session_state.valores['ins_outros'], step=500.0)

with st.expander("👷 Mão de Obra", expanded=True):
    st.session_state.valores['mao_tec'] = st.number_input("Técnicos", value=st.session_state.valores['mao_tec'], step=2000.0)
    st.session_state.valores['mao_aux'] = st.number_input("Auxiliares", value=st.session_state.valores['mao_aux'], step=1000.0)
    st.session_state.valores['mao_eng'] = st.number_input("Engenharia/Projeto", value=st.session_state.valores['mao_eng'], step=1000.0)

with st.expander("⚙️ Serviços", expanded=True):
    st.session_state.valores['serv_startup'] = st.number_input("Startup/Comissionamento", value=st.session_state.valores['serv_startup'], step=500.0)
    st.session_state.valores['serv_testes'] = st.number_input("Testes + Carga de gás", value=st.session_state.valores['serv_testes'], step=500.0)

col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    st.session_state.valores['garantia'] = st.number_input("Garantia %", value=st.session_state.valores['garantia'], step=0.5)
with col_p2:
    st.session_state.valores['adm'] = st.number_input("Adm/Frete %", value=st.session_state.valores['adm'], step=0.5)
with col_p3:
    st.session_state.valores['margem_dir'] = st.number_input("Margem %", value=st.session_state.valores['margem_dir'], step=1.0)

with col2:
st.subheader("🎯 MODELO TERCEIRO")

st.session_state.valores['fornece_equip'] = st.checkbox("Você fornece equipamentos?", value=st.session_state.valores['fornece_equip'])
if st.session_state.valores['fornece_equip']:
    valor_padrao = st.session_state.valores['equip_cond'] + st.session_state.valores['equip_evap']
    st.session_state.valores['valor_equip_terc'] = st.number_input("Valor equipamentos", value=valor_padrao, step=5000.0)

st.session_state.valores['fornece_insumos'] = st.checkbox("Você fornece insumos?", value=st.session_state.valores['fornece_insumos'])
if st.session_state.valores['fornece_insumos']:
    st.session_state.valores['valor_insumos_terc'] = st.number_input("Valor insumos", value=st.session_state.valores['ins_cobre'], step=2000.0)

st.markdown("---")
st.session_state.valores['mao_terc'] = st.number_input("Mão de obra", value=st.session_state.valores['mao_terc'], step=2000.0)
st.session_state.valores['consumiveis'] = st.number_input("Consumíveis", value=st.session_state.valores['consumiveis'], step=500.0)
st.session_state.valores['startup_terc'] = st.number_input("Startup", value=st.session_state.valores['startup_terc'], step=500.0)
st.session_state.valores['margem_terc'] = st.number_input("Margem Terceiro %", value=st.session_state.valores['margem_terc'], step=1.0)

resultados = calcular_tudo()

st.markdown("---")
col_res1, col_res2 = st.columns(2)

with col_res1:
st.subheader("📊 RESULTADO DIRETO")
st.metric("💰 Seu Custo Total", f"R$ {resultados['custo_total_dir']:,.2f}")
st.metric("🏷️ Preço para Cliente", f"R$ {resultados['preco_cliente']:,.2f}")
st.metric("📈 Seu Lucro", f"R$ {resultados['lucro_dir']:,.2f}")

with col_res2:
st.subheader("📊 RESULTADO TERCEIRO")
st.metric("💰 Seu Custo Total", f"R$ {resultados['custo_total_terc']:,.2f}")
st.metric("🏷️ Preço para Construtora", f"R$ {resultados['preco_terc']:,.2f}")
st.metric("📈 Seu Lucro", f"R$ {resultados['lucro_terc']:,.2f}")

st.markdown("---")
diferenca = resultados['lucro_dir'] - resultados['lucro_terc']
if diferenca > 0:
st.success(f"✅ **Recomendação:** Modelo DIRETO é R$ {diferenca:,.2f} mais lucrativo")
else:
st.info(f"ℹ️ **Recomendação:** Modelo TERCEIRO tem lucro de R$ {resultados['lucro_terc']:,.2f} com menos risco")

st.caption("💡 **Faça upload do projeto (PDF, TXT, DWG) ou preencha manualmente. O sistema extrai automaticamente as informações!**")
