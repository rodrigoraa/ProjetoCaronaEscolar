import streamlit as st
st.set_page_config(layout="wide", page_title="Sistema de Caronas")

import pandas as pd
from models import CaronaModel
from views import CaronaView

class CaronaController:
    def __init__(self):
        self.model = CaronaModel()
        self.view = CaronaView()

    def processar_estatisticas(self, df_drivers, df_passengers, selected_day):
        active_drivers = [
            (idx, row) for idx, row in df_drivers.iterrows() 
            if not (selected_day in row and row[selected_day] == "OFF")
        ]
        
        active_drivers.sort(
            key=lambda d: (
                len(df_passengers[df_passengers[selected_day] == d[1]['Nome']]) == 0, 
                d[1]['Nome']
            )
        )

        nao_vai = df_passengers[df_passengers[selected_day] == "NÃO VAI"]
        sem_carona = df_passengers[
            (df_passengers[selected_day] != "NÃO VAI") & 
            ((df_passengers[selected_day].isnull()) | (df_passengers[selected_day] == ""))
        ]

        mapa_vagas = {}
        qtd_motoristas_vagas = 0
        for idx, d in active_drivers:
            d_name = d['Nome']
            tot = int(d.get('Vagas', 4))
            ocp = len(df_passengers[df_passengers[selected_day] == d_name])
            restante = tot - ocp
            if restante > 0:
                qtd_motoristas_vagas += 1
                mapa_vagas[d_name] = restante

        stats = {
            "total_passengers": len(df_passengers) - len(nao_vai),
            "nao_alocados": len(sem_carona),
            "alocados": (len(df_passengers) - len(nao_vai)) - len(sem_carona),
            "total_motoristas": len(active_drivers),
            "motoristas_com_vagas": qtd_motoristas_vagas
        }
        
        return active_drivers, sem_carona, mapa_vagas, stats

    def run(self):
        result_sidebar = self.view.render_sidebar()
        
        if result_sidebar and result_sidebar[0] == "CREATE":
            tupla_sidebar = result_sidebar + (None,) * (11 - len(result_sidebar))
            _, tipo, nome, telefone, vagas, dias_selecionados, _, _, _, _, _ = tupla_sidebar
            
            dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
            
            if nome:
                if tipo == "Motorista":
                    new_data = {"Nome": nome, "Telefone": telefone, "Vagas": vagas}
                    for dia in dias_semana:
                        new_data[dia] = "ON" if dias_selecionados.get(dia) else "OFF"
                    
                    new_df = pd.DataFrame([new_data])
                    self.model.save_new_driver(new_df)
                else:
                    new_data = {"Nome": nome} 
                    for dia in dias_semana:
                        new_data[dia] = "" if dias_selecionados.get(dia) else "NÃO VAI"
                    
                    new_df = pd.DataFrame([new_data])
                    self.model.save_new_passenger(new_df)
                
                st.success("Criado com sucesso!")
                st.rerun()

        selected_day = self.view.render_day_selector() 

        df_drivers = self.model.get_drivers()
        df_passengers = self.model.get_passengers()

        active_drivers, sem_carona, mapa_vagas, stats = self.processar_estatisticas(
            df_drivers, df_passengers, selected_day
        )

        result_dash = self.view.render_mobile_dashboard(
            active_drivers, sem_carona, mapa_vagas, stats, df_passengers, selected_day
        )

        if result_dash:
            tupla_completa = result_dash + (None,) * (11 - len(result_dash))
            action, _, _, _, _, _, param1, param2, param3, param4, param5 = tupla_completa

            if action == "ADD_BULK":
                if param1: 
                    self.model.assign_passenger_bulk(param1, param2, selected_day)
                    st.rerun()
            
            elif action == "MOVE":
                self.model.assign_passenger(param1, param2, selected_day)
                st.toast(f"{param1} movido localmente.")
                st.rerun()

            elif action == "TRANSFER_ALL":
                self.model.transfer_passengers(param1, param2, selected_day)
                st.toast(f"Transferidos de {param1} para {param2} (Local)")
                st.rerun()
                
            elif action == "REMOVE":
                self.model.unassign_passenger(param1, selected_day)
                st.rerun()
            
            elif action == "UPDATE_DRIVER":
                self.model.update_driver_full(param1, param2, param3, param4, param5)
                st.toast("Motorista atualizado (Local)")
                st.rerun()

            elif action == "DELETE_DRIVER":
                self.model.delete_driver(param1)
                st.toast("Motorista removido (Local)")
                st.rerun()
                
            elif action == "SAVE_TO_CLOUD":
                with st.spinner("☁️ Salvando na planilha do Google..."):
                    self.model.commit_changes()
                st.toast("✅ Todos os dados foram salvos!", icon="💾")
                st.rerun()