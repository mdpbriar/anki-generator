import os
from pathlib import Path

import streamlit as st

from src.anki_generator import AnkiGenerator

tmp_folder = "/tmp"

template_file = "src/template.xls"

def main():
    # print("Hello from anki-generator!")
    intro_text = """
    Hello, you can here convert an excel file into an anki cards deck.
    Your excel file must be formated as follows:
    - you can have as many sheets as needed
    - each sheet has a unique name and a question associated with it
    - the question must be written in cell B1
    - a series of question/answers must be written on two columns (A and B), starting row 4
    - You can raise the difficulty of a sheet. Anki will take the first lines in first order by default, it means that the
    first questions asked will be the ones on top of your sheets. If you want to make a sheet more difficult and appear later, 
    you can add a number in cell B2, more the number will be high, later the questions will appear in your deck
    
    Deck ID:
    **You should always keep the same name for your excel file !!**\\
    This name will be used to generate the deck id, if you change the excel name, the id will be changed automatically, 
    and it will be considered as new deck, and not as a new version for the same deck.
    
    This apply too for the sheet names, keep the same sheet names, you can change the questions in B1, but always keep the same sheet names.
    """

    st.set_page_config(page_title="Anki Generator", page_icon=":material/edit:")

    st.title("Anki Generator")

    st.markdown(intro_text)

    if os.path.exists(template_file):
        with open(template_file, "rb") as f:
            st.download_button("Download Excel Template", f, "template.xls")

    st.write("Once you excel file is ready, you can upload it below :")

    uploaded_file = st.file_uploader("Upload an .xls or a .ods", type=[".xls", ".ods"], help="Upload your excel file here")
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
                st.download_button("Download Anki deck", f, file_name, False)


    st.page_link("https://github.com/mdpbriar/anki-generator/", label="Github repository")


if __name__ == "__main__":
    main()
