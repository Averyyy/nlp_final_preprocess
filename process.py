import os
import requests
from bs4 import BeautifulSoup
import re
import string

def sanitize_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return "".join(c for c in filename if c in valid_chars)


def download_wikiQA():
    url = "https://download.microsoft.com/download/E/5/F/E5FCFCEE-7005-4814-853D-DAA7C66507E0/WikiQACorpus.zip"
    response = requests.get(url)

    with open("WikiQACorpus.zip", "wb") as f:
        f.write(response.content)

    if os.name == 'nt':  # Windows
        os.system("powershell.exe Expand-Archive -LiteralPath WikiQACorpus.zip -DestinationPath resources")
    else:  # Linux
        os.system("unzip WikiQACorpus.zip -d resources")

def process_wikiQA():
    wikiQA_path = os.path.join("resources", "WikiQACorpus", "WikiQA.tsv")

    with open(wikiQA_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    total_lines = len(lines) - 1

    # Create the output directory if it doesn't exist
    if not os.path.exists("processed_data"):
        os.makedirs("processed_data")

    for index, line in enumerate(lines[1:], 1):
        fields = line.split("\t")
        document_id = fields[2].strip()
        document_title = fields[3].strip()
        url = f"https://en.wikipedia.org/wiki/{document_title.replace(' ', '_')}"

        try:
            # Download HTML content
            response = requests.get(url)
            html_content = response.text

            # Extract main content from HTML
            soup = BeautifulSoup(html_content, "html.parser")
            main_content = soup.find("div", {"id": "mw-content-text"})
            text = main_content.get_text()

            # Remove excessive empty lines
            cleaned_text = re.sub(r'\n+', '\n', text).strip()

            # Remove special characters and store the content as a txt file
            txt_path = os.path.join("processed_data", f"{document_id}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(re.sub(r'[^\x00-\x7F]+', ' ', cleaned_text))

            # Print processing status
            print(f"Processing {index}/{total_lines} ({(index / total_lines) * 100:.2f}%)")
        except requests.exceptions.RequestException as e:
            print(f"Error while processing {index}/{total_lines}: {e}")





def main():
    # Check if WikiQACorpus exists in the directory, if not, download it
    wikiQA_folder = os.path.join("resources", "WikiQACorpus")
    if not os.path.exists(wikiQA_folder):
        download_wikiQA()
        print("WikiQACorpus has been downloaded.")
    else:
        print("WikiQACorpus already exists. Skipping download.")

    # Process the dataset
    process_wikiQA()
    print("WikiQACorpus has been processed and saved as .txt files.")

if __name__ == "__main__":
    main()
