from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from datetime import datetime
import time
import imaplib
import email
from email.header import decode_header
from apikey import openai_key
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup


# Importing necessary modules from your local paths
from database import session, Email

# Set OpenAI API key
os.environ['OPENAI_API_KEY'] = openai_key
username = "shahishnu379@gmail.com"
password = "uczm hshi wwsv potn"

# Function to send email
def send_email(email_content, recipient_email, email_subject):
    msg = MIMEText(email_content, 'html')
    msg['Subject'] = email_subject
    msg['From'] = username
    msg['To'] = recipient_email
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(username, password)
    server.sendmail(username, recipient_email, msg.as_string())
    server.quit()

# Function to check emails
def check_emails():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")

    status, messages = mail.search(None, '(UNSEEN)')
    mail_ids = messages[0].split()

    for mail_id in mail_ids:
        status, msg_data = mail.fetch(mail_id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                email_subject = decode_header(msg["subject"])[0][0]
                if isinstance(email_subject, bytes):
                    email_subject = email_subject.decode()
                email_from = msg.get("From")

                email_body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            email_body = part.get_payload(decode=True).decode()
                            break
                        elif part.get_content_type() == "text/html" and not email_body:
                            email_body = part.get_payload(decode=True).decode()
                else:
                    email_body = msg.get_payload(decode=True).decode()

                check_ai(email_body, email_from, email_subject)

    mail.logout()

# Function to process email content and send formatted table
def check_ai(body, email_from, email_subject):
    current_date = datetime.now().strftime("%B %d, %Y")
    email_content = f""" 
    <!DOCTYPE html> 
    <html> 
    <head> 
    <style> 
    table {{ width: 100%; border-collapse: collapse; }} 
    th, td {{ border: 1px solid black; padding: 8px; text-align: left; }} 
    th {{ background-color: #f2f2f2; }} 
    </style> 
    </head> 
    <body> 
    <table> 
    <tr> 
    <th>Sender Email</th> 
    <th>From Date</th> 
    <th>To Date</th> 
    <th>Current Date</th> 
    </tr> 
    <tr> 
    <td>{email_from}</td> 
    <td><!-- From_date from LLM output --></td> 
    <td><!-- To_date from LLM output --></td> 
    <td>{current_date}</td> 
    </tr> 
    </table> 
    </body> 
    </html> 
    """

    prompt_template = PromptTemplate(
        input_variables=['email_from', 'current_date', 'body','email_content'],
        template="Take note of this date: {current_date} and this email content: {body}. Now, generate an email body that includes only a table with the following columns: Sender ({email_from}),From_date, To_date, and Current_date. If necessary, calculate the From_date and To_date based on the information provided in the email.Generate the output in the form of table mentioned in {email_content}. Format all dates in {current_date}."
    )
    llm = ChatOpenAI(temperature=0.6)
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.run({
        "email_from": email_from,
        "current_date": current_date,
        "body": body,
        "email_content": email_content
    })
    
    # Parse HTML content to extract dates
    soup = BeautifulSoup(response, 'html.parser')
    from_date = soup.find_all('td')[1].text.strip()
    to_date = soup.find_all('td')[2].text.strip()

    # Send the email with formatted HTML content
    recipient_email = "smverappan@gmail.com"
    send_email(response, recipient_email, email_subject)

    # Store email in database
    email_record = Email(
        email_from=email_from,
        email_subject=email_subject,
        from_date=from_date,
        to_date=to_date
    )
    session.add(email_record)
    session.commit()
    print("Email stored in database")


# Run the email checker periodically
while True:
    check_emails()
    time.sleep(5)