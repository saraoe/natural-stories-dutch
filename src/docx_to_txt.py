"""
converting docx files to txt
"""

# from pypandoc.pandoc_download import download_pandoc
# # see the documentation how to customize the installation path
# # but be aware that you then need to include it in the `PATH`
# download_pandoc()

import pypandoc
from glob import glob
import os
import re

if not os.path.exists("texts/"):
    os.makedirs("texts/")

stories_path = "stories/*"

for i, docx_file in enumerate(glob(stories_path)):
    if "docx" not in docx_file:
        os.rename(docx_file, f"{docx_file}.docx")
        docx_file = f"{docx_file}.docx"
    file_name = docx_file[8:-6]
    file_name = re.sub("\s", "_", file_name)
    file_name = re.sub("[^_]\W", "", file_name)
    print(f"{i}: {file_name}")
    output = pypandoc.convert_file(
        docx_file, "plain", outputfile=f"texts/{file_name}.txt"
    )
