from functools import reduce
import numbers
import operator

from . import util


class TrackWrapper(object):

    def __init__(self, top_item):
        self.track = top_item.item
        self.weight = top_item.weight

    @util.cached_property
    def track_tags(self):
        return self.track.get_top_tags()

    @util.cached_property
    def artist_tags(self):
        return self.track.artist.get_top_tags()

    @util.cached_property
    def tag_to_count(self):
        return {
            top_item.item.name: top_item.weight
            for top_item in self.track_tags
        }

    @util.cached_property
    def artist_tag_to_count(self):
        return {
            top_item.item.name: float(top_item.weight)
            for top_item in self.track.artist.get_top_tags()
        }


class TrackListBuilder(object):

    def __init__(self, scorer):
        self._scorer = scorer

    def build_track_list(self, tracks, number=None, threshold=1, stop_at_number=False):
        wrapped_tracks = map(TrackWrapper, tracks)
        scored_tracks = []
        for wrapped_track in wrapped_tracks:
            score = self._scorer.score(wrapped_track)
            # print wrapped_track.track
            # print score
            if score >= threshold:
                scored_tracks.append((score, wrapped_track.track))
            if stop_at_number and len(scored_tracks) >= number:
                break
        # sort needs to be descending
        return map(operator.itemgetter(1), sorted(scored_tracks)[:number])


class Scorer(object):

    @staticmethod
    def less_than_weighter(threshold):
        return lambda score: 0 if score >= threshold else 1

    @staticmethod
    def scale_function(scale):
        return lambda x: x * scale

    def __init__(self, weighter=1, **kwargs):
        self.weighter = self.scale_function(weighter) \
                        if isinstance(weighter, numbers.Number) else weighter

    def score(self, wrapped_track):
        return self.weighter(self._score(wrapped_track))



class CombinerScorer(Scorer):

    def __init__(self, *scorers, **kwargs):
        super(CombinerScorer, self).__init__(**kwargs)
        self._scorers = scorers


class ProductScorer(CombinerScorer):

    def _score(self, wrapped_track):
        return reduce(operator.mul, (scorer.score(wrapped_track) for scorer in self._scorers))


class SumScorer(CombinerScorer):

    def _score(self, wrapped_track):
        return sum(scorer.score(wrapped_track) for scorer in self._scorers)


class MaxScorer(CombinerScorer):

    def _score(self, wrapped_track):
        return max(scorer.score(wrapped_track) for scorer in self._scorers)


class TagScorer(Scorer):

    def __init__(self, tag_matcher, tag_attribute='artist_tags', **kwargs):
        super(TagScorer, self).__init__(**kwargs)
        self.artist_to_score_cache = {}
        self._tag_matcher = tag_matcher if callable(tag_matcher) else lambda x: x.item.name == tag_matcher
        self._tag_attribute = tag_attribute


class TagWeightScorer(TagScorer):

    def _score(self, wrapped_track):
        if wrapped_track.track.artist in self.artist_to_score_cache:
            return self.artist_to_score_cache[wrapped_track.track.artist]
        tags = getattr(wrapped_track, self._tag_attribute)
        matching_tag = None
        for tag in tags:
            if self._tag_matcher(tag):
                matching_tag = tag
                break
        score = -1 if matching_tag is None else float(tag.weight)/100
        self.artist_to_score_cache[wrapped_track.track.artist] = score
        return score


class TagRankScorer(TagScorer):

    @staticmethod
    def binary_rank_to_score(rank, maximum_rank):
        return rank < maximum_rank

    @staticmethod
    def default_rank_to_score(rank, maximum_rank):
        return float(maximum_rank - rank)/maximum_rank

    def __init__(self, tag_matcher, maximum_rank=5, rank_to_score=None, **kwargs):
        super(TagRankScorer, self).__init__(tag_matcher, **kwargs)
        if rank_to_score is None:
            rank_to_score = self.default_rank_to_score
        self._rank_to_score = rank_to_score
        self._maximum_rank = maximum_rank

    def _score(self, wrapped_track):
        tags = getattr(wrapped_track, self._tag_attribute)
        matching_tag = None
        for rank, tag in enumerate(tags):
            if self._tag_matcher(tag):
                break
        return self._rank_to_score(rank, self._maximum_rank)
