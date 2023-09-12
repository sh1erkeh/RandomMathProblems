import requests, fitz
import random, json

reduction_ratio = 1.5
code_word = "Задача"

with open("bank.json", "r", encoding="utf-8") as file:
    bank = json.load(file)


def get_scans(url: str) -> list:
    req = requests.get(url)
    pdf = fitz.open(stream=req.content, filetype="pdf")

    clips = []
    mat = fitz.Matrix(3.0, 3.0)

    for page in pdf:
        rect = page.rect
        words = page.get_text("words")
        
        if words[0][4] != code_word and len(clips) > 0:
            clips.pop()
        
        tasks = list(filter(lambda x: x[4] == code_word, words))
        tasks.append((words[-2][0], min(words[-2][1] + 40, words[-1][1])))

        for i in range(len(tasks) - 1):
            top_left = fitz.Point(tasks[i][0] / reduction_ratio, tasks[i][1])
            bottom_right = fitz.Point(rect.width - tasks[i][0] / reduction_ratio, tasks[i + 1][1])

            clip = fitz.Rect(top_left, bottom_right)
            pix = page.get_pixmap(matrix=mat, clip=clip)
            clips.append(pix)

    return clips


def main() -> None:
    sheet_index = random.randint(0, len(bank) - 1)
    clips = get_scans(bank[sheet_index])

    scan_index = random.randint(0, len(clips) - 1)
    clips[scan_index].save(open(f"task.png", "wb"))


if __name__ == "__main__":
    main()