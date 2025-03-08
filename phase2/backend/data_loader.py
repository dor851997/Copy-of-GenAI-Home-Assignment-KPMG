from bs4 import BeautifulSoup
import os

DATA_DIRECTORY = "../phase2_data"  # clearly defined global constant

def load_html_knowledge_base():
    """
    Loads HTML files from the 'phase2_data' folder located at the project's root into a single knowledge base text.
    """
    knowledge_base_text = ""
    data_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), DATA_DIRECTORY))

    for filename in os.listdir(data_directory):
        if filename.endswith(".html"):
            file_path = os.path.join(data_directory, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")
                knowledge_base_text += soup.get_text(separator="\n", strip=True) + "\n\n"

    return knowledge_base_text