import azure.functions as func
import tempfile
import pdfplumber
import ics
from datetime import datetime
import re

async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get the file from the request
        file = req.files.get('file')
        if not file:
            return func.HttpResponse(
                "No file uploaded",
                status_code=400
            )

        # Create a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(file.read())
            temp_pdf_path = temp_pdf.name

        # Process the PDF and create events
        events = []
        with pdfplumber.open(temp_pdf_path) as pdf:
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

        # Create ICS calendar
        calendar = ics.Calendar()
        for event in events:
            cal_event = ics.Event()
            cal_event.name = event['title']
            cal_event.begin = event['datetime']
            cal_event.duration = {'hours': 2}
            cal_event.location = event['location']
            calendar.events.add(cal_event)

        # Return the ICS file
        return func.HttpResponse(
            str(calendar),
            mimetype="text/calendar",
            headers={
                "Content-Disposition": "attachment; filename=schedule.ics"
            }
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error processing file: {str(e)}",
            status_code=500
        )