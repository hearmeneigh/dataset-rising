from datetime import datetime
from typing import Optional, List, Dict

from database.utils.enums import Source, Rating, Format


class PostEntity:
    def __init__(self, post: Optional[Dict[str, any]] = None):
        if post is not None:
            for key in post:
                setattr(self, key, post[key])

    source: Source
    source_id: str

    rating: Rating
    tags: List[str]

    description: Optional[str]

    origin_urls: List[str]
    origin_md5: Optional[str]
    origin_format: Format
    origin_size: int

    image_url: str
    image_width: int
    image_height: int
    image_ratio: float

    small_url: Optional[str]
    small_width: Optional[int]
    small_height: Optional[int]

    medium_url: Optional[str]
    medium_width: Optional[int]
    medium_height: Optional[int]

    score: Optional[int]
    favorites_count: Optional[int]
    comment_count: Optional[int]
    view_count: Optional[int]

    created_at: Optional[datetime]
    timestamp: datetime

    selector: Optional[str]
