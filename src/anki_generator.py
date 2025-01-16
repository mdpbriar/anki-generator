import os
import random
from pathlib import Path

import genanki
import pyexcel
from random import randrange

tmp_folder = '/tmp'

def is_castable_to_int(input_string):
    try:
        # Attempt to convert the string to an integer
        int(input_string)
        return True
    except ValueError:
        # If a ValueError is raised, the string is not castable to an integer
        return False

class AnkiGenerator:

    excel_path: str
    deck: genanki.Deck

    def __init__(self, excel_path: str) -> None:
        self.excel_path = excel_path

        # get the deck name from file name
        anki_deck_name = Path(excel_path).stem
        random.seed(anki_deck_name)

        deck_id = randrange(1 << 30, 1 << 31)

        print(f"Anki deck name: {anki_deck_name}")

        self.deck = genanki.Deck(deck_id, anki_deck_name)


    def _extract_data_from_sheet(self, sheet_name: str):

        sheet = pyexcel.get_sheet(file_name=self.excel_path, sheet_name=sheet_name)
        question = sheet[0, 1]
        start_sort = sheet[1, 1]
        start_sort = 0 if not start_sort or not is_castable_to_int(start_sort) else int(start_sort)

        random.seed(sheet_name)
        model_id = random.randrange(1 << 30, 1 << 31)

        my_model = genanki.Model(
            model_id,
            'Simple Model',
            fields=[
                {'name': 'Question'},
                {'name': 'Answer'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': question + " :<br/>{{Question}}",
                    'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
                },
            ])
        records = pyexcel.get_array(file_name=self.excel_path, sheet_name=sheet_name, start_row=6)
        notes = []
        for index, record in enumerate(records):
            if record[0] == '' or record[1] == '':
                continue
            notes.append(
                (
                    genanki.Note(
                        model=my_model,
                        fields=[record[0], record[1]],
                    ),
                    index + start_sort
                )
            )

        return notes

    def generate_anki(self) -> [str, int]:
        book = pyexcel.get_book(file_name=self.excel_path)
        sheet_names = book.sheet_names()
        notes = []
        for sheet_name in sheet_names:
            notes.extend(self._extract_data_from_sheet(sheet_name))

        notes = sorted(notes, key=lambda tup: tup[1])

        for note, index in notes:
            self.deck.add_note(note)

        file_path = os.path.join(tmp_folder,f"{self.deck.name}.apkg")

        genanki.Package(self.deck).write_to_file(file_path)

        print(f"The deck has been generated with id {self.deck.deck_id}, keep this ID, next time you generate the deck, input the id to update the package")

        return file_path, self.deck.deck_id
