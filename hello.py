import genanki
import pyexcel

def main():
    # print("Hello from anki-generator!")

    records = pyexcel.get_records(file_name="ankki-preparation.ods")

    my_model = genanki.Model(
        1607392319,
        'Simple Model',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': 'Translate from Nederlands to English :<br/>{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ])

    my_deck = genanki.Deck(
        2059400110,
        'Leren het Nederlands met Bavo')

    for record in records:
        print(record)
        my_note = genanki.Note(
            model=my_model,
            fields=[record['Nederlands'], record['English']])

        my_deck.add_note(my_note)

    genanki.Package(my_deck).write_to_file('output.apkg')

    print("deck is generated")


if __name__ == "__main__":
    main()
