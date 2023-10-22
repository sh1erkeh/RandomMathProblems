import random, json, re, time
import requests, fitz

reduction_ratio = 1.5
pattern1 = r"\d+\."
pattern2 = "Задача"

with open("bank.json", "r", encoding="utf-8") as file:
    bank = json.load(file)


def flags_decomposer(flags: int) -> list:
    """Make font flags human readable."""
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


def find_spans(page: fitz.fitz.Page, pattern: str) -> list:
    tasks = []
    blocks = page.get_text("dict", flags=11)["blocks"]
    for b in blocks:
        for l in b["lines"]:
            for s in l["spans"]:
                res_flags = flags_decomposer(s["flags"])
                if re.match(pattern, s["text"]):
                    if pattern == pattern1 and "bold" in res_flags:
                        tasks.append(s["bbox"])
                    elif pattern == pattern2:
                        tasks.append(s["bbox"])
    return tasks


def get_picture(url: str) -> list:
    req = ''
    while req == '':
        try:
            req = requests.get(url)
            break
        except:
            time.sleep(5)
            continue
    pdf = fitz.open(stream=req.content, filetype="pdf")

    clips = []
    mat = fitz.Matrix(4.0, 4.0)

    for page in pdf:
        rect = page.rect
        tasks = find_spans(page, pattern1)
        if len(tasks) == 0:
            tasks = find_spans(page, pattern2)

        for i in range(len(tasks) - 1):
            top_left = fitz.Point(tasks[i][0] / reduction_ratio, tasks[i][1])
            bottom_right = fitz.Point(rect.width - tasks[i][0] / reduction_ratio, tasks[i + 1][1])

            clip = fitz.Rect(top_left, bottom_right)
            pix = page.get_pixmap(matrix=mat, clip=clip)
            clips.append(pix)
    return clips


def generate() -> None:
    sheet_index = random.randint(0, len(bank) - 1)
    clips = get_picture(bank[sheet_index])

    scan_index = random.randint(0, len(clips) - 1)
    clips[scan_index].save(open(f"task.png", "wb"))
