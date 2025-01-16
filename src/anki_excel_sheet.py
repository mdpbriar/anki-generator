import os
import random

import genanki
import gtts
import pyexcel
import tempfile

from genanki import Note
from pandas.core.util.hashing import hash_tuples

tmp_folder = tempfile.gettempdir()

def is_castable_to_int(input_string):
    try:
        # Attempt to convert the string to an integer
        int(input_string)
        return True
    except ValueError:
        # If a ValueError is raised, the string is not castable to an integer
        return False


def check_is_valid_language_code(language_code: str):
    gtts_languages = gtts.lang.tts_langs()
    available_languages_codes = gtts_languages.keys()
    return language_code is not None and language_code != "" and language_code in available_languages_codes


class AnkiExcelSheet:

    sheet_name: str
    excel_path: str
    question: str
    reversed: bool = False
    reversed_question: str = None
    anki_package: genanki.Package
    start_sort: int
    language_A: str|None
    language_B: str|None

    def __init__(self, sheet_name: str, excel_path: str, anki_package: genanki.Package, text_to_speech:bool=False):
        self.sheet_name = sheet_name
        self.excel_path = excel_path
        self.anki_package = anki_package

        sheet = pyexcel.get_sheet(file_name=excel_path, sheet_name=sheet_name)
        self.question = sheet[0, 1]
        start_sort = sheet[1, 1]
        self.reversed = bool(sheet[2, 1])
        self.reversed_question = sheet[3, 1]
        self.start_sort = 0 if not start_sort or not is_castable_to_int(start_sort) else int(start_sort)
        language_A = sheet[5, 0]
        language_B = sheet[5, 1]

        self.language_A = language_A if text_to_speech and check_is_valid_language_code(language_A) else None
        self.language_B = language_B if text_to_speech and check_is_valid_language_code(language_B) else None


    def generate_notes(self) -> list[tuple[Note, int]]:
        records = pyexcel.get_array(file_name=self.excel_path, sheet_name=self.sheet_name, start_row=6)
        my_model = self._generate_model()
        my_reversed_model = self._generate_model(reverse=True) if self.reversed else None

        notes = []

        for index, record in enumerate(records):
            if record[0] == '' or record[1] == '':
                continue

            # we can set the difficulty of a record by putting a number next to it
            record_difficulty = record[2] if len(record) > 2 and is_castable_to_int(record[2]) else self.start_sort + index

            media_col_a = self._add_speech_to_package(record[0], self.language_A) if self.language_A is not None else None
                # note_fields.append(media_field)
            media_col_b = self._add_speech_to_package(record[1], self.language_B) if self.language_B is not None else None
                # note_fields.append(media_field)

            note_fields = [str(record[0]), str(record[1])]
            if media_col_a is not None:
                note_fields.append(media_col_a)
            if media_col_b is not None:
                note_fields.append(media_col_b)

            notes.append(self._generate_note(fields=note_fields, index=record_difficulty, model=my_model))

            if my_reversed_model is not None:
                # Si on a un model reversed, alors on inverse question et réponse
                reversed_note_fields = [str(record[1]), str(record[0])]
                if media_col_b is not None:
                    reversed_note_fields.append(media_col_b)
                if media_col_a is not None:
                    reversed_note_fields.append(media_col_a)
                notes.append(self._generate_note(fields=reversed_note_fields, index=index+self.start_sort, model=my_reversed_model))

        return notes


    def _generate_model(self, reverse:bool = False) -> genanki.Model:
        seeder = self.sheet_name
        if reverse:
            seeder += "reversed"
        random.seed(seeder)
        model_id = random.randrange(1 << 30, 1 << 31)

        question = self.question if not reverse else self.reversed_question

        model_fields = [
            {'name': 'Question'},
            {'name': 'Answer'},
        ]
        qfmt = question + " :<br/>{{Question}}"
        afmt = '{{FrontSide}}<hr id="answer">{{Answer}}'

        # if a language is defined for the questions column, we add a media for the question
        if (not reverse and self.language_A is not None) or (reverse and self.language_B is not None):
            model_fields.append({'name': 'MediaQuestion'})
            qfmt = qfmt + "<br>{{MediaQuestion}}"

        # if a language is defined for the answers column, we add a media for the answer
        if (not reverse and self.language_B is not None) or (reverse and self.language_A is not None):
            model_fields.append({'name': 'MediaAnswer'})
            afmt = afmt + "<br>{{MediaAnswer}}"

        return genanki.Model(
            model_id,
            'Simple Model',
            fields=model_fields,
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': qfmt,
                    'afmt': afmt,
                },
            ])


    def _add_speech_to_package(self, text: str, language_code: str) -> str:
        # we read the text with gtts
        tts = gtts.gTTS(text=text, lang=language_code)
        # we create the file name from the text
        file_name = '{}.mp3'.format(text)
        file_path = os.path.join(tmp_folder, file_name)
        tts.save(file_path)
        # we add the file to the package
        self.anki_package.media_files.append(file_path)

        return f"[sound:{file_name}]"


    def _generate_note(self, fields: list, index: int, model: genanki.Model) -> tuple[Note, int]:
        return (
            genanki.Note(
                model=model,
                fields=fields,
            ),
            index
        )