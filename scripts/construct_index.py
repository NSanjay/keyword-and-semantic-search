import re
import json
from pathlib import *
import argparse
import jsonlines

separator = "[SEP]"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="../dump/")
    parser.add_argument("--out_dir", type=str, default="../para_json_files/")
    parser.add_argument("--file", type=str, default="wiki_00")
    parser.add_argument("--out_file", type=str, default="index_file.jsonl")

    args = parser.parse_args()

    max_paras = 0
    for a_path in Path(args.data_dir).rglob(pattern="**/*"):
        if a_path.is_file():
            with jsonlines.open(a_path) as in_file, \
                    jsonlines.open(Path(args.out_dir, str(a_path.parent.name) + a_path.name + ".jsonl"), "w") as out_file:
                for line in in_file:

                    url = line["url"]
                    the_id = line["id"]
                    the_text = line["text"].strip()
                    title = line["title"].strip()

                    paragraphs = re.split(r'[\n]{2,}', the_text)

                    max_paras = max(max_paras, len(paragraphs))

                    no_of_paragraphs = 0
                    for i, paragraph in enumerate(paragraphs):
                        if not paragraph.strip() or len(paragraph) < 100:
                            continue

                        # if no_of_paragraphs == 500:
                        #     break

                        no_of_paragraphs += 1
                        out = {}
                        out["id"] = str(the_id) + separator + title + separator + str(i) + separator + url
                        out["contents"] = title + separator + paragraph
                        out_file.write(out)

    print("max_paras", max_paras)


if __name__ == "__main__":
    main()

