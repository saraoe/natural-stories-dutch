gdown --fuzzy https://docs.google.com/spreadsheets/d/1_kV9RKfu1NKk9zzSQT04u9dqv-IuYkCFbzIRyISOvZc/edit#gid=0 -O data/stories_index.xlsx
gdown https://drive.google.com/drive/folders/1_uHPJPGMHjBsRy_tqaYbv2iaI024s3UQ?usp=sharing --folder --remaining-ok -O stories/

python src/docx_to_txt.py
python src/get_descriptives.py