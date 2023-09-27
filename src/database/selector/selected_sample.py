from typing import List, Optional, Dict

from database.entities.post import PostEntity


class SelectedSample(PostEntity):
    def __init__(self, matches: List[str], post: Optional[Dict[str, any]] = None):
        super().__init__(post=post)
        self.matches = matches
