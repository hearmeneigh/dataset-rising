from enum import Enum


category_naming_order = {
    'general': 0,
    'symbol': 1,
    'species': 2,
    'artist': 3,
    'meta': 4,
    'copyright': 5,
    'character': 6,
    'lore': 7,
    'rating': 8,
    'score': 9,
    'comments': 10,
    'aspect_ratio': 11,
    'invalid': 100
}


class Category(Enum):
    GENERAL = 'general'
    ARTIST = 'artist'
    COPYRIGHT = 'copyright'
    CHARACTER = 'character'
    SPECIES = 'species'
    INVALID = 'invalid'
    META = 'meta'
    LORE = 'lore'
    SYMBOL = 'symbol'
    RATING = 'rating'
    SCORE = 'score'
    COMMENTS = 'comments'
    ASPECT_RATIO = 'aspect_ratio'


class Format(Enum):
    JPG = 'jpg'
    PNG = 'png'
    GIF = 'gif'
    WEBM = 'webm'
    MP4 = 'mp4'
    SWF = 'swf'


class Source(Enum):
    E621 = 'e621',
    GELBOORU = 'gelbooru',
    DANBOORU = 'danbooru'


class Rating(Enum):
    SAFE = 's'
    QUESTIONABLE = 'q'
    EXPLICIT = 'e'


class Category(Enum):
    GENERAL = 'general'
    SPECIES = 'species'
    CHARACTER = 'character'
    ARTIST = 'artist'
    COPYRIGHT = 'copyright'
    META='meta'
    LORE='lore'
    SYMBOL='symbol'
    ASPECT_RATIO='aspect_ratio'
    RATING='rating'
    SCORE='score'
    FAVORITES='favorites'
    COMMENTS='comments'
    VIEWS='views'
    DESCRIPTION='description'
