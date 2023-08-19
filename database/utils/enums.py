from enum import Enum


category_naming_order = {
    'general': 0,
    'symbol': 1,
    'species': 2,
    'artist': 3,
    'meta': 4,
    'character': 5,
    'copyright': 6,
    'lore': 7,
    'rating': 8,
    'score': 9,
    'comments': 10,
    'aspect_ratio': 11,
    'rising': 12,
    'description': 13,
    'views': 14,
    'invalid': 100
}


class Format(str, Enum):
    JPG = 'jpg'
    PNG = 'png'
    GIF = 'gif'
    WEBM = 'webm'
    MP4 = 'mp4'
    SWF = 'swf'


class Source(str, Enum):
    E621 = 'e621',
    GELBOORU = 'gelbooru',
    DANBOORU = 'danbooru'
    RISING = 'rising'


class Rating(str, Enum):
    SAFE = 's'
    QUESTIONABLE = 'q'
    EXPLICIT = 'e'


class Category(str, Enum):
    GENERAL = 'general'
    SPECIES = 'species'
    CHARACTER = 'character'
    ARTIST = 'artist'
    COPYRIGHT = 'copyright'
    META = 'meta'
    LORE = 'lore'
    SYMBOL = 'symbol'
    ASPECT_RATIO = 'aspect_ratio'
    RATING = 'rating'
    SCORE = 'score'
    FAVORITES = 'favorites'
    COMMENTS = 'comments'
    VIEWS = 'views'
    DESCRIPTION = 'description'
    RISING = 'rising'
    INVALID = 'invalid'

