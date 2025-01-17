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
    kpi_data = {"monatsziele": {"Umsatz": 500, "Gewinn": 500}, "wochenwerte": {}}  # Standardwerte für Umsatz und Gewinn

# Funktion zum Speichern der Daten
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(kpi_data, f, indent=4)

def create_gauge(title, value, max_value):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 14}},
        delta = {'reference': max_value, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge = {
            'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#007bff"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps' : [
                {'range': [0, max_value*0.33], 'color': "#ff4d4d"},
                {'range': [max_value*0.33, max_value*0.66], 'color': "#ffff66"},
                {'range': [max_value*0.66, max_value], 'color': "#90ee90"}],
            'threshold' : {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value}}))
    fig.update_layout(width=300, height=250, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "darkblue", 'family': "Arial"})
    return fig

# Streamlit Konfiguration
st.set_page_config(page_title="Dashboard", page_icon=":chart_with_upwards_trend:", layout="wide")

# Hintergrundbild
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("https://github.com/GerriF86/Gabi/blob/main/Screenshot.png");  # Ersetze dies durch deinen Link
        background-size: cover;  # Oder 'contain', je nachdem, wie du das Bild anzeigen möchtest
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Titel mit Styling
st.markdown("<h1 style='text-align: center; color: #007bff; font-family: Cursive;'>Gabi's Antikmöbel-Erfolge</h1>", unsafe_allow_html=True)

# Bild mit Styling
image = Image.open("th.jpg")
st.image(image, use_container_width=False, width=40)

# Wochenwerte und -übersicht
st.subheader("Wochenwerte & Wochenübersicht")
aktuelle_woche = st.number_input("Aktuelle Woche", min_value=1, step=1)

# Standard KPIs
default_monatsziele = ["Einkäufe", "Ausgaben", "Verkäufe", "Umsatz", "Gewinn"]
monatsziele_keys = list(kpi_data.get("monatsziele", default_monatsziele))

# Anzahl der Spalten für Wochenwerte
number_of_wochenwerte_columns = len(monatsziele_keys)
wochenwerte_columns = st.columns(number_of_wochenwerte_columns)

if str(aktuelle_woche) not in kpi_data["wochenwerte"]:
    kpi_data["wochenwerte"][str(aktuelle_woche)] = {}

for kpi_index, kpi_name in enumerate(monatsziele_keys):
    if kpi_name not in kpi_data["wochenwerte"][str(aktuelle_woche)]:
        kpi_data["wochenwerte"][str(aktuelle_woche)][kpi_name] = 0
    kpi_data["wochenwerte"][str(aktuelle_woche)][kpi_name] = wochenwerte_columns[kpi_index].number_input(
        f"wochenwert_{kpi_name} (Woche {aktuelle_woche})",
        value=kpi_data["wochenwerte"][str(aktuelle_woche)][kpi_name],
        key=f"wochenwert_{kpi_name}_{aktuelle_woche}",
        step=100 if kpi_name in ("Umsatz", "Gewinn") else 1  # Schrittweite für Umsatz und Gewinn
    )
save_data()

# Wochenübersicht (Tachos)
if str(aktuelle_woche) in kpi_data["wochenwerte"]:
    for kpi_index, kpi_name in enumerate(monatsziele_keys):
        with wochenwerte_columns[kpi_index]:
            if kpi_data["monatsziele"].get(kpi_name, 0) != 0:
                prozentsatz = (kpi_data["wochenwerte"][str(aktuelle_woche)][kpi_name] / kpi_data["monatsziele"][kpi_name]) * 100

                # Tachos mit angepassten Farben
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=prozentsatz,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': kpi_name, 'font': {'size': 14}},
                    delta={'reference': 100, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
                    gauge={
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "lightgray"},  # Fortschrittsbalken in Grau
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, prozentsatz], 'color': "blue"}  # Erreichten Bereich blau färben
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': prozentsatz}}))
                fig.update_layout(width=300, height=250, margin=dict(l=10, r=10, t=30, b=10),
                                  paper_bgcolor="rgba(0,0,0,0)", font={'color': "darkblue", 'family': "Arial"})
                st.plotly_chart(fig, use_container_width=True)

                # Motivierende Texte (sortiert und mit Werten)
                motivation_stufen = [
                    (0, "Gabi, du schaffst das! 💪"),
                    (25, "Gib Gas, Gabi! 🏎️ Das Ziel ist in Sicht!"),
                    (50, "Halbzeit! Weiter so, Gabi! 👍"),
                    (75, "Du bist auf dem besten Weg, Gabi! 💪 {prozentsatz}% erreicht!"),
                    (100, "Super Arbeit, Gabi! Du rockst das! 🎉")
                ]

                for stufe, text in motivation_stufen:
                    if prozentsatz <= stufe:
                        st.write(f"<p style='color: {'darblue' if prozentsatz < 33 else 'grey' if prozentsatz < 66 else 'gold'};'>{text.format(prozentsatz=prozentsatz)}</p>", unsafe_allow_html=True)
                        break

            else:
                st.write(f"{kpi_name}: Monatsziel ist 0, daher keine Prozentanzeige")

# Monatsziele
st.subheader("Monatsziele")

# Anzahl der Spalten für Monatsziele
number_of_monatsziele_columns = len(monatsziele_keys)
monatsziele_columns = st.columns(number_of_monatsziele_columns)

for kpi_index, kpi_name in enumerate(monatsziele_keys):
    if kpi_name not in kpi_data["monatsziele"]:
        kpi_data["monatsziele"][kpi_name] = 500 if kpi_name in ("Umsatz", "Gewinn") else 0  # Standardwert für Umsatz und Gewinn
    kpi_data["monatsziele"][kpi_name] = monatsziele_columns[kpi_index].number_input(
        f"Monatsziel für {kpi_name}",
        value=kpi_data["monatsziele"][kpi_name],
        key=f"monatsziel_{kpi_name}",
        step=100 if kpi_name in ("Umsatz", "Gewinn") else 1  # Schrittweite für Umsatz und Gewinn
    )
save_data()

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
