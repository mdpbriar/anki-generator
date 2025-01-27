import os
from pathlib import Path

import streamlit as st

from src.anki_generator import AnkiGenerator

tmp_folder = "/tmp"

template_file = "src/template.xls"

def main():
    # print("Hello from anki-generator!")
    intro_text = """
    #### You don't know what Anki cards are ?
    
    Check on this website, you can download the app : https://apps.ankiweb.net/
    
    #### What is this website for ?
    
    Anki cards allow you to learn anything from a deck of cards. You can find decks online for free, but you can also make your own !
    This website will allow you to generate your own cards from an **excel file**.
    
    #### How to do this ?
    
    First create you excel file, always **keep the same file with the same name** when you want to update your deck. If you change the name of the excel file, next time you import the deck, it will be considered as a new one.
    
    You can then add as many sheets as you want. For each main question you want to ask, a sheet has to be created. Be careful to keep the same name for the sheet when you recreate you deck, or else it will be considered as a new model of questions.
    You must write :
    - in B1, the question you will ask, like "translate this", "answer the following question", or "what is the missing word ?"
    - in B2, the difficulty, more you put a high number there, later the questions in this sheet will come. **If you don't know, leave blank.**
    - in B3, you can write 'true' if you want to make a double set of cards and reverse the questions, then you can write in B4 the reverse questions, useful if you want to have to ask for translations both ways for example.
    - your sets of questions/answers must be written starting from **7** !
    - if you want to have sounds files attached, you can add in columns **A6 and B6 the code of the languages** you want to translate the column to. You can leave it blank if you don't want any sound.
    """

    st.set_page_config(page_title="Anki Generator", page_icon=":material/edit:")

    st.title("Anki Generator")

    st.markdown(intro_text)

    st.text("Here is an excel file you can use as template, you can copy the first sheet and add as many as you want :")

    if os.path.exists(template_file):
        with open(template_file, "rb") as f:
            st.download_button("Download Excel Template", f, "template.xls")

    st.write("Once you excel file is ready, you can upload it below :")

    voice_on = st.toggle("Add voice", help="Toggle this on to add google speech to your cards")

    uploaded_file = st.file_uploader("Upload an .xls or a .ods", type=[".xls", ".ods"], help="Upload your excel file here")
    if uploaded_file is not None:
        bytes_data = uploaded_file.read()

        file_path = os.path.join(tmp_folder, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(bytes_data)

        anki_generator = AnkiGenerator(excel_path=file_path, voice_to_speech=voice_on)
        anki_path, deck_id = anki_generator.generate_anki()

        if os.path.exists(anki_path):
            file_name = Path(anki_path).name
            with open(anki_path, "rb") as f:
                st.download_button("Download Anki deck", f, file_name, False)


    st.page_link("https://github.com/mdpbriar/anki-generator/", label="Github repository")


if __name__ == "__main__":
    main()
