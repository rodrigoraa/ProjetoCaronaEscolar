import streamlit as st
from models import CaronaModel
from views import CaronaView

class CaronaController:
    def __init__(self):
        self.model = CaronaModel()
        self.view = CaronaView()

    def run(self):
        st.title("Sistema de Caronas 🚗")

        btn_add, tipo, nome, regiao, vagas = self.view.render_sidebar()
        
        if btn_add and nome:
            if tipo == "Motorista":
                self.model.add_driver(nome, vagas, regiao)
                st.success(f"Motorista {nome} adicionado!")
            else:
                self.model.add_passenger(nome, regiao)
                st.success(f"Passageiro {nome} adicionado!")
            st.rerun()

        df_d = self.model.get_drivers()
        df_p = self.model.get_passengers()
        
        edited_drivers, edited_passengers = self.view.render_tables(df_d, df_p)
        
        if not df_d.equals(edited_drivers):
            self.model.update_drivers(edited_drivers)

        if not df_p.equals(edited_passengers):
            self.model.update_passengers(edited_passengers)

        if self.view.render_allocation_button():
            result_df, leftovers = self.model.allocate_rides()
            self.view.render_results(result_df, leftovers)