import streamlit as st
import json
import os
import plotly.graph_objects as go
import pandas as pd

DATA_FILE = "kpi_data.json"

# Daten laden oder initialisieren
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        kpi_data = json.load(f)
else:
    kpi_data = {"monatsziele": {}, "wochenwerte": {}}

# Funktion zum Speichern der Daten
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(kpi_data, f, indent=4)

def create_gauge(title, value, max_value):
    # ... (bleibt unverändert)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        gauge = {
            'axis': {'range': [None, max_value]},
            'bar': {'color': "#0000FF"}, #Standardfarbe
            'steps' : [
                {'range': [0, max_value*0.33], 'color': "red"},
                {'range': [max_value*0.33, max_value*0.66], 'color': "yellow"},
                {'range': [max_value*0.66, max_value], 'color': "green"}],
            'threshold' : {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': value}}))
    return fig

st.set_page_config(page_title="KPI Dashboard", page_icon=":chart_with_upwards_trend:", layout="wide")
st.title("Gabi's Antikmöbel-Erfolge")

# CSS für minimalistisches Design (bleibt unverändert)
st.markdown("""<style>...</style>""", unsafe_allow_html=True)

# Monatsziele
st.subheader("Monatsziele")
monatsziele_keys = list(kpi_data.get("monatsziele", ["Anzahl Einkäufe", "Ausgabenbudget", "Anzahl Verkäufe", "Umsatz", "Gewinn"]))

# Calculate the number of columns, defaulting to 10 if necessary
number_of_monatsziele_columns = max(len(monatsziele_keys), 10) #Default ist nun 10

try:
    number_of_monatsziele_columns = int(number_of_monatsziele_columns)
except ValueError:
    st.error("Ungültige Anzahl von Spalten berechnet. Verwende Standardwert (10).")
    number_of_monatsziele_columns = 10

monatsziele_columns = st.columns(number_of_monatsziele_columns)

for kpi_index, kpi_name in enumerate(monatsziele_keys):
    # Important: Check if the index is within the valid range of columns
    if kpi_index < number_of_monatsziele_columns: #Überprüfung hinzugefügt
        if kpi_name not in kpi_data["monatsziele"]:
            kpi_data["monatsziele"][kpi_name] = 0
        kpi_data["monatsziele"][kpi_name] = monatsziele_columns[kpi_index].number_input(
            f"Monatsziel für {kpi_name}",
            value=kpi_data["monatsziele"][kpi_name],
            key=f"monatsziel_{kpi_name}",
        )
save_data()

# Wochenwerte und -übersicht
st.subheader("Wochenwerte & Wochenübersicht")
aktuelle_woche = st.number_input("Aktuelle Woche", min_value=1, step=1)

monatsziele_keys = list(kpi_data["monatsziele"].keys())
number_of_wochenwerte_columns = max(len(monatsziele_keys), 10)

try:
    number_of_wochenwerte_columns = int(number_of_wochenwerte_columns)
except ValueError:
    st.error("Ungültige Anzahl von Spalten berechnet. Verwende Standardwert (10).")
    number_of_wochenwerte_columns = 10

wochenwerte_columns = st.columns(number_of_wochenwerte_columns)

if str(aktuelle_woche) not in kpi_data["wochenwerte"]:
    kpi_data["wochenwerte"][str(aktuelle_woche)] = {}

for kpi_index, kpi_name in enumerate(monatsziele_keys):
    if kpi_index < number_of_wochenwerte_columns: #Überprüfung hinzugefügt
        if kpi_name not in kpi_data["wochenwerte"][str(aktuelle_woche)]:
            kpi_data["wochenwerte"][str(aktuelle_woche)][kpi_name] = 0
        kpi_data["wochenwerte"][str(aktuelle_woche)][kpi_name] = wochenwerte_columns[kpi_index].number_input(
            f"Wert für {kpi_name}",
            value=kpi_data["wochenwerte"][str(aktuelle_woche)][kpi_name],
            key=f"wochenwert_{kpi_name}",
        )
save_data()

if str(aktuelle_woche) in kpi_data["wochenwerte"]:
    for kpi_index, kpi_name in enumerate(monatsziele_keys):
        if kpi_index < number_of_wochenwerte_columns: #Überprüfung hinzugefügt
            if kpi_data["monatsziele"][kpi_name] != 0:
                prozentsatz = (kpi_data["wochenwerte"][str(aktuelle_woche)][kpi_name] / kpi_data["monatsziele"][kpi_name]) * 100
                color = "Grün" if prozentsatz > 66 else "Gelb" if prozentsatz > 33 else "Rot"
                wochenwerte_columns[kpi_index].plotly_chart(create_gauge(kpi_name, prozentsatz, 100))
                # Motivierende Texte
                if prozentsatz < 33:
                    wochenwerte_columns[kpi_index].write(f"Gabi, du schaffst das! ")
                elif prozentsatz < 66:
                    wochenwerte_columns[kpi_index].write(f"Halbzeit! Weiter so, Gabi! ")
                else:
                    wochenwerte_columns[kpi_index].write(f"Super Arbeit, Gabi! Du rockst das! ")
            else:
                wochenwerte_columns[kpi_index].write(f"{kpi_name}: Monatsziel ist 0, daher keine Prozentanzeige")

# Verlaufsanzeige
st.subheader("Verlauf")
try:
    wochen_df = pd.DataFrame.from_dict(kpi_data["wochenwerte"], orient='index').T
    st.line_chart(wochen_df)
except:
    st.write("Noch keine Daten für den Verlauf vorhanden")
