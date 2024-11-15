import azure.functions as func
import base64
import io
import json
import pdfplumber
import ics
from datetime import datetime
import re

def extract_events_from_pdf(pdf_file):
    events = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')

            for line in lines:
                match = re.search(r'([A-Za-z]+\.\s+[A-Za-z]+\.\s+\d+)\s+(.*?)(\d{1,2}:\d{2}\s*[AP]M)\s*(Home|Away)', line)

                if match:
                    date_str, description, time_str, location = match.groups()
                    try:
                        current_year = datetime.now().year
                        date_str = f"{date_str} {current_year}"
                        event_datetime = datetime.strptime(f"{date_str} {time_str}", "%a. %b. %d %Y %I:%M %p")

                        events.append({
                            'title': f"Basketball: {description.strip()} ({location})",
                            'datetime': event_datetime,
                            'location': location
                        })
                    except ValueError as e:
                        print(f"Error parsing date: {e}")
                        continue

    return events

def create_ics_file(events):
    calendar = ics.Calendar()
    for event in events:
        cal_event = ics.Event()
        cal_event.name = event['title']
        cal_event.begin = event['datetime']
        cal_event.duration = {'hours': 2}
        cal_event.location = event['location']
        calendar.events.add(cal_event)
    return calendar

async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        pdf_content = req_body.get('pdf_content')

        if not pdf_content:
            return func.HttpResponse(
                "Please provide PDF content",
                status_code=400
            )

        # Convert base64 to PDF file
        pdf_bytes = base64.b64decode(pdf_content)
        pdf_file = io.BytesIO(pdf_bytes)

        # Process the PDF
        events = extract_events_from_pdf(pdf_file)

        if not events:
            return func.HttpResponse(
                "No events found in PDF",
                status_code=400
            )

        calendar = create_ics_file(events)

        # Return the ICS file
        return func.HttpResponse(
            str(calendar),
            mimetype="text/calendar",
            headers={
                "Content-Disposition": "attachment; filename=basketball_schedule.ics"
            }
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error processing request: {str(e)}",
            status_code=500
        )