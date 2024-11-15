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
            # You'll need to customize this parsing logic based on your PDF format
            # This is a simple example assuming each line contains: "Event Title | Date | Time"
            for line in text.split('\n'):
                if '|' in line:
                    title, date, time = line.split('|')
                    # Parse date and time strings to create datetime object
                    datetime_str = f"{date.strip()} {time.strip()}"
                    event_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
                    events.append({
                        'title': title.strip(),
                        'datetime': event_datetime
                    })
    return events

def create_ics_file(events):
    calendar = ics.Calendar()
    for event in events:
        cal_event = ics.Event()
        cal_event.name = event['title']
        cal_event.begin = event['datetime']
        cal_event.duration = {'hours': 1}  # Default duration
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
        calendar = create_ics_file(events)

        # Save the calendar to a temporary file
        with open('temp_calendar.ics', 'w') as f:
            f.write(str(calendar))

        return send_file(
            'temp_calendar.ics',
            as_attachment=True,
            download_name='events.ics',
            mimetype='text/calendar'
        )
    except Exception as e:
        return f'Error processing file: {str(e)}', 500

if __name__ == '__main__':
    app.run(debug=True)