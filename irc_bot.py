import time
import os
import sys
import yaml

import ssl
import irc.client

from threading import Thread


irc_connection = None

settings_file = os.environ.get("SETTINGS_FILE", "settings.yaml")
settings = yaml.safe_load(open(settings_file))['irc']


def on_connect(connection, event):
    global irc_connection
    print("INFO: Connected to irc server")
    if irc.client.is_channel(settings['channel']):
        connection.join(settings['channel'])
        print(f"INFO: Joined channel {settings['channel']}")
    irc_connection = connection


def on_disconnect(connection, event):
    print(f"I don't know why but I disconnected {str(event)}")
    sys.exit(1)


def on_generic_errro(connection, event):
    print("ERROR: {}".format(event))
    sys.exit(1)


def setup_irc():
    try:
        print(f"DEBUG: Connecting to irc server as {settings['nickname']}")
        ssl_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
        reactor = irc.client.Reactor()
        c = reactor.server().connect(settings['server'],
                                     settings['port'],
                                     settings['nickname'],
                                     password=settings['pass'],
                                     connect_factory=ssl_factory)
    except irc.client.ServerConnectionError:
        print("Error connecting to irc server")
        sys.exit(1)
    c.add_global_handler("welcome", on_connect)
    c.add_global_handler("passwdmismatch", on_generic_errro)
    c.add_global_handler("nicknameinuse", on_generic_errro)
    c.add_global_handler("disconnect", on_disconnect)

    reactor.process_forever()


def start_irc_thread():
    print("DEBUG: Starting irc bot in background task")
    t = Thread(target=setup_irc)
    t.start()
    while not irc_connection:
        print("DEBUG: Still not connected to irc. Waiting ...")
        time.sleep(2)
    return t, irc_connection


if __name__ == '__main__':
    start_irc_thread()

