import random, json, re

import requests, fitz, pymupdf
from collections.abc import Iterator

reduction_ratio = 1.5


def flags_decomposer(flags: int) -> list:
    res_flags = []
    if flags & 2 ** 0:
        res_flags.append("superscript")
    if flags & 2 ** 1:
        res_flags.append("italic")
    if flags & 2 ** 2:
        res_flags.append("serifed")
    else:
        res_flags.append("sans")
    if flags & 2 ** 3:
        res_flags.append("monospaced")
    else:
        res_flags.append("proportional")
    if flags & 2 ** 4:
        res_flags.append("bold")
    return res_flags


def find_spans(page: fitz.Page) -> Iterator[tuple]:
    for b in page.get_text("dict", flags=11)["blocks"]:
        for l in b["lines"]:
            for s in l["spans"]:
                res_flags = flags_decomposer(s["flags"])
                if re.match(r"\d+\.", s["text"]) and "bold" in res_flags:
                    yield s["bbox"]
                if re.match("Задача", s["text"]):
                    yield s["bbox"]


def process_page(page: pymupdf.Page) -> Iterator[pymupdf.Pixmap]:
    tasks = list(find_spans(page))
    for i in range(len(tasks) - 1):
        top_left = fitz.Point(tasks[i][0] / reduction_ratio, tasks[i][1])
        bottom_right = fitz.Point(page.rect.width - tasks[i][0] / reduction_ratio, tasks[i + 1][1])

        clip = fitz.Rect(top_left, bottom_right)
        pix = page.get_pixmap(matrix=fitz.Matrix(4.0, 4.0), clip=clip)
        yield pix


def get_pictures(url: str) -> list:
    req = requests.get(url)
    pdf = fitz.open(stream=req.content, filetype="pdf")

    pictures = []
    for page in pdf:
        pictures += process_page(page)
    return pictures


def generate() -> None:
    with open("bank.json", "r", encoding="utf-8") as file:
        bank = json.load(file)
    pictures = get_pictures(random.choice(bank))
    random.choice(pictures).save(open(f"task.png", "wb"))
