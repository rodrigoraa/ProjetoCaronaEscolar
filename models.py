import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import time

class CaronaModel:
    def __init__(self):
        self.conn = st.connection("gsheets", type=GSheetsConnection)
        self._ensure_data_loaded()

    def _ensure_data_loaded(self):
        if 'unsaved_changes' not in st.session_state:
            st.session_state['unsaved_changes'] = False

        if 'drivers' not in st.session_state or 'passengers' not in st.session_state:
            self.force_reload()

    def mark_unsaved(self):
        st.session_state['unsaved_changes'] = True

    def force_reload(self):
        days = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        try:
            df_drivers = self.conn.read(worksheet="Motoristas", ttl=0)
            if 'Vagas' in df_drivers.columns:
                df_drivers['Vagas'] = pd.to_numeric(df_drivers['Vagas'], errors='coerce').fillna(4).astype(int)
            else:
                df_drivers['Vagas'] = 4
                
            if 'Telefone' not in df_drivers.columns:
                df_drivers['Telefone'] = ""
            
            for day in days:
                if day not in df_drivers.columns:
                    df_drivers[day] = "ON" 
            
            st.session_state['drivers'] = df_drivers

            df_passengers = self.conn.read(worksheet="Passageiros", ttl=0)
            for day in days:
                if day not in df_passengers.columns:
                    df_passengers[day] = None
            
            st.session_state['passengers'] = df_passengers
            st.session_state['unsaved_changes'] = False
            
        except Exception:
            cols_driver = ["Nome", "Telefone", "Vagas"] + days
            st.session_state['drivers'] = pd.DataFrame(columns=cols_driver)
            
            cols_pass = ["Nome"] + days
            st.session_state['passengers'] = pd.DataFrame(columns=cols_pass)

    def commit_changes(self):
        self.conn.update(worksheet="Motoristas", data=st.session_state['drivers'])
        time.sleep(1)
        self.conn.update(worksheet="Passageiros", data=st.session_state['passengers'])
        st.session_state['unsaved_changes'] = False

    def update_driver_full(self, old_name, new_name, new_telefone, new_vagas, new_days_dict):
        df_d = st.session_state['drivers']
        idx = df_d[df_d['Nome'] == old_name].index
        
        if not idx.empty:
            df_d.loc[idx, 'Nome'] = new_name
            df_d.loc[idx, 'Telefone'] = str(new_telefone)
            df_d.loc[idx, 'Vagas'] = new_vagas
            
            for day, is_on in new_days_dict.items():
                df_d.loc[idx, day] = "ON" if is_on else "OFF"
            
            st.session_state['drivers'] = df_d

            if old_name != new_name:
                df_p = st.session_state['passengers']
                days = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
                for day in days:
                    df_p[day] = df_p[day].replace(old_name, new_name)
                st.session_state['passengers'] = df_p

            self.mark_unsaved()
    
    def transfer_passengers(self, old_driver, new_driver, day_column):
        df_p = st.session_state['passengers']
        df_p.loc[df_p[day_column] == old_driver, day_column] = new_driver
        st.session_state['passengers'] = df_p
        self.mark_unsaved()

    def assign_passenger_bulk(self, passenger_list, driver_name, day_column):
        df_p = st.session_state['passengers']
        for p_name in passenger_list:
            df_p.loc[df_p['Nome'] == p_name, day_column] = driver_name
        st.session_state['passengers'] = df_p
        self.mark_unsaved()

    def assign_passenger(self, passenger_name, driver_name, day_column):
        df_p = st.session_state['passengers']
        df_p.loc[df_p['Nome'] == passenger_name, day_column] = driver_name
        st.session_state['passengers'] = df_p
        self.mark_unsaved()

    def unassign_passenger(self, passenger_name, day_column):
        df_p = st.session_state['passengers']
        df_p.loc[df_p['Nome'] == passenger_name, day_column] = ""
        st.session_state['passengers'] = df_p
        self.mark_unsaved()

    def delete_driver(self, driver_name):
        df_d = st.session_state['drivers']
        df_d = df_d[df_d['Nome'] != driver_name]
        st.session_state['drivers'] = df_d

        df_p = st.session_state['passengers']
        days = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        for day in days:
            df_p[day] = df_p[day].replace(driver_name, "")
        st.session_state['passengers'] = df_p
        
        self.mark_unsaved()

    def save_new_driver(self, new_driver_df):
        st.session_state['drivers'] = pd.concat([st.session_state['drivers'], new_driver_df], ignore_index=True)
        self.mark_unsaved()

    def save_new_passenger(self, new_passenger_df):
        st.session_state['passengers'] = pd.concat([st.session_state['passengers'], new_passenger_df], ignore_index=True)
        self.mark_unsaved()

    def get_drivers(self):
        return st.session_state['drivers']

    def get_passengers(self):
        return st.session_state['passengers']