from src.anki_generator import AnkiGenerator


def main():
    # print("Hello from anki-generator!")

    anki_generator = AnkiGenerator(excel_path="leren_het_nederlands_met_bavo.xls")
    anki_generator.generate_anki()


if __name__ == "__main__":
    main()
