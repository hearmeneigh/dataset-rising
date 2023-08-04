from alive_progress import alive_bar


class Progress:
    def __init__(self, title: str = None, total=None):
        self.title = title
        self.bar = alive_bar(total, title=title, length=40, enrich_print=True, bar='smooth', spinner='dots_waves')

    def update(self, completed: int = None, message: str = None):
        self.bar(completed, message=message)
