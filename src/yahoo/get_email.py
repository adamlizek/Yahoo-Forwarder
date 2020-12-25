import config
import time
import imaplib
import email
import re
import logging


def read_email_from_gmail(forwarding_email):
    FROM_EMAIL = config.GMAIL_EMAIL
    FROM_PWD = config.GMAIL_PASSWORD
    SMTP_SERVER = "imap.gmail.com"
    SMTP_PORT = 993

    try:
        while True:
            mail = imaplib.IMAP4_SSL(SMTP_SERVER)
            mail.login(FROM_EMAIL, FROM_PWD)
            mail.select('inbox')
            type, data = mail.search(None, 'ALL')
            mail_ids = data[0]

            id_list = mail_ids.split()

            if len(id_list) == 0:
                #print('No unread emails present! Trying again.')
                time.sleep(2)
            else:
                id_list.reverse()
                id_list = id_list[:config.DESIRED_INSTANCES*2]
                break

        for id in id_list:
            typ, data = mail.fetch(str(int(id)), '(RFC822)' )

            #print(id)

            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(response_part[1].decode())
                    email_subject = msg['subject']
                    #print(msg['to'])
                    if msg['to'] == forwarding_email:
                        email_from = msg['from']
                    else:
                        continue
                        # print('Email skipped - ' + email_subject)
                        # continue
                    # print(email_subject)
                    # print('From : ' + email_from + '\n')
                    # print('Subject : ' + email_subject + '\n')

                    if not msg.is_multipart():
                        link_pattern = re.compile('<a[^>]+href=\'(.*?)\'[^>]*>(.*)?</a>')
                        search = link_pattern.search(msg.get_payload())
                        if search is not None:
                            url = search.group(0)
                            # print("Link found! -> " + url)
                            url = url[9:-16]
                            # print(url)
                            return str(url)

                        else:
                            print("No links were found.")
                            return 'not_found'

            return 'not_found'

    except Exception as e:
        logging.info("Error: Check Gmail Credentials, and that Less Secure Apps is enabled!")
        print(str(e))