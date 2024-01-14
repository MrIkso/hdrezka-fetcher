# modules
import email
import imaplib
import re
import requests
import smtplib
import sys
import time
import os

def main():
    """Main function"""
    arguments = sys.argv

    # check if exists arguments
    if len(arguments) > 1:
        sender_email = arguments[1]
        # os.environ.get("SENDER_EMAIL")
        sender_password = arguments[2]
        # os.environ.get("SENDER_PASSWORD")
        # receiver_email = os.environ.get("RECEIVER_EMAIL")
        send_email(sender_email, sender_password)
    else:
        print("Arguments not found")
        sys.exit(0)

def get_email_body(received_email):
    text_body = ""
    text_encoding = None
    html_body = ""
    html_encoding = None
    if received_email.is_multipart():
        for payload in received_email.get_payload():
            # If the message comes with a signature it can be that this
            # payload itself has multiple parts, so just return the
            # first one
            if payload.is_multipart():
                text_body, text_encoding, html_body, html_encoding = get_email_body(payload)
            else:
                body = payload.get_payload(decode=True)
                encoding = payload.get_content_charset()
                if payload.get_content_type() == "text/plain":
                    text_body = body
                    text_encoding = encoding
                elif payload.get_content_type() == "text/html":
                    html_body = body
                    html_encoding = encoding
    else:
        text_body = received_email.get_payload(decode=True)
        text_encoding = received_email.get_content_charset()
        html_body = None
    return text_body, text_encoding, html_body, html_encoding
    
def check_and_upgrade_url(url):
    if check_mirror(url):
        save_miror(url)
    else:
        url = "https://" + url.split("://")[1]
        if check_mirror(url):
            print("URL доступен (после добавления https):", url)
            save_miror(url)
            
def check_mirror(url):
    request_response = requests.head(url)
    status_code = request_response.status_code
    website_is_up = status_code == 200
    return website_is_up

def save_miror(url):
    env_file = os.getenv('GITHUB_ENV')
    env_file = open(env_file, "a")
    env_file.write("MIRROR=" + mirror)
    env_file.close()
    
    file = open("mirror.txt", "w")
    file.write(mirror)
    file.close()

def send_email(sender_email, sender_password):
    """Send and read an email"""

    # https://www.systoolsgroup.com/imap/
    gmail_host = "imap.gmail.com"

    pattern = r'<a\s+[^>]*href="([^"]*)"[^>]*>'

    print("Sending mail...")
    sender_mail = smtplib.SMTP("smtp.gmail.com", 587)
    sender_mail.ehlo()
    sender_mail.starttls()

    recipient = "mirror@hdrezka.org"
    sender_mail.login(sender_email, sender_password)

    message = """From:<{0}>
    To:<{1}>""".format(
        sender_email, recipient
    )

    sender_mail.sendmail(sender_email, recipient, message)
    sender_mail.close()

    print("Waiting for reply...")
    time.sleep(30)
    print("Reading mail...")
    # set connection
    mail = imaplib.IMAP4_SSL(gmail_host)

    # login
    mail.login(sender_email, sender_password)

    # select inbox
    mail.select("INBOX")

    # select specific mails
    result, selected_mails = mail.search(None, '(FROM "mirror@hdrezka.org")')

    # total number of mails from specific user
    print("Total Messages from ", recipient, len(selected_mails[0].split()))

    ids = selected_mails[0]  # data is a list.
    id_list = ids.split()  # ids is a space separated string
    latest_email_id = id_list[-1]  # get the latest

    result, data = mail.fetch(latest_email_id, "(RFC822)")
    result, bytes_data = data[0]

    # convert the byte data to message
    email_message = email.message_from_bytes(bytes_data)
    print("\n===========================================")

    # access data
    # print("Subject: ",email_message["subject"])
    # print("To:", email_message["to"])
    print("From: ", email_message["from"])
    print("Date: ", email_message["date"])
    text_body, text_encoding, html_body, html_encoding = get_email_body(email_message)
    normal_html_body = html_body.decode(email_message.get_content_charset() or "utf-8")
    #print("Message: \n", normal_html_body)
    
    match = re.search(pattern, normal_html_body)
    if match:
        mirror = match.group(1).strip()[:-1]
        print("Mirror: ", mirror)
        check_and_upgrade_url(mirror)
    else:
        print("text not match!")
            
    print("==========================================\n")
        
    mail.close()
    mail.logout()

main()
