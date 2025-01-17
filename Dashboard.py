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
    kpi_data = {"monatsziele": {"Umsatz": 500, "Gewinn": 500}, "wochenwerte": {}}

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
            'bar': {'color': "lightgray"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, value], 'color': "blue"}
            ],
            'threshold' : {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value}}))
    fig.update_layout(width=300, height=250, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "darkblue", 'family': "Arial"})
    return fig
# Wochenwerte und -übersicht
st.subheader("Wochenwerte & Wochenübersicht")
aktuelle_woche = st.number_input("Aktuelle Woche", min_value=1, step=1)
# Hintergrundbild
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.app.goo.gl/PM1A1CVUzydHsGRa7");   # Pfad zum Bild im gleichen Ordner
        background-size: cover;  # Oder 'contain', je nachdem, wie du das Bild anzeigen möchtest
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Titel mit Styling
st.markdown("<h1 style='text-align: center; color: #007bff; font-family: Cursive;'>Gabi's Antikmöbel-Erfolge</h1>", unsafe_allow_html=True)

# Bild mit Styling
image = Image.open("th.jpg")
st.image(image, use_container_width=False, width=400)

# Standard KPIs
default_monatsziele = ["Anzahl Einkäufe", "Ausgabenbudget", "Anzahl Verkäufe", "Umsatz", "Gewinn"]
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
        f"Wert für {kpi_name} (Woche {aktuelle_woche})",
        value=kpi_data["wochenwerte"][str(aktuelle_woche)][kpi_name],
        key=f"wochenwert_{kpi_name}_{aktuelle_woche}",
        step=100 if kpi_name in ("Umsatz", "Gewinn") else 1
    )
save_data()

# Wochenübersicht (Tachos)
if str(aktuelle_woche) in kpi_data["wochenwerte"]:
    for kpi_index, kpi_name in enumerate(monatsziele_keys):
        with wochenwerte_columns[kpi_index]:
            if kpi_data["monatsziele"].get(kpi_name, 0) != 0:
                prozentsatz = (kpi_data["wochenwerte"][str(aktuelle_woche)][kpi_name] / kpi_data["monatsziele"][kpi_name]) * 100
                st.plotly_chart(create_gauge(kpi_name, prozentsatz, 100), use_container_width=True)

                # Wochenziel berechnen
                wochenziel = kpi_data["monatsziele"][kpi_name] / 4  # Annahme: 4 Wochen pro Monat

                # Motivierende Texte mit dynamischem Wochenziel
                motivation_stufen = [
                    (0, "Gabi, du schaffst das! 💪"),
                    (25, "Gib Gas, Gabi! 🏎️ Das Ziel ist in Sicht!"),
                    (wochenziel / kpi_data["monatsziele"][kpi_name] * 100, f"Halbzeit! Weiter so, Gabi! 👍 (Wochenziel: {wochenziel:.0f})"),  # Dynamisches Wochenziel
                    (75, "Du bist auf dem besten Weg, Gabi! 💪 {prozentsatz}% erreicht!"),
                    (100, "Super Arbeit, Gabi! Du rockst das! 🎉")
                ]

                for stufe, text in motivation_stufen:
                    if prozentsatz <= stufe:
                        st.write(text.format(prozentsatz=prozentsatz))
                        break

            else:
                st.write(f"{kpi_name}: Monatsziel ist 0, daher keine Prozentanzeige")

# Verlaufsanzeige mit separaten Graphen für jedes KPI
st.subheader("Verlauf")

if not kpi_data["wochenwerte"]:
    st.write("Noch keine Daten für den Verlauf vorhanden.")
else:
    try:
        wochen_df = pd.DataFrame.from_dict(kpi_data["wochenwerte"], orient='index')
        wochen_df = wochen_df.sort_index(axis=1)

        if wochen_df.empty:
            st.write("Noch keine Daten für den Verlauf vorhanden.")
        else:
            for kpi_name in wochen_df.columns:
                st.write(f"**{kpi_name}**")  # KPI-Name als Überschrift
                st.line_chart(wochen_df[kpi_name])  # Separater Graph für jedes KPI
    except Exception as e:
        st.write("Fehler beim Erstellen des Verlaufsdiagramms.")
        st.write(f"Details: {e}")
