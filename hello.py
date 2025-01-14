import os
from pathlib import Path

import streamlit as st

from src.anki_generator import AnkiGenerator

tmp_folder = "/tmp"


def main():
    # print("Hello from anki-generator!")
    intro_text = """
    Hello, you can here convert an excel file into an anki cards deck.
    Your excel file must be formated as follows:
    - you can have as many sheets as needed
    - each sheet has a unique name and a question associated with it
    - the question must be written in cell B1
    - a series of question/answers must be written on two columns (A and B), starting row 4
    
    Deck ID:
    You need to keep the same ID for a deck if you want to update it instead of installing it as new.\\
    If your file has an id ("file_name-id.xls"), the deck will be generated with this id.\\
    If you didn't put any id in the file, an id will be generated.\\
    Keep this id and rename your file with adding "-" at the end and the id generated.
    
    Ex: if you upload **"my_super_anki_deck.xls"**, the id **1220592972** might be generated.\\
    Rename then your xls file to **"my_super_anki_deck-1220592972.xls"**, so the next time you upload it, the deck will be generated with the same id
    """

    st.title("Anki Generator")

    st.markdown(intro_text)

    uploaded_file = st.file_uploader("Upload an .xls or a .ods", type=[".xls", ".ods"])
    if uploaded_file is not None:
        bytes_data = uploaded_file.read()

        file_path = os.path.join(tmp_folder, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(bytes_data)

        anki_generator = AnkiGenerator(excel_path=file_path)
        anki_path, deck_id = anki_generator.generate_anki()
        print(anki_path)
        st.write("Your deck has the following ID: {}".format(deck_id))

        if os.path.exists(anki_path):
            file_name = Path(anki_path).name
            with open(anki_path, "rb") as f:
                st.download_button("Download anki file", f, file_name, False)




if __name__ == "__main__":
    main()
