from database.utils.enums import Source


class ImplicationEntity:
    source: Source
    source_id: str

    origin_name: str
    implies: [str]
