import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from login import get_token
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os
import constants
from utils import str_to_date, get_zoned_date, format_date_with_day, get_location_by_id, timezone, get_locations
    
def fetch_single_date(token, origin_id, destination_id, date, quantity):
    data = constants.CONSULT_DATA
    data['token'] = token
    data['origen'] = origin_id
    data['destino'] = destination_id
    data['fechaSalida'] = date
    data['cantidadPasajes'] = quantity
  
    response = requests.post(constants.CONSULT_URL, headers=constants.CONSULT_HEADERS, data=data)

    if response.status_code == 200:
        return {
            "date": date,
            "content": response.text
        }
    else:
        print(f"Failed to fetch availability of date {date}. Status code: {response.status_code}")
        return None
    
def fetch_tickets_data(consult):
    token = get_token()
    date_range = []
    current_date = consult["from_date"]

    while str_to_date(current_date) <= str_to_date(consult['to_date']):
        date_range.append(current_date)
        current_date = (get_zoned_date(current_date) + timedelta(days=1)).strftime("%d-%m-%Y")

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_single_date, [token] * len(date_range), [consult["origin_id"]] * len(date_range), [consult["destination_id"]] * len(date_range), date_range, [consult["quantity"]] * len(date_range)))

    return [result for result in results if result is not None]

def validate_departure_date(soup, date):
    departure_date = date.replace('-', '/')
    dd_list = soup.find_all('dd')
    if not dd_list or len(dd_list) < 3:
        return False
    for i in range(3):
        if departure_date in dd_list[i].get_text():
            return departure_date
    return False

def check_availability(date, html_content):
    result = {
        "service_available": True,
        "date": None
    }
    soup = BeautifulSoup(html_content, 'html.parser')
    departure_date = validate_departure_date(soup, date)
    if not departure_date:
        return result
    labels = soup.find_all("label")
    data = [label for label in labels if 'Sale' in label.get_text() and 'Llega' in label.get_text()]
    if not data:
        return result
    booked = data[0].get_text().split('Sale ')[1].strip()
    total = data[0].get_text().split('Llega ')[1].strip()
    is_available = total > booked
    if not is_available:
        return result
    some_available = False
    travel_hours = []
    for label in data:
        label_text = label.get_text()
        booked = label_text.split('Solicitados: ')[1][:1]
        total = label_text.split('Cupo Total: ')[1][:1]
        if booked == total:
            continue
        if not some_available:
            some_available = True
            result['date'] = format_date_with_day(departure_date)
        departure_hour = label_text.split('Sale ')[1].strip()[:5]
        arrival_hour = label_text.split('Llega ')[1].strip()[:5]
        travel_hours.append(f"{departure_hour} - {arrival_hour}")
    if not some_available:
        return result
    result['date'] = f"{result['date']} [{', '.join(travel_hours)}])"
    return result

def get_range_report(consult):
    tickets_data = fetch_tickets_data(consult)
    range_report = {
        'origin': get_location_by_id(consult['origin_id'])['name'],
        'destination': get_location_by_id(consult['destination_id'])['name'],
        'date_range': f"{consult['from_date']} - {consult['to_date']}",
        'dates': []
    }

    for data in tickets_data:
        result = check_availability(data['date'], data['content'])

        if not result['service_available']:
            print(f"No se encontraron servicios disponibles para {range_report['origin']} - {range_report['destination']} en la fecha {data['date']}")
            continue
        if result['date']:
            range_report['dates'].append(result['date'])

    return range_report

def get_report(consults):
    ticket_report_list = []
    for consult in consults:
        range_report = get_range_report(consult)
        ticket_report_list.append(range_report)
    return ticket_report_list

def get_email_body(ticket_report_list):
    email_body = ""
    for ticket in ticket_report_list:
        email_body += f"Origen: {ticket['origin']}\nDestino: {ticket['destination']}\nRango de fechas: {ticket['date_range']}\nFechas disponibles:\n"
        for date in ticket['dates']:
            email_body += f"\n - {date}\n"
        if not ticket['dates']:
            email_body += ' -- No hay -- \n'
        email_body += '\n------------------------------------------------\n\n'
    return email_body

def send_email(sender_email, sender_password, recipient_email, subject,  email_body):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(email_body, 'plain'))

    # Connect to the SMTP server and send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

    print(f"Email sent successfully: {subject}")

def send_report_to_email(report):
    date_tz = timezone.localize(datetime.now())
    email_subject = f"TICKET REPORT: {date_tz.strftime('%d-%m-%Y %H:%M')}"
    email_body = get_email_body(report)
    send_email(os.getenv('SENDER_EMAIL'), os.getenv('SENDER_PASSWORD'), os.getenv('RECIPIENT_EMAIL'), email_subject, email_body)