import streamlit as st
import json
import os
import plotly.graph_objects as go
import pandas as pd

DATA_FILE = "kpi_data.json"

# Daten laden oder initialisieren
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {"monatsziele": {}, "wochenwerte": {}}

# Funktion zum Speichern der Daten
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

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
st.markdown(
    """
    <style>
    body {
        background-color: #f5f5f5;
        font-family: sans-serif;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    .st-bu {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 5px;
        margin-bottom: 10px;
    }
    .stProgress > div > div {
        background-color: var(--color);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Monatsziele
st.subheader("Monatsziele")
monatsziele_keys = list(data.get("monatsziele", ["Anzahl Einkäufe", "Ausgabenbudget", "Anzahl Verkäufe", "Umsatz", "Gewinn"]))

# Ensure a valid number of columns (at least 1)
num_cols_monatsziele = max(len(monatsziele_keys), 1)  # Use max to guarantee at least 1 column

cols_monatsziele = st.columns(num_cols_monatsziele)

for i, kpi in enumerate(monatsziele_keys):
    if kpi not in data["monatsziele"]:
        data["monatsziele"][kpi] = 0
    data["monatsziele"][kpi] = cols_monatsziele[i].number_input(f"Monatsziel für {kpi}", value=data["monatsziele"][kpi], key=f"monatsziel_{kpi}")
save_data()


# Wochenwerte und -übersicht
st.subheader("Wochenwerte & Wochenübersicht")
aktuelle_woche = st.number_input("Aktuelle Woche", min_value=1, step=1)

monatsziele_keys = list(data["monatsziele"].keys()) #Die Keys aus den Monatszielen verwenden
num_cols = len(monatsziele_keys)
cols = st.columns(num_cols)

if str(aktuelle_woche) not in data["wochenwerte"]:
    data["wochenwerte"][str(aktuelle_woche)] = {}

for i, kpi in enumerate(monatsziele_keys):
    if kpi not in data["wochenwerte"][str(aktuelle_woche)]:
        data["wochenwerte"][str(aktuelle_woche)][kpi] = 0
    data["wochenwerte"][str(aktuelle_woche)][kpi] = cols[i].number_input(f"Wert für {kpi}", value=data["wochenwerte"][str(aktuelle_woche)][kpi], key=f"wochenwert_{kpi}")
save_data()

if str(aktuelle_woche) in data["wochenwerte"]:
    for i, kpi in enumerate(monatsziele_keys):
        if data["monatsziele"][kpi] != 0:
            prozentsatz = (data["wochenwerte"][str(aktuelle_woche)][kpi] / data["monatsziele"][kpi]) * 100
            color = "Grün" if prozentsatz > 66 else "Gelb" if prozentsatz > 33 else "Rot"
            cols[i].plotly_chart(create_gauge(kpi, prozentsatz, 100))
            # Motivierende Texte
            if prozentsatz < 33:
                cols[i].write(f"Gabi, du schaffst das! ")
            elif prozentsatz < 66:
                cols[i].write(f"Halbzeit! Weiter so, Gabi! ")
            else:
                cols[i].write(f"Super Arbeit, Gabi! Du rockst das! ")
        else:
            cols[i].write(f"{kpi}: Monatsziel ist 0, daher keine Prozentanzeige")

# Verlaufsanzeige
st.subheader("Verlauf")
try:
    wochen_df = pd.DataFrame.from_dict(data["wochenwerte"], orient='index').T
    st.line_chart(wochen_df)
except:
    st.write("Noch keine Daten für den Verlauf vorhanden")
