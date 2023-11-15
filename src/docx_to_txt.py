"""
converting docx files to txt
"""

# from pypandoc.pandoc_download import download_pandoc
# # see the documentation how to customize the installation path
# # but be aware that you then need to include it in the `PATH`
# download_pandoc()

import pypandoc
from glob import glob
import os, re
import argparse


def docx_to_txt(docx_path, txt_path):
    if not os.path.exists(txt_path):
        os.makedirs(txt_path)

    for i, docx_file in enumerate(glob(docx_path + "*")):
        # when using gdown on the folder, the files does not always have the .docx
        if "docx" not in docx_file:
            os.rename(docx_file, f"{docx_file}.docx")
            docx_file = f"{docx_file}.docx"

        file_name = docx_file.lower()
        file_name = re.sub("docx", "", file_name)
        path_folder_name = re.sub("[^a-zA-Z]+", "", docx_path)
        file_name = re.sub(path_folder_name, "", file_name)
        file_name = re.sub(r"[\s]", "_", file_name)
        file_name = re.sub(r"[^_\w]", "", file_name)

        # make seperate folder for edited texts
        if "edited" in file_name:
            edited_text_path = os.path.join(txt_path, "edited")
            if not os.path.exists(edited_text_path):
                os.makedirs(edited_text_path)
            file_name = re.sub("edited_", "", file_name)
            file_name = os.path.join("edited", file_name)

        print(f"{i}: {file_name}")
        output = pypandoc.convert_file(
            docx_file, "plain", outputfile=os.path.join(txt_path, f"{file_name}.txt")
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--docx_path", type=str, required=True, help="Filepath for the docx-files."
    )
    parser.add_argument(
        "--txt_path",
        type=str,
        required=True,
        help="Name of the filepath for outputting the txt-files.",
    )
    args = parser.parse_args()

    docx_path = args.docx_path
    txt_path = args.txt_path
    docx_to_txt(docx_path, txt_path)
