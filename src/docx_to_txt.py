"""
converting docx files to txt
"""

# from pypandoc.pandoc_download import download_pandoc
# # see the documentation how to customize the installation path
# # but be aware that you then need to include it in the `PATH`
# download_pandoc()

import pypandoc
from glob import glob
import re

path = "../texts/*.docx"

for i, docx_file in enumerate(glob(path)):
    file_name = docx_file[6:-5]
    file_name = re.sub("\s", "_", file_name)
    file_name = re.sub("[^_]\W", "", file_name)
    print(f"{i}: {file_name}")
    output = pypandoc.convert_file(
        docx_file, "plain", outputfile=f"texts/{file_name}.txt"
    )
