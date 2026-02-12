import streamlit as st

class CaronaView:
    def render_sidebar(self):
        with st.sidebar:
            st.header("Cadastro")
            tipo = st.radio("Tipo", ["Passageiro", "Motorista"])
            nome = st.text_input("Nome")
            regiao = st.selectbox("Região", ["Centro", "Zona Norte", "Zona Sul", "Zona Leste", "Zona Oeste"])
            vagas = 0
            
            if tipo == "Motorista":
                vagas = st.number_input("Vagas", 1, 6, 4)
            
            btn_add = st.button("Adicionar")
            return btn_add, tipo, nome, regiao, vagas

    def render_tables(self, df_drivers, df_passengers):
        st.subheader("Gerenciamento de Listas")
        c1, c2 = st.columns(2)
        
        with c1:
            st.write("🚗 **Motoristas**")
            new_drivers = st.data_editor(df_drivers, num_rows="dynamic", key="edit_drv")
        
        with c2:
            st.write("🙋‍♂️ **Passageiros**")
            new_passengers = st.data_editor(df_passengers, num_rows="dynamic", key="edit_pas")
            
        return new_drivers, new_passengers

    def render_allocation_button(self):
        st.divider()
        return st.button("🚀 Gerar Rotas e Alocações", type="primary")

    def render_results(self, df_result, left_overs):
        st.subheader("Resultado da Distribuição")
        st.table(df_result)
        
        if left_overs:
            st.error(f"⚠️ Pessoas sem carona: {', '.join(left_overs)}")
        else:
            st.success("✅ Todos foram alocados!")