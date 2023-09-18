import json
from typing import List

from database.entities.tag import AliasEntity
from database.translator.translator import AliasTranslator


class AliasImporter:
    def __init__(self, translator: AliasTranslator):
        self.translator = translator

    def load(self, filename) -> List[AliasEntity]:
        aliases = []

        with open(filename, 'rt') as ap:
            for line in ap:
                aliases.append(self.translator.translate(json.loads(line)))

        return aliases
