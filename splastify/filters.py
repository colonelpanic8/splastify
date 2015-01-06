from . import util


class TrackWrapper(object):

    def __init__(self, top_item):
        self.track = top_item.item
        self.play_count = top_item.weight

    @util.cached_property
    def track_tags(self):
        return self.track.get_top_tags()

    @util.cached_property
    def tag_to_count(self):
        return {
            top_item.item.name: top_item.weight
            for top_item in self.track_tags
        }

    @util.cached_property
    def artist_tag_to_count(self):
        return {
            top_item.item.name: top_item.weight
            for top_item in self.track.artist.get_top_tags()
        }


class TopTrackFinder(object):

    def __init__(self, user, track_filter):
        self._user = user
        self._filter = track_filter

    def get_matching_tracks(self, limit=1000):
        tracks = [TrackWrapper(top_item)
                  for top_item in self._user.get_top_tracks(limit=limit)]
        return [wrapper.track for wrapper in tracks
                if self._filter.matches(wrapper)]


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
