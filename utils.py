# utils.py

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_random_exponential
import re
import random
import time
from icalendar import Calendar
from datetime import datetime
import os

# Google Calendar integration
import google.auth
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class ExtractionError(Exception):
    pass

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/99.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/99.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/99.0 Safari/537.36"
]

@retry(stop=stop_after_attempt(5), wait=wait_random_exponential(min=2, max=6), reraise=True)
def extract_info_from_url(url):
    """
    Extracts title, description, and price from a Kleinanzeigen URL.
    (You likely need to adapt this for the real structure.)
    """
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    try:
        time.sleep(random.uniform(1, 3))  # Delay
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else "Nicht gefunden"
        description = soup.find('p').text.strip() if soup.find('p') else "Nicht gefunden"
        price_span = soup.find('span', class_='price')
        price = price_span.text.strip() if price_span else "Nicht gefunden"

        return {"title": title, "description": description, "price": price}
    except requests.RequestException as e:
        raise ExtractionError(f"Fehler beim Abrufen der URL: {e}")
    except Exception as e:
        raise ExtractionError(f"Fehler beim Parsen der HTML-Daten: {e}")

def analyze_manual_text(text):
    """
    Analyzes manually pasted text to extract:
    - seller_name
    - title
    - condition
    - location
    - description
    """
    lines = text.splitlines()
    extracted_info = {
        "seller_name": None,
        "title": None,
        "condition": None,
        "location": None,
        "description": None
    }

    for line in lines:
        line = line.strip().lower()
        if "verkäufer" in line and not extracted_info["seller_name"]:
            extracted_info["seller_name"] = line.split(":")[-1].strip().title()
        elif len(line) > 10 and not extracted_info["title"]:
            extracted_info["title"] = line.capitalize()
        elif "zustand" in line and not extracted_info["condition"]:
            extracted_info["condition"] = line.split(":")[-1].strip()
        elif re.match(r"\d{5}\s+\w+", line) and not extracted_info["location"]:
            extracted_info["location"] = line
        elif not extracted_info["description"]:
            extracted_info["description"] = line

    return {
        "seller_name": extracted_info["seller_name"] or "Unbekannter Verkäufer",
        "title": extracted_info["title"] or "Nicht verfügbar",
        "condition": extracted_info["condition"] or "Keine Angaben",
        "location": extracted_info["location"] or "Keine Adresse gefunden",
        "description": extracted_info["description"] or "Keine Beschreibung verfügbar"
    }

##################################################################
# ICS-based calendar read (for demonstration)
##################################################################

CALENDAR_URL = "https://calendar.google.com/calendar/ical/your_calendar_id_here/basic.ics"

def fetch_calendar_events():
    """
    Fetches the ICS calendar file and extracts events (read-only).
    """
    try:
        response = requests.get(CALENDAR_URL)
        response.raise_for_status()
        calendar = Calendar.from_ical(response.text)

        events = []
        for component in calendar.walk():
            if component.name == "VEVENT":
                event_summary = component.get("summary")
                event_start = component.get("dtstart").dt
                event_end = component.get("dtend").dt
                events.append({
                    "summary": str(event_summary),
                    "start": event_start,
                    "end": event_end
                })

        return sorted(events, key=lambda x: x["start"])
    except requests.RequestException as e:
        return [{"summary": "Fehler beim Laden des Kalenders", "start": None, "end": None}]

##################################################################
# Google Calendar read/write (optional)
##################################################################

def get_gcalendar_service():
    """
    Returns an authenticated Google Calendar service object using OAuth2 credentials.
    Requires 'credentials.json' in your working directory.
    """
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8080)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    return service

def add_event_to_google_calendar(summary, start_datetime, end_datetime):
    """
    Adds a new event to the user's Google Calendar (write access).
    """
    try:
        service = get_gcalendar_service()
        event = {
            "summary": summary,
            "start": {"dateTime": start_datetime.isoformat()},
            "end": {"dateTime": end_datetime.isoformat()},
        }
        created_event = service.events().insert(calendarId="primary", body=event).execute()
        return created_event
    except HttpError as error:
        return {"error": f"An error occurred: {error}"}


##################################################################
# Hotel search (Google Places)
##################################################################

def search_hotels_near_location(location):
    """
    Uses Google Places to find hotels near 'location'.
    Make sure to enable the Places API and use your key below.
    """
    api_key = "YOUR_GOOGLE_API_KEY_HERE"
    url = (
        "https://maps.googleapis.com/maps/api/place/textsearch/json"
        f"?query=hotels+in+{location}&key={api_key}"
    )
    try:
        response = requests.get(url)
        data = response.json()
        hotels = []
        if data.get("results"):
            for r in data["results"]:
                name = r.get("name")
                address = r.get("formatted_address")
                rating = r.get("rating", "Keine Bewertung")
                hotels.append({"name": name, "address": address, "rating": rating})

        return hotels
    except Exception as e:
        return [{"error": f"Fehler bei der Hotelsuche: {e}"}]
