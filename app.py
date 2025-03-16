# app.py

import streamlit as st
from utils import (
    extract_info_from_url,
    analyze_manual_text,
    fetch_calendar_events,
    add_event_to_google_calendar,
    search_hotels_near_location,
    ExtractionError
)
from negotiation import generate_personal_message
from llm_manager import LLMManager
import pyperclip
import datetime
from config import SETTINGS

# Set up page
st.set_page_config(page_title="Möbelkauf-Assistent", layout="wide", page_icon="🪑")

# Session state initialization
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "ollama"

if "llm_manager" not in st.session_state:
    st.session_state.llm_manager = LLMManager(
        provider=st.session_state.llm_provider,
        ollama_config=SETTINGS,  # e.g. { "model": "llama3.2:3b", ... }
        openai_model="gpt-3.5-turbo"
    )

def main():
    st.title("🪑 Möbelkauf-Assistent")
    st.markdown("Analysieren Sie Anzeigen oder fügen Sie manuell Text ein, um eine Nachricht zu erstellen.")

    # Let user pick which LLM to use
    st.session_state.llm_provider = st.radio(
        "LLM-Provider auswählen:",
        ["ollama", "openai"],
        index=0 if st.session_state.llm_provider == "ollama" else 1
    )

    # Update the manager's provider if changed
    st.session_state.llm_manager.set_provider(st.session_state.llm_provider)

    input_method = st.radio("Input-Methode wählen:", ["URL analysieren", "Text einfügen"])
    extracted_info = {}

    # Step 1: Extract info
    if input_method == "URL analysieren":
        url = st.text_input("Kleinanzeigen-URL:", placeholder="https://www.kleinanzeigen.de/...")
        if st.button("Anzeige analysieren"):
            try:
                with st.spinner("Analysiere die Anzeige..."):
                    extracted_info = extract_info_from_url(url)
                st.success("Anzeige erfolgreich analysiert!")
                st.json(extracted_info)
            except ExtractionError as e:
                st.error(f"Fehler bei der Analyse: {e}")
            except Exception as e:
                st.error(f"Unerwarteter Fehler: {e}")
    else:
        # "Text einfügen"
        manual_text = st.text_area("Fügen Sie den Text hier ein:")
        if st.button("Text analysieren"):
            with st.spinner("Analysiere den Text..."):
                extracted_info = analyze_manual_text(manual_text)
            st.success("Text erfolgreich analysiert!")
            st.json(extracted_info)

    # Step 2: If we have extracted info, show text options
    if extracted_info:
        show_text_options(extracted_info)

def show_text_options(extracted_info):
    st.subheader("Schritt 2: Textbausteine auswählen")
    st.write("Anzeigendetails:")
    st.json(extracted_info)

    selected_options = st.multiselect(
        "Welche Textbausteine möchten Sie verwenden?",
        options=["Erstkontakt", "Preisverhandlung", "Zustandsabfrage", "Terminvereinbarung"],
        default=["Erstkontakt"]
    )

    if "Terminvereinbarung" in selected_options:
        show_calendar_section()

    # Step: Hotel search
    st.subheader("Hotels in der Nähe suchen")
    if st.button("Hotels suchen"):
        location = extracted_info.get("location", "")
        if not location or location == "Keine Adresse gefunden":
            st.error("Keine gültige Ortsangabe gefunden.")
        else:
            with st.spinner("Suche nach Hotels..."):
                hotels = search_hotels_near_location(location)
            if hotels and "error" not in hotels[0]:
                st.write("Gefundene Hotels:")
                for hotel in hotels:
                    st.markdown(
                        f"- **{hotel['name']}**\n"
                        f"  - Adresse: {hotel['address']}\n"
                        f"  - Bewertung: {hotel['rating']}"
                    )
            else:
                st.error(f"Fehler bei der Hotelsuche: {hotels[0].get('error')}")

    # Generate the message
    if st.button("Nachricht generieren"):
        llm = st.session_state.llm_manager
        with st.spinner("Generiere Nachricht..."):
            message = generate_personal_message(llm, extracted_info, selected_options)
        st.text_area("Generierte Nachricht:", value=message, height=300)

        if st.button("Nachricht kopieren"):
            pyperclip.copy(message)
            st.success("Nachricht in die Zwischenablage kopiert!")

def show_calendar_section():
    st.subheader("📅 Kalender-Übersicht")

    events = fetch_calendar_events()
    if events and "Fehler" not in events[0]["summary"]:
        for event in events:
            start_time = event["start"].strftime("%d.%m.%Y %H:%M") if event["start"] else "Unbekannt"
            end_time = event["end"].strftime("%d.%m.%Y %H:%M") if event["end"] else "Unbekannt"
            st.markdown(f"- **{event['summary']}**: {start_time} - {end_time}")
    else:
        st.error("Fehler beim Laden der ICS-basierten Kalenderdaten.")

    st.subheader("Neuen Termin hinzufügen (Google Calendar)")
    summary = st.text_input("Termin-Bezeichnung:")
    date = st.date_input("Datum:")
    start_time = st.time_input("Startzeit:")
    end_time = st.time_input("Endzeit:")
    if st.button("Kalender-Eintrag erstellen"):
        if summary and date and start_time and end_time:
            start_dt = datetime.datetime.combine(date, start_time)
            end_dt = datetime.datetime.combine(date, end_time)
            with st.spinner("Füge Termin hinzu..."):
                created_event = add_event_to_google_calendar(summary, start_dt, end_dt)
            if "error" in created_event:
                st.error(created_event["error"])
            else:
                st.success(f"Kalendereintrag erstellt: {created_event.get('htmlLink', 'Kein Link')}")
        else:
            st.error("Bitte Titel, Datum und Zeiten angeben.")

if __name__ == "__main__":
    main()
