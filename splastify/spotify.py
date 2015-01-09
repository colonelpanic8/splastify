from __future__ import absolute_import

import time

import threading

import spotify

class SpotifyClient(object):

    @classmethod
    def login(cls, username, password):
        logged_in_event = threading.Event()
        def connection_state_listener(session):
             if session.connection.state is spotify.ConnectionState.LOGGED_IN:
                  logged_in_event.set()
        config = spotify.Config()
        config.load_application_key_file("spotify_appkey.key")

        session = spotify.Session(config)
        session.on(
            spotify.SessionEvent.CONNECTION_STATE_UPDATED,
            connection_state_listener
        )
        session.login(username, password)
        while not logged_in_event.wait(0.1):
            session.process_events()
        return cls(session)

    def __init__(self, session):
        self._session = session

    def make_playlist(self, name):
        return self._session.playlist_container.add_new_playlist(name)

    def get_playlist_by_name(self, name):
        for playlist in self._session.playlist_container:
            if playlist.name == name:
                return playlist

    def upsert_playlist_by_name(self, name):
        return self.get_playlist_by_name(name) or self.make_playlist(name)

    def add_tracks_to_playlist_by_name(self, name, tracks):
        playlist = self.upsert_playlist_by_name(name)
        playlist.load()
        tracks_to_add = set(tracks)
        for track in playlist.tracks:
            if track in tracks_to_add:
                tracks_to_add.remove(track)
        playlist.add_tracks(tracks_to_add)
        playlist.load()
        return playlist

    def add_track_links_to_playlist_by_name(self, name, tracks):
        return self.add_tracks_to_playlist_by_name(
            name, map(self._session.get_track, tracks)
        )

    def remove_duplicates(self, playlist):
        playlist.load()
        tracks_seen = set()
        indices_to_remove = set()
        for index, track in enumerate(playlist.tracks):
            if track in tracks_seen:
                indices_to_remove.add(index)
            else:
                tracks_seen.add(track)
        playlist.remove_tracks(indices_to_remove)
        playlist.load()
        while playlist.has_pending_changes:
            time.sleep(.01)
        return playlist

    def remove_missing(self, playlist, tracks):
        indices_to_remove = []
        for index, track in enumerate(playlist.tracks):
            if track not in tracks:
                indices_to_remove.append(index)
        playlist.remove_tracks(indices_to_remove)
        while playlist.has_pending_changes:
            time.sleep(.01)
        return playlist

    def clear(self, playlist):
        playlist.load()
        playlist.remove_tracks(range(playlist.tracks))
        while playlist.has_pending_changes:
            time.sleep(.01)
        return playlist

    def sync_with_tracks(self, name, tracks):
        playlist = self.add_tracks_to_playlist_by_name(name, set(tracks))
        self.remove_missing(playlist, tracks)
        return playlist

    def sync_with_tracks_by_links(self, name, track_links):
        return self.sync_with_tracks(
            name, map(self._session.get_track, track_links)
        )
