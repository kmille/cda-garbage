#!/usr/bin/env python 
import sys
import os
import re
import yaml
from termcolor import cprint
import arrow

from imapclient import IMAPClient
import ssl
import email

from ipdb import set_trace


settings_file = os.environ.get("SETTINGS_FILE", "settings.yaml")
settings = yaml.safe_load(open(settings_file))


def get_body_of_mail(message_data):
    email_message = email.message_from_bytes(message_data[b'RFC822'])
    subject = email_message.get('Subject')
    date = email_message.get('Date')
    if subject != settings['mail']['subject']:
        cprint(f"DEBUG: Skipping mail '{subject}' from {date}", 'magenta')
        return
    body = ""
    print(f"DEBUG: Processing mail '{subject}' from {date}")
    if email_message.is_multipart():
        for part in email_message.get_payload():
            body += part.get_payload()
    else:
        body = email_message.get_payload()
    return body


def get_mails_from_ead():
    ssl_context = ssl.create_default_context(cafile="/etc/ssl/certs/ca-certificates.crt")
    server = IMAPClient(settings['mail']['server'], ssl_context=ssl_context)
    server.login(settings['mail']['user'], settings['mail']['pass'])
    server.select_folder('INBOX')
    # just check the last 5 mails (independent of (un)seen)
    messages = server.search()[:5]
    for __, message_data in server.fetch(messages, 'RFC822').items():
        body = get_body_of_mail(message_data)
        if body:
            yield(body)
    server.logout()


def get_abholtermin(email_body):
    abholtermin = re.search(settings['mail']['regex_abholung'], email_body)
    if not abholtermin:
        cprint("ERROR: Problem with the regex", "red")
        sys.exit(1)
    __, date, description = abholtermin.group(1).strip().split(' ', 2)
    return date, description


def check_notification(date):
    # check if tomorrow is Abholung
    date_abholung = arrow.get(date, "DD.MM.YYYY")
    tomorrow = arrow.now().shift(days=+1)
    if date_abholung.day == tomorrow.day and date_abholung.month == tomorrow.month \
                                         and date_abholung.year == tomorrow.year:
        cprint(f"DEBUG:   Bingo! Will notify others about the news! ({date_abholung.format('DD.MM.YYYY')} vs {tomorrow.format('DD.MM.YYYY')})", 'green')
        return True
    else:
        print(f"DEBUG:   Zonk! Will not notify. ({date_abholung.format('DD.MM.YYYY')} vs {tomorrow.format('DD.MM.YYYY')})")
        return False
        #return True


def read_mails_and_notify(irc_bot):
    # irc_bot is a irc.client.Reactor object
    cprint(f"DEBUG: Let's check our mails at {arrow.now().format()}", 'yellow')
    for mail in get_mails_from_ead():
        date, description = get_abholtermin(mail)
        if check_notification(date):
            msg = settings['msg'].format(description)
            print(f"INFO: Sending irc message {msg}")
            irc_bot.privmsg(settings['irc']['channel'], msg)
    cprint(f"DEBUG: Done. Checked our mails at {arrow.now().format()}", 'yellow')


if __name__ == '__main__':
    read_mails_and_notify()
