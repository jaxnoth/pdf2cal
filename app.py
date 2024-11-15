from flask import Flask, render_template, request, send_file
import pdfplumber
import ics
from datetime import datetime
import re

app = Flask(__name__)

def extract_events_from_pdf(pdf_file):
    events = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            # Split into lines and process each line
            lines = text.split('\n')

            for line in lines:
                # Look for lines that match game schedule pattern
                # Example: "Tue. Jan. 2 Boys JV Basketball vs Centennial 5:30 PM Away"
                match = re.search(r'([A-Za-z]+\.\s+[A-Za-z]+\.\s+\d+)\s+(.*?)(\d{1,2}:\d{2}\s*[AP]M)\s*(Home|Away)', line)

                if match:
                    date_str, description, time_str, location = match.groups()

                    # Parse the date
                    try:
                        # Add current year since it's not in the PDF
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
        cal_event.duration = {'hours': 2}  # Basketball games typically last 2 hours
        cal_event.location = event['location']
        calendar.events.add(cal_event)
    return calendar

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'pdf_file' not in request.files:
        return 'No file uploaded', 400

    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        return 'No file selected', 400

    try:
        events = extract_events_from_pdf(pdf_file)

        if not events:
            return 'No events found in PDF', 400

        calendar = create_ics_file(events)

        # Use a more secure temporary file approach
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ics', delete=False) as temp_file:
            temp_file.write(str(calendar))
            temp_path = temp_file.name

        try:
            return send_file(
                temp_path,
                as_attachment=True,
                download_name='basketball_schedule.ics',
                mimetype='text/calendar'
            )
        finally:
            import os
            os.unlink(temp_path)  # Clean up the temporary file

    except Exception as e:
        return f'Error processing file: {str(e)}', 500

if __name__ == '__main__':
    app.run(debug=True)