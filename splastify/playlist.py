import threading

import spotify


logged_in_event = threading.Event()
def connection_state_listener(session):
     if session.connection.state is spotify.ConnectionState.LOGGED_IN:
         logged_in_event.set()


def login(username, password):
    config = spotify.Config()
    config.load_application_key_file("spotify_appkey.key")

    session = spotify.Session(config)
    session.on(
        spotify.SessionEvent.CONNECTION_STATE_UPDATED,
        connection_state_listener)
    session.login(username, password)
    while not logged_in_event.wait(0.1):
        session.process_events()
    return session

