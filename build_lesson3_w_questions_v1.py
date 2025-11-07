import argparse
import os
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Cm

# ---------- Цвета и шрифты ----------
BLACK = RGBColor(0, 0, 0)
DARK_RED = RGBColor(139, 0, 0)
DARK_GREEN = RGBColor(0, 100, 0)
PURPLE = RGBColor(102, 0, 153)
THAI_FONT_NAME = "Noto Sans Thai"

OUT_NAME = "cha_lesson_3_w_questions_v1.docx"

BLOCK_TITLES = {
    "🎓 Lesson 3 — W-Questions — Vocabulary: Student Graduation",
    "👩‍🏫 Explanation",
    "✍️ Examples:",
    "🧠 Practice",
    "🎓 Vocabulary (Student Graduation)",
    "🧺 Word bank:",
    "🎓 Vocabulary Exercises",
    "🧾 Exit check & Homework",
    "🧾 Exit check (5 quick items):",
}


def new_doc():
    doc = Document()
    for s in doc.sections:
        s.page_height = Cm(29.7)
        s.page_width = Cm(21.0)
        s.left_margin = Cm(2.0)
        s.right_margin = Cm(2.0)
        s.top_margin = Cm(2.0)
        s.bottom_margin = Cm(2.0)
        fp = s.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run1 = fp.add_run("© Cha 2025 · Page ")
        run1.font.size = Pt(9)
        run1.font.color.rgb = BLACK
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), "PAGE")
        run2 = fp.add_run()
        run2._r.append(fld)
    return doc


def line_ru(doc: Document, txt: str, size=11):
    p = doc.add_paragraph()
    r = p.add_run(f"({txt})")
    r.font.italic = True
    r.font.color.rgb = DARK_RED
    r.font.size = Pt(size)


def line_th(doc: Document, txt: str, size=11):
    p = doc.add_paragraph()
    r = p.add_run(f"({txt})")
    r.font.italic = True
    r.font.color.rgb = DARK_GREEN
    r.font.size = Pt(size)
    r.font.name = THAI_FONT_NAME


def norm_exact(s: str) -> str:
    s = (s or "").strip()
    s = s.replace("\u2011", "-")
    s = s.replace("\u2013", "-")
    s = s.replace("\u2014", "-")
    s = s.replace("\u2212", "-")
    s = re.sub(r"^\s*\d+(?:\.\d+)*[\)\.]?\s+", "", s)
    s = re.sub(r"^[\u2022\-\u2013\u2014]\s+", "", s)
    return re.sub(r"\s+", " ", s)


def load_answers_from_source(path: str) -> dict:
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f]
    i = 0
    ans = {}
    while i < len(lines):
        en = lines[i].strip()
        if not en:
            i += 1
            continue
        if en in BLOCK_TITLES:
            i += 1
            continue
        if i + 2 <= len(lines) - 1 and lines[i + 1].lstrip().startswith(
                "Answer:") and lines[i + 2].lstrip().startswith("คำตอบ:"):
            key = norm_exact(en)
            a_en = lines[i + 1].strip()
            a_th = lines[i + 2].strip()
            ans.setdefault(key, []).extend([a_en, a_th])
            i += 3
            if i < len(lines) and not lines[i].strip():
                i += 1
            continue
        i += 1
    return ans


def build():
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-ru", dest="with_ru", action="store_true",
                        default=True)
    parser.add_argument("--no-ru", dest="with_ru", action="store_false")
    parser.add_argument("--with-th", dest="with_th", action="store_true",
                        default=True)
    parser.add_argument("--no-th", dest="with_th", action="store_false")
    parser.add_argument("--translations-source", type=str,
                        default="lesson3_translations_source.txt")
    parser.add_argument("--with-answers", dest="with_answers",
                        action="store_true", default=False)
    parser.add_argument("--answers-source", type=str,
                        default="lesson3_answers_source.txt")
    args = parser.parse_args()

    if not args.translations_source or not os.path.exists(
            args.translations_source):
        raise FileNotFoundError(
            f"Translations source not found: {args.translations_source}")

    ans_map = {}
    if args.with_answers and args.answers_source and os.path.exists(
            args.answers_source):
        ans_map = load_answers_from_source(args.answers_source)

    with open(args.translations_source, "r", encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f]

    doc = new_doc()

    i = 0
    total = len(lines)
    section = None

    while i < total:
        L = lines[i].rstrip("\n")
        if not L.strip():
            i += 1
            continue

        # секции
        low = L.lower().strip()
        if L in BLOCK_TITLES:
            if "explanation" in low:
                section = "expl"
            elif "practice" in low:
                section = "practice"
            elif "vocabulary (student graduation)" in low:
                section = "vocab"
            elif "vocabulary exercises" in low:
                section = "vocab_ex"
            elif "exit check" in low or "homework" in low:
                section = "exit"
            # печатаем заголовок как есть
            doc.add_paragraph(L)
            i += 1
            continue

        # Внутри Word bank (vocab) – переразмечаем строку по флагам RU/TH
        if section == "vocab" and " — " in L and re.match(r"^[A-Za-z]\.",
                                                          L.strip()):
            # ожидаем формат: a. <emoji?> EN — RU — TH
            parts = re.split(r"\s—\s", L, maxsplit=2)
            if len(parts) >= 2:
                left = parts[0]  # литер + EN (и эмодзи)
                ru_part = parts[1] if len(parts) >= 2 else None
                th_part = parts[2] if len(parts) >= 3 else None
                out_line = left
                if args.with_ru and ru_part:
                    out_line += " — " + ru_part
                if args.with_th and th_part:
                    out_line += " — " + th_part
                doc.add_paragraph(out_line)
                i += 1
                continue

        # если строка в скобках — это перевод и он должен идти только вместе с EN строкой — пропускаем здесь
        if L.strip().startswith("(") and L.strip().endswith(")"):
            i += 1
            continue

        # Печатаем EN строку как есть
        p_en = doc.add_paragraph(L)

        # Если далее есть RU/TH строки — добавим согласно флагам
        ru_txt = th_txt = None
        if i + 1 < total and lines[i + 1].strip().startswith("("):
            ru_txt = lines[i + 1].strip()
            if ru_txt.startswith("(") and ru_txt.endswith(")"):
                ru_txt = ru_txt[1:-1]
        if i + 2 < total and lines[i + 2].strip().startswith("("):
            th_txt = lines[i + 2].strip()
            if th_txt.startswith("(") and th_txt.endswith(")"):
                th_txt = th_txt[1:-1]

        if args.with_ru and ru_txt:
            line_ru(doc, ru_txt)
        if args.with_th and th_txt:
            line_th(doc, th_txt)

        # если это упражнение и включены ответы — добавим
        if args.with_answers and section in ("practice", "vocab_ex", "exit"):
            key = norm_exact(L)
            ans_lines = ans_map.get(key)
            if ans_lines:
                for a in ans_lines:
                    ap = doc.add_paragraph()
                    ar = ap.add_run(a)
                    ar.font.color.rgb = PURPLE

        # Шагаем. Если RU/TH использованы — перескочим их
        if ru_txt and th_txt:
            i += 3
        elif ru_txt or th_txt:
            i += 2
        else:
            i += 1

    doc.save(OUT_NAME)
    print("[lesson3] Saved:", OUT_NAME)


if __name__ == "__main__":
    build()
