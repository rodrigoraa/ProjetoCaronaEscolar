import streamlit as st
import pandas as pd
import urllib.parse
from utils.pdf_service import gerar_pdf_relatorio 

class CaronaView:
    def render_sidebar(self):
        with st.sidebar:
            st.header("Novo Cadastro")
            tipo = st.radio("Tipo", ["Passageiro", "Motorista"], horizontal=True)
            nome = st.text_input("Nome")
            
            telefone = ""
            vagas = 0
            if tipo == "Motorista":
                telefone = st.text_input("WhatsApp (Ex: 5511999999999)")
                vagas = st.number_input("Vagas totais", 1, 6, 4)
            
            st.write(f"📅 **Dias de atividade ({tipo}):**")
            dias_selecionados = {}
            c1, c2, c3 = st.columns(3)
            dias_selecionados["Segunda"] = c1.checkbox("Seg", value=True)
            dias_selecionados["Terça"] = c2.checkbox("Ter", value=True)
            dias_selecionados["Quarta"] = c3.checkbox("Qua", value=True)
            dias_selecionados["Quinta"] = c1.checkbox("Qui", value=True)
            dias_selecionados["Sexta"] = c2.checkbox("Sex", value=True)
            
            if st.button("Salvar Cadastro", type="primary", use_container_width=True):
                return "CREATE", tipo, nome, telefone, vagas, dias_selecionados, None, None, None, None, None

            st.divider()
            if st.button("🔄 Recarregar Dados", use_container_width=True):
                st.session_state.clear()
                st.rerun()
            
            return None, None, None, None, None, None, None, None, None, None, None

    def render_day_selector(self):
        days = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        st.write("### Selecione o Dia:")
        return st.radio("Selecione o dia", days, horizontal=True, label_visibility="collapsed")

    def _aplicar_estilos(self):
        st.markdown("""
            <style>
                .block-container { padding: 1.5rem 0.5rem 5rem 0.5rem !important; max-width: 100%; }
                header {visibility: hidden;} footer {visibility: hidden;}
                .streamlit-expanderHeader { font-size: 16px; font-weight: 600; }
                div[data-testid="stExpanderDetails"] div[data-testid="stVerticalBlock"] { gap: 0.1rem !important; }
                div[data-testid="stExpanderDetails"] div[data-testid="column"] { padding: 0 !important; }
                div[data-testid="stExpanderDetails"] div.element-container { margin-bottom: 0 !important; }
                div[data-testid="stExpanderDetails"] button[kind="secondary"] { min-height: 2rem !important; padding: 0 !important; }
            </style>
        """, unsafe_allow_html=True)

    def _renderizar_resumo(self, stats):
        with st.expander("📊 Resumo do Dia", expanded=False):
            m1, m2 = st.columns(2)
            m1.metric("Total de Passageiros", stats["total_passengers"])
            m2.metric("Passageiros Alocados", stats["alocados"])
            
            m3, m4 = st.columns(2)
            m3.metric("Passageiros Não Alocados", stats["nao_alocados"], delta_color="inverse")
            m4.metric("Total de Motoristas", stats["total_motoristas"])
            
            st.metric("Motoristas c/ Vagas Livres", stats["motoristas_com_vagas"])

    def _renderizar_grid_motoristas(self, active_drivers, df_passengers, sem_carona, mapa_vagas, selected_day):
        num_cols = 3
        grid_cols = st.columns(num_cols, gap="small")

        for i, (index, driver) in enumerate(active_drivers):
            with grid_cols[i % num_cols]:
                driver_name = driver['Nome']
                telefone_motorista = str(driver.get('Telefone', '')).split('.')[0].strip()
                total_vagas = int(driver.get('Vagas', 4))

                current_passengers = df_passengers[df_passengers[selected_day] == driver_name]
                ocupados = len(current_passengers)
                vagas_restantes = total_vagas - ocupados
                
                progresso = min(ocupados / total_vagas if total_vagas > 0 else 0, 1.0)
                is_expanded = st.session_state.get("motorista_ativo") == driver_name

                with st.expander(f"🚗 {driver_name} • {ocupados}/{total_vagas}", expanded=is_expanded):
                    st.progress(progresso)
                    
                    swap_key = f"swap_mode_{index}"
                    if ocupados > 0:
                        if st.button("🔄 Trocar Motorista", key=f"btn_swap_toggle_{index}", use_container_width=True):
                            st.session_state[swap_key] = not st.session_state.get(swap_key, False)
                        
                        if st.session_state.get(swap_key, False):
                            st.info("Transferir para:")
                            candidatos_validos = [m for m, v in mapa_vagas.items() if m != driver_name and v >= ocupados]
                            
                            if candidatos_validos:
                                novo_motorista = st.selectbox("Selecione o destino:", candidatos_validos, key=f"sel_swap_{index}", label_visibility="collapsed")
                                c_conf, c_canc = st.columns(2)
                                if c_conf.button("✅ Confirmar", key=f"btn_conf_swap_{index}", use_container_width=True):
                                    st.session_state[swap_key] = False
                                    return "TRANSFER_ALL", None, None, None, None, None, driver_name, novo_motorista, None, None, None
                                if c_canc.button("❌ Cancelar", key=f"btn_canc_swap_{index}", use_container_width=True):
                                    st.session_state[swap_key] = False
                                    st.rerun()
                            else:
                                st.error(f"Nenhum com {ocupados} vagas.")
                    
                    st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 2px solid rgba(128,128,128,0.2);'>", unsafe_allow_html=True)
                    
                    if not current_passengers.empty:
                        for idx_p, passenger in current_passengers.iterrows():
                            p_name = passenger['Nome']
                            c_info, c_action = st.columns([6, 1]) 
                            with c_info:
                                st.markdown(f"<div style='line-height: 1.2; padding-top: 0.2rem;'><strong>{p_name}</strong></div>", unsafe_allow_html=True)
                            with c_action:
                                if st.button("❌", key=f"rem_{driver_name}_{p_name}_{selected_day}"):
                                    st.session_state["motorista_ativo"] = driver_name
                                    return "REMOVE", None, None, None, None, None, p_name, None, None, None, None

                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    mensagem = f"Olá, O Expresso do Conhecimento já tem seus passageiros confirmados para {selected_day}, com destino à escola: \n\n"
                    if not current_passengers.empty:
                        for idx_p, passenger in current_passengers.iterrows():
                            mensagem += f"✓ {passenger['Nome']}\n"
                    else:
                        mensagem += "Nenhum passageiro alocado ainda. 📭\n"

                    msg_codificada = urllib.parse.quote(mensagem)
                    num_limpo = ''.join(filter(str.isdigit, telefone_motorista))
                    
                    link_wpp = f"https://wa.me/{num_limpo}?text={msg_codificada}" if num_limpo else f"https://wa.me/?text={msg_codificada}"
                    st.link_button("📱 Enviar WhatsApp", link_wpp, use_container_width=True)

                    if ocupados < total_vagas:
                        opcoes = sem_carona['Nome'].tolist()
                        if opcoes:
                            escolhidos = st.multiselect(
                                f"Add ({vagas_restantes})", opcoes, max_selections=vagas_restantes,
                                key=f"sel_{driver_name}_{selected_day}", label_visibility="collapsed", placeholder="+ Passageiro..."
                            )
                            if escolhidos:
                                if st.button("Adicionar", key=f"add_{driver_name}_{selected_day}", use_container_width=True):
                                    st.session_state["motorista_ativo"] = driver_name
                                    return "ADD_BULK", None, None, None, None, None, escolhidos, driver_name, None, None, None
                    
                    with st.expander("⚙️ Editar Motorista"):
                        new_name = st.text_input("Nome", value=driver_name, key=f"n_{index}")
                        new_telefone = st.text_input("WhatsApp", value=telefone_motorista, key=f"t_{index}")
                        new_vagas = st.number_input("Vagas", 1, 8, total_vagas, key=f"v_{index}")
                        st.caption("Dias ON:")
                        new_days = {}
                        days_list = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
                        cols_dias = st.columns(3) + st.columns(2)
                        
                        for k, d in enumerate(days_list):
                            is_checked = not (d in driver and driver[d] == "OFF")
                            new_days[d] = cols_dias[k].checkbox(d[:3], value=is_checked, key=f"d_{d}_{index}")

                        if st.button("💾 Salvar", key=f"save_{index}", use_container_width=True):
                            return "UPDATE_DRIVER", None, None, None, None, None, driver_name, new_name, new_telefone, new_vagas, new_days
                        
                        if st.button("🗑️ Excluir", key=f"del_{index}", use_container_width=True):
                             return "DELETE_DRIVER", None, None, None, None, None, driver_name, None, None, None, None

        return None

    def render_mobile_dashboard(self, active_drivers, sem_carona, mapa_vagas, stats, df_passengers, selected_day):
        self._aplicar_estilos()

        if st.session_state.get('unsaved_changes'):
            st.warning("⚠️ Você tem alterações não salvas! Clique em 'Salvar Tudo' no final da página.")
        
        st.header(f"📅 Gestão: {selected_day}")
        
        self._renderizar_resumo(stats)
        st.divider()

        pdf_bytes = gerar_pdf_relatorio(active_drivers, df_passengers, selected_day)
        st.download_button(
            label="📄 Imprimir Relatório Geral (PDF)", data=pdf_bytes, file_name=f"Relatorio_Geral_{selected_day}.pdf",
            mime="application/pdf", use_container_width=True, type="primary"
        )
        st.divider()

        action_result = self._renderizar_grid_motoristas(active_drivers, df_passengers, sem_carona, mapa_vagas, selected_day)
        if action_result:
            return action_result

        st.divider()
        
        if st.session_state.get('unsaved_changes'):
            if st.button("💾 SALVAR TUDO NA PLANILHA", type="primary", use_container_width=True):
                return "SAVE_TO_CLOUD", None, None, None, None, None, None, None, None, None, None
        else:
            st.caption("✅ Tudo sincronizado.")

        return None, None, None, None, None, None, None, None, None, None, None