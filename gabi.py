import streamlit as st
import json
import os
import plotly.graph_objects as go
import pandas as pd
from PIL import Image

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
    fig.update_layout(width=300, height=250, margin=dict(l=10, r=10, t=30, b=10)) # Breite und Höhe des Gauge-Diagramms anpassen und margins
    return fig

st.set_page_config(page_title="Dashboard", page_icon=":chart_with_upwards_trend:", layout="wide")
st.title("Gabi's Antikmöbel-Erfolge")

image = Image.open("th.jpg") # Bild öffnen mit PIL - **Ändere "th.jpg" zu deinem Bildpfad**
st.image(image, caption="Antikmöbel", use_container_width=False, width=400) # Bild anzeigen

# Monatsziele
st.subheader("Monatsziele")
default_monatsziele = ["Anzahl Einkäufe", "Ausgabenbudget", "Anzahl Verkäufe", "Umsatz", "Gewinn"]
monatsziele_keys = list(kpi_data.get("monatsziele", default_monatsziele))

# Anzahl der Spalten
number_of_monatsziele_columns = len(monatsziele_keys)

monatsziele_columns = st.columns(number_of_monatsziele_columns)

for kpi_index, kpi_name in enumerate(monatsziele_keys):
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

# Anzahl der Spalten für Wochenwerte
number_of_wochenwerte_columns = len(monatsziele_keys)
wochenwerte_columns = st.columns(number_of_wochenwerte_columns)

if str(aktuelle_woche) not in kpi_data["wochenwerte"]:
    kpi_data["wochenwerte"][str(aktuelle_woche)] = {}

for kpi_index, kpi_name in enumerate(monatsziele_keys):
    if kpi_name not in kpi_data["wochenwerte"][str(aktuelle_woche)]:
        kpi_data["wochenwerte"][str(aktuelle_woche)][kpi_name] = 0
    kpi_data["wochenwerte"][str(aktuelle_woche)][kpi_name] = wochenwerte_columns[kpi_index].number_input(
        f"Wert für {kpi_name} (Woche {aktuelle_woche})",
        value=kpi_data["wochenwerte"][str(aktuelle_woche)][kpi_name],
        key=f"wochenwert_{kpi_name}_{aktuelle_woche}",
    )
save_data()

if str(aktuelle_woche) in kpi_data["wochenwerte"]:
    for kpi_index, kpi_name in enumerate(monatsziele_keys):
        with wochenwerte_columns[kpi_index]:
            if kpi_data["monatsziele"][kpi_name] != 0:
                prozentsatz = (kpi_data["wochenwerte"][str(aktuelle_woche)][kpi_name] / kpi_data["monatsziele"][kpi_name]) * 100
                st.plotly_chart(create_gauge(kpi_name, prozentsatz, 100), use_container_width=True)
                # Motivierende Texte
                if prozentsatz < 33:
                    st.write(f"Gabi, du schaffst das! 💪")
                elif prozentsatz < 66:
                    st.write(f"Halbzeit! Weiter so, Gabi! 👍")
                else:
                    st.write(f"Super Arbeit, Gabi! Du rockst das! 🎉")
            else:
                st.write(f"{kpi_name}: Monatsziel ist 0, daher keine Prozentanzeige")


# Verlaufsanzeige
st.subheader("Verlauf")

# Fehlerbehandlung falls noch keine Daten vorhanden sind
if not kpi_data["wochenwerte"]:
    st.write("Noch keine Daten für den Verlauf vorhanden.")
else:
    try:
        wochen_df = pd.DataFrame.from_dict(kpi_data["wochenwerte"], orient='index')
        # Spalten sortieren, um sie konsistent anzuzeigen
        wochen_df = wochen_df.sort_index(axis=1)
        # Fehlerbehandlung falls DataFrame leer ist
        if wochen_df.empty:
            st.write("Noch keine Daten für den Verlauf vorhanden.")
        else:
            st.line_chart(wochen_df.transpose())
    except Exception as e:
        st.write("Fehler beim Erstellen des Verlaufsdiagramms.")
        st.write(f"Details: {e}")
