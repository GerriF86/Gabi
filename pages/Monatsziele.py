import streamlit as st
import json
import os

DATA_FILE = "kpi_data.json"

# Daten laden
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        kpi_data = json.load(f)
else:
    kpi_data = {"monatsziele": {"Umsatz": 500, "Gewinn": 500}, "wochenwerte": {}}

# Funktion zum Speichern der Daten
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(kpi_data, f, indent=4)

# Monatsziele
st.subheader("Monatsziele")

# Standard KPIs
default_monatsziele = ["Anzahl Einkäufe", "Ausgabenbudget", "Anzahl Verkäufe", "Umsatz", "Gewinn"]
monatsziele_keys = list(kpi_data.get("monatsziele", default_monatsziele))

# Anzahl der Spalten für Monatsziele
number_of_monatsziele_columns = len(monatsziele_keys)
monatsziele_columns = st.columns(number_of_monatsziele_columns)

for kpi_index, kpi_name in enumerate(monatsziele_keys):
    if kpi_name not in kpi_data["monatsziele"]:
        kpi_data["monatsziele"][kpi_name] = 500 if kpi_name in ("Umsatz", "Gewinn") else 0
    kpi_data["monatsziele"][kpi_name] = monatsziele_columns[kpi_index].number_input(
        f"Monatsziel für {kpi_name}",
        value=kpi_data["monatsziele"][kpi_name],
        key=f"monatsziel_{kpi_name}",
        step=100 if kpi_name in ("Umsatz", "Gewinn") else 1
    )
save_data()
