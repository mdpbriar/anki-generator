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
        parts = anki_deck_name.split("-")
        id = parts[-1]
        if is_castable_to_int(id) and int(id) in range(1 << 30, 1 << 31):
        # if 1 << 30 <= id <= 1 << 31:
            deck_id = int(id)
        else:
            deck_id = randrange(1 << 30, 1 << 31)

        print(f"Anki deck name: {anki_deck_name}")

        self.deck = genanki.Deck(deck_id, anki_deck_name)


    def _extract_data_from_sheet(self, sheet_name: str):

        sheet = pyexcel.get_sheet(file_name=self.excel_path, sheet_name=sheet_name)
        question = sheet[0, 1]

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
        records = pyexcel.get_array(file_name=self.excel_path, sheet_name=sheet_name, start_row=3)
        for record in records:
            if record[0] == '' or record[1] == '':
                continue
            my_note = genanki.Note(
                model=my_model,
                fields=[record[0], record[1]])

            self.deck.add_note(my_note)

    def generate_anki(self) -> [str, int]:
        book = pyexcel.get_book(file_name=self.excel_path)
        sheet_names = book.sheet_names()
        for sheet_name in sheet_names:
            self._extract_data_from_sheet(sheet_name)

        file_path = os.path.join(tmp_folder,f"{self.deck.name}.apkg")

        genanki.Package(self.deck).write_to_file(file_path)

        print(f"The deck has been generated with id {self.deck.deck_id}, keep this ID, next time you generate the deck, input the id to update the package")

        return file_path, self.deck.deck_id
