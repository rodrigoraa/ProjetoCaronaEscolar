import pandas as pd
import streamlit as st

class CaronaModel:
    def __init__(self):
        if 'drivers' not in st.session_state:
            st.session_state['drivers'] = pd.DataFrame(
                columns=["Nome", "Vagas", "Região"]
            )
        if 'passengers' not in st.session_state:
            st.session_state['passengers'] = pd.DataFrame(
                columns=["Nome", "Região"]
            )

    def get_drivers(self):
        return st.session_state['drivers']

    def get_passengers(self):
        return st.session_state['passengers']

    def add_driver(self, nome, vagas, regiao):
        new_driver = pd.DataFrame([{"Nome": nome, "Vagas": vagas, "Região": regiao}])
        st.session_state['drivers'] = pd.concat([st.session_state['drivers'], new_driver], ignore_index=True)

    def add_passenger(self, nome, regiao):
        new_passenger = pd.DataFrame([{"Nome": nome, "Região": regiao}])
        st.session_state['passengers'] = pd.concat([st.session_state['passengers'], new_passenger], ignore_index=True)

    def update_drivers(self, new_df):
        st.session_state['drivers'] = new_df

    def update_passengers(self, new_df):
        st.session_state['passengers'] = new_df

    def allocate_rides(self):
        drivers = st.session_state['drivers'].copy()
        passengers = st.session_state['passengers']['Nome'].tolist()
        allocation_results = []

        for index, driver in drivers.iterrows():
            seats = int(driver['Vagas'])
            allocated = []
        
            while seats > 0 and passengers:
                allocated.append(passengers.pop(0))
                seats -= 1
            
            allocation_results.append({
                "Motorista": driver['Nome'],
                "Região": driver['Região'],
                "Passageiros": ", ".join(allocated) if allocated else "---",
                "Vagas Livres": seats
            })
        
        return pd.DataFrame(allocation_results), passengers