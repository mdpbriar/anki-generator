import os
import random
import tempfile
from pathlib import Path

import genanki
import pyexcel
from random import randrange, shuffle

from src.anki_excel_sheet import AnkiExcelSheet

tmp_folder = tempfile.gettempdir()

class AnkiGenerator:

    excel_path: str
    deck: genanki.Deck
    voice_to_speech: bool = False

    def __init__(self, excel_path: str, voice_to_speech: bool = False) -> None:
        self.excel_path = excel_path

        # get the deck name from file name
        anki_deck_name = Path(excel_path).stem

        # we generate the deck ID based on the excel file name
        random.seed(anki_deck_name)
        deck_id = randrange(1 << 30, 1 << 31)

        self.deck = genanki.Deck(deck_id, anki_deck_name)
        self.voice_to_speech = voice_to_speech


    def generate_anki(self) -> [str, int]:
        book = pyexcel.get_book(file_name=self.excel_path)
        sheet_names = book.sheet_names()

        # we initiate a packages
        anki_package = genanki.Package(self.deck)

        notes = []
        for sheet_name in sheet_names:
            # for each sheet in the excel file, we initiate a anki sheet and generate the anki notes
            anki_excel_sheet = AnkiExcelSheet(sheet_name, self.excel_path, anki_package, self.voice_to_speech)
            notes.extend(anki_excel_sheet.generate_notes())

        # We mix the notes
        shuffle(notes)
        # we sort the notes to mix the deck
        notes = sorted(notes, key=lambda tup: tup[1])

        # we add each note to the deck
        for note, index in notes:
            self.deck.add_note(note)

        # we write the package to a file
        file_path = os.path.join(tmp_folder,f"{self.deck.name}.apkg")
        anki_package.write_to_file(file_path)

        print(f"The deck has been generated with id {self.deck.deck_id}, keep this ID, next time you generate the deck, input the id to update the package")

        return file_path, self.deck.deck_id
