import streamlit as st
import pandas as pd

class CaronaView:
    def render_sidebar(self):
        with st.sidebar:
            st.header("Novo Cadastro")
            tipo = st.radio("Tipo", ["Passageiro", "Motorista"], horizontal=True)
            nome = st.text_input("Nome")
            
            endereco = ""
            if tipo == "Passageiro":
                endereco = st.text_input("Endereço")
            
            vagas = 0
            if tipo == "Motorista":
                vagas = st.number_input("Vagas totais", 1, 6, 4)
            
            st.write(f"📅 **Dias de atividade ({tipo}):**")
            dias_selecionados = {}
            c1, c2, c3 = st.columns(3)
            dias_selecionados["Segunda"] = c1.checkbox("Seg", value=True)
            dias_selecionados["Terça"] = c2.checkbox("Ter", value=True)
            dias_selecionados["Quarta"] = c3.checkbox("Qua", value=True)
            dias_selecionados["Quinta"] = c1.checkbox("Qui", value=True)
            dias_selecionados["Sexta"] = c2.checkbox("Sex", value=True)
            
            if st.button("Salvar Cadastro", type="primary"):
                return "CREATE", tipo, nome, endereco, vagas, dias_selecionados, None, None, None, None

            st.divider()
            if st.button("🔄 Recarregar Dados"):
                st.session_state.clear()
                st.rerun()
            
            return None, None, None, None, None, None, None, None, None, None

    def render_day_selector(self):
        days = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        st.write("### Selecione o Dia:")
        selected_day = st.radio("Selecione o dia", days, horizontal=True, label_visibility="collapsed")
        return selected_day

    def render_mobile_dashboard(self, df_drivers, df_passengers, selected_day):
        st.markdown("""
            <style>
                .block-container {
                    padding-top: 1rem;
                    padding-bottom: 5rem;
                    padding-left: 2rem;
                    padding-right: 2rem;
                    max-width: 100%;
                }
                /* Deixa o botão de troca largura total para facilitar o clique no mobile */
                div[data-testid="stButton"] button {
                    width: 100%;
                }
            </style>
        """, unsafe_allow_html=True)

        if st.session_state.get('unsaved_changes'):
            st.warning("⚠️ Você tem alterações não salvas! Clique em 'Salvar Tudo' no final da página.")
        
        st.header(f"📅 Gestão: {selected_day}")

        active_drivers = []
        for index, row in df_drivers.iterrows():
            if not (selected_day in row and row[selected_day] == "OFF"):
                active_drivers.append((index, row))

        def count_passengers(driver_data):
            d_name = driver_data[1]['Nome']
            return len(df_passengers[df_passengers[selected_day] == d_name])

        active_drivers.sort(key=count_passengers, reverse=True)

        nao_vai = df_passengers[df_passengers[selected_day] == "NÃO VAI"]
        sem_carona = df_passengers[
            (df_passengers[selected_day] != "NÃO VAI") & 
            ((df_passengers[selected_day].isnull()) | (df_passengers[selected_day] == ""))
        ]

        qtd_total_passengers = len(df_passengers) - len(nao_vai)
        qtd_nao_alocados = len(sem_carona)
        qtd_alocados = qtd_total_passengers - qtd_nao_alocados
        qtd_total_motoristas = len(active_drivers)
        
        mapa_vagas = {} 
        qtd_motoristas_vagas = 0
        
        for idx, d in active_drivers:
            d_name = d['Nome']
            try:
                tot = int(d['Vagas'])
            except:
                tot = 4
            ocp = len(df_passengers[df_passengers[selected_day] == d_name])
            
            restante = tot - ocp
            if restante > 0:
                qtd_motoristas_vagas += 1
                mapa_vagas[d_name] = restante

        st.markdown("##### Resumo do Dia")
        m1, m2 = st.columns(2)
        m1.metric("Total Passageiros (Ativos)", qtd_total_passengers)
        m2.metric("Passageiros Alocados", qtd_alocados)
        
        m3, m4 = st.columns(2)
        m3.metric("Passageiros Não Alocados", qtd_nao_alocados, delta_color="inverse")
        m4.metric("Total Motoristas (Hoje)", qtd_total_motoristas)
        m5 = st.columns(1)[0]
        m5.metric("Motoristas c/ Vagas Livres", qtd_motoristas_vagas)
        
        st.divider()

        num_cols = 3
        grid_cols = st.columns(num_cols, gap="small")

        for i, (index, driver) in enumerate(active_drivers):
            with grid_cols[i % num_cols]:
                driver_name = driver['Nome']
                try:
                    total_vagas = int(driver['Vagas'])
                except:
                    total_vagas = 4

                current_passengers = df_passengers[df_passengers[selected_day] == driver_name]
                ocupados = len(current_passengers)
                vagas_restantes = total_vagas - ocupados
                
                progresso = ocupados / total_vagas if total_vagas > 0 else 0
                if progresso > 1: progresso = 1
                
                with st.container(height=850, border=True):
                    col_a, col_b = st.columns([3, 1])
                    col_a.subheader(f"🚗 {driver_name}")
                    col_b.write(f"**{ocupados}/{total_vagas}**")
                    st.progress(progresso)
                    
                    swap_key = f"swap_mode_{index}"
                    
                    if ocupados > 0:
                        if st.button("🔄 Trocar", key=f"btn_swap_toggle_{index}"):
                            st.session_state[swap_key] = not st.session_state.get(swap_key, False)
                        
                        if st.session_state.get(swap_key, False):
                            st.info("Transferir passageiros para:")
                            
                            candidatos_validos = [m for m, v in mapa_vagas.items() if m != driver_name and v >= ocupados]
                            
                            if candidatos_validos:
                                novo_motorista = st.selectbox(
                                    "Selecione o destino:", 
                                    candidatos_validos, 
                                    key=f"sel_swap_{index}",
                                    label_visibility="collapsed"
                                )
                                
                                c_conf, c_canc = st.columns(2)
                                if c_conf.button("✅ Confirmar", key=f"btn_conf_swap_{index}"):
                                    st.session_state[swap_key] = False
                                    return "TRANSFER_ALL", None, None, None, None, None, driver_name, novo_motorista, None, None
                                
                                if c_canc.button("❌ Cancelar", key=f"btn_canc_swap_{index}"):
                                    st.session_state[swap_key] = False
                                    st.rerun()
                            else:
                                st.error(f"Nenhum motorista com {ocupados} vagas livres.")
                    
                    if not current_passengers.empty:
                        for idx_p, passenger in current_passengers.iterrows():
                            p_name = passenger['Nome']
                            c_info, c_action = st.columns([4, 1])
                            
                            with c_info:
                                st.write(f"**{p_name}**")
                                if 'Endereço' in passenger:
                                    end_str = str(passenger['Endereço']).strip()
                                    if end_str and end_str.lower() != "nan" and end_str.lower() != "none":
                                        st.caption(f"{end_str}")
                            
                            if c_action.button("❌", key=f"rem_{driver_name}_{p_name}_{selected_day}"):
                                return "REMOVE", None, None, None, None, None, p_name, None, None, None
                            
                            st.divider()

                    if ocupados < total_vagas:
                        opcoes = sem_carona['Nome'].tolist()
                        if opcoes:
                            escolhidos = st.multiselect(
                                f"Add ({vagas_restantes})", 
                                opcoes, 
                                max_selections=vagas_restantes,
                                key=f"sel_{driver_name}_{selected_day}",
                                label_visibility="collapsed",
                                placeholder="Adicionar..."
                            )
                            if escolhidos:
                                if st.button("Adicionar", key=f"add_{driver_name}_{selected_day}", use_container_width=True):
                                    return "ADD_BULK", None, None, None, None, None, escolhidos, driver_name, None, None
                    
                    with st.expander("⚙️ Editar Motorista"):
                        new_name = st.text_input("Nome", value=driver_name, key=f"n_{index}")
                        new_vagas = st.number_input("Vagas", 1, 8, total_vagas, key=f"v_{index}")
                        
                        st.caption("Dias ON:")
                        new_days = {}
                        days_list = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
                        cols_dias = st.columns(5)
                        for k, d in enumerate(days_list):
                            is_checked = True
                            if d in driver and driver[d] == "OFF":
                                is_checked = False
                            new_days[d] = cols_dias[k].checkbox(d[:3], value=is_checked, key=f"d_{d}_{index}")

                        if st.button("💾 Salvar Alterações", key=f"save_{index}", use_container_width=True):
                            return "UPDATE_DRIVER", None, None, None, None, None, driver_name, new_name, new_vagas, new_days
                        
                        if st.button("🗑️ Excluir Motorista", key=f"del_{index}", use_container_width=True):
                             return "DELETE_DRIVER", None, None, None, None, None, driver_name, None, None, None

        st.divider()
        if st.session_state.get('unsaved_changes'):
            if st.button("💾 SALVAR TUDO NA PLANILHA", type="primary", use_container_width=True):
                return "SAVE_TO_CLOUD", None, None, None, None, None, None, None, None, None
        else:
            st.caption("✅ Tudo sincronizado.")

        return None, None, None, None, None, None, None, None, None, None