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


# e621_categories = {
#     0: Category.GENERAL,
#     1: Category.ARTIST,
#     3: Category.COPYRIGHT,
#     4: Category.CHARACTER,
#     5: Category.SPECIES,
#     6: Category.INVALID,
#     7: Category.META,
#     8: Category.LORE
# }


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

numeric_categories = {
    Category.GENERAL: 0,
    Category.ARTIST: 1,
    Category.COPYRIGHT: 3,
    Category.CHARACTER: 4,
    Category.SPECIES: 5,
    Category.INVALID: 6,
    Category.META: 7,
    Category.LORE: 8,
    #
    Category.SYMBOL: 9,
    Category.ASPECT_RATIO: 10,
    Category.RATING: 11,
    Category.SCORE: 12,
    Category.FAVORITES: 13,
    Category.COMMENTS: 14,
    Category.VIEWS: 15,
    Category.DESCRIPTION: 16,
    Category.RISING: 17
}
