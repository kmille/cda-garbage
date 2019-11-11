import os
import sys
import time
import schedule
import yaml

from imap_ead import read_mails_and_notify
from irc_bot import start_irc_thread 

from ipdb import set_trace

irc_connection = None

settings_file = os.environ.get("SETTINGS_FILE", "settings.yaml")
settings = yaml.safe_load(open(settings_file))


def setup_schedule():
    print("DEBUG: Initialize jobs")
    for time_of_job in settings['daily_jobs']:
        print(f"INFO: Add daily job at {time_of_job}")
        schedule.every().day.at(time_of_job).do(read_mails_and_notify, irc_connection)
    # for debugging
    #schedule.every(10).seconds.do(read_mails_and_notify, irc_connection)

    print("DEBUG: Starting task scheduler")
    try:
        while 1:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("INFO: We are hiring ©kmille-botsolutins GmbH")
        sys.exit(0)


if __name__ == '__main__':
    irc_connection = start_irc_thread()
    setup_schedule()
