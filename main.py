# modules
import email
import imaplib
import re
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


def send_email(sender_email, sender_password):
    """Send and read an email"""

    # https://www.systoolsgroup.com/imap/
    gmail_host = "imap.gmail.com"

    pattern = r"Текущий адрес персонального зеркала:\s+(.+)"

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
    for part in email_message.walk():
        if (
            part.get_content_type() == "text/plain"
            or part.get_content_type() == "text/html"
        ):
            message = part.get_payload(decode=True)
            # print("Message: \n", message.decode())
            match = re.search(pattern, message.decode())
            if match:
                found_text = match.group(1)
                newText = "https://" + found_text
                print("Mirror: ", newText)
                env_file = os.getenv('GITHUB_ENV')

                with open(env_file, "a") as myfile:
                    myfile.write("MIRROR=" + newText)
                #file = open("mirror.txt", "w")
                #file.write(newText.strip())
                #file.close()
            else:
                print("text not match!")

            print("==========================================\n")
            break

    mail.close()
    mail.logout()


main()
