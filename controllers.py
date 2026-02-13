import streamlit as st
st.set_page_config(layout="wide", page_title="Sistema de Caronas")

import pandas as pd
from models import CaronaModel
from views import CaronaView

class CaronaController:
    def __init__(self):
        self.model = CaronaModel()
        self.view = CaronaView()

    def run(self):
        result_sidebar = self.view.render_sidebar()
        
        if result_sidebar and result_sidebar[0] == "CREATE":
            _, tipo, nome, endereco, vagas, dias_selecionados, _, _, _, _ = result_sidebar
            
            dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
            
            if nome:
                if tipo == "Motorista":
                    new_data = {"Nome": nome, "Vagas": vagas}
                    for dia in dias_semana:
                        new_data[dia] = "ON" if dias_selecionados.get(dia) else "OFF"
                    
                    new_df = pd.DataFrame([new_data])
                    self.model.save_new_driver(new_df)
                else:
                    new_data = {"Nome": nome, "Endereço": endereco}
                    for dia in dias_semana:
                        new_data[dia] = "" if dias_selecionados.get(dia) else "NÃO VAI"
                    
                    new_df = pd.DataFrame([new_data])
                    self.model.save_new_passenger(new_df)
                
                st.success("Criado com sucesso!")
                st.rerun()

        selected_day = self.view.render_day_selector() 

        df_drivers = self.model.get_drivers()
        df_passengers = self.model.get_passengers()

        result_dash = self.view.render_mobile_dashboard(
            df_drivers, 
            df_passengers, 
            selected_day
        )

        if result_dash:
            action, _, _, _, _, _, param1, param2, param3, param4 = result_dash

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
                self.model.update_driver_full(param1, param2, param3, param4)
                st.toast("Motorista atualizado (Local)")
                st.rerun()

            elif action == "DELETE_DRIVER":
                self.model.delete_driver(param1)
                st.toast("Motorista removido (Local)")
                st.rerun()
                
            elif action == "SAVE_TO_CLOUD":
                self.model.commit_changes()
                st.rerun()