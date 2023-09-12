from enum import Enum


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

