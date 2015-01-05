import pylast

# You have to have your own unique two values for API_KEY and API_SECRET
# Obtain yours from http://www.last.fm/api/account for Last.fm

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)


class cached_property(object):
    """Descriptor that caches the result of the first call to resolve its
    contents.
    """

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = self.func(obj)
        setattr(obj, self.func.__name__, value)
        return value

    def bust_self(self, obj):
        """Remove the value that is being stored on `obj` for this
        :class:`.cached_property`
        object.

        :param obj: The instance on which to bust the cache.
        """
        if self.func.__name__ in obj.__dict__:
            delattr(obj, self.func.__name__)

    @classmethod
    def bust_caches(cls, obj, excludes=()):
        """Bust the cache for all :class:`.cached_property` objects on `obj`

        :param obj: The instance on which to bust the caches.
        """
        for name, _ in cls.get_cached_properties(obj):
            if name in obj.__dict__ and not name in excludes:
                delattr(obj, name)

    @classmethod
    def get_cached_properties(cls, obj):
        return inspect.getmembers(type(obj), lambda x: isinstance(x, cls))



class TrackWrapper(object):

    def __init__(self, top_item):
        self.track = top_item.item
        self.play_count = top_item.weight

    @cached_property
    def track_tags(self):
        return self.track.get_top_tags()

    @cached_property
    def tag_to_count(self):
        return {
            top_item.item.name: top_item.weight
            for top_item in self.track_tags
        }

    @property
    def artist_tag_to_count(self):
        if self.track.artist not in artist_to_tag_to_count:
            artist_to_tag_to_count[self.track.artist] = {
            top_item.item.name: top_item.weight
            for top_item in self.track.artist.get_top_tags(limit=8)
        }
        return artist_to_tag_to_count[self.track.artist]


class TagQuantityFilter(object):

    def __init__(self, tag, quantity):
        self.tag = tag
        self.quantity = quantity

    def matches(self, track):
        return self.tag in track.tag_to_count and track.tag_to_count >= self.quantity


class ArtistTagFilter(object):

    def __init__(self, tag):
        self.tag = tag

    def matches(self, track):
        return self.tag in track.artist_tag_to_count


class TopTrackFinder(object):

    def __init__(self, user, track_filter):
        self._user = user
        self._filter = track_filter

    def get_matching_tracks(self, limit=1000):
        tracks = [TrackWrapper(top_item)
                  for top_item in self._user.get_top_tracks(limit=limit)]
        return [wrapper.track for wrapper in tracks
                if self._filter.matches(wrapper)]


import logging

from coloredlogs import ColoredStreamHandler


def enable_logger(log_name, level=logging.DEBUG):
    log = logging.getLogger(log_name)
    handler = ColoredStreamHandler(severity_to_style={'WARNING': dict(color='red')})
    handler.setLevel(level)
    log.setLevel(level)
    log.addHandler(handler)

enable_logger('requests')

finder = TopTrackFinder(network.get_user('IvanMalison'), ArtistTagFilter(u'folk'))
