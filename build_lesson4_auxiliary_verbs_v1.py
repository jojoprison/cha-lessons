# -*- coding: utf-8 -*-
# build_lesson4_auxiliary_verbs_v1.py
# Генерит DOCX: cha_lesson_4_auxiliary_verbs_v1.docx на основе cha_lesson_4_auxiliary_verbs_lite_v3.docx
# Требования:
# - Добавить RU строку после каждой EN строки в Explanation / Practice / Vocabulary Exercises / Exit check & Homework
#   (тёмно-красный курсив), а подчёркнутые фрагменты и капс из EN — отзеркалить в RU (чёрный, bold+underline, CAPS).
# - В Vocabulary после RU добавить « — TH» перевод модальных/вспомогательных.

import os
import re
import time

from deep_translator import GoogleTranslator
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Cm

# ---------- Цвета и стили ----------
GOLD = RGBColor(184, 134, 11)
BLACK = RGBColor(0, 0, 0)
DARK_RED = RGBColor(139, 0, 0)
DARK_GREEN = RGBColor(0, 100, 0)
PURPLE = RGBColor(102, 0, 153)

THAI_FONT_NAME = "Noto Sans Thai"

SRC_NAME = "cha_lesson_4_auxiliary_verbs_lite_v3.docx"
OUT_NAME = "cha_lesson_4_auxiliary_verbs_v1.docx"

# Тайский словарь для Vocabulary (ключ — нормализованный EN термин)
TH_VOCAB = {
    "can": "สามารถ",
    "could": "อาจจะ / สามารถ(อดีต)",
    "may": "อาจจะ",
    "might": "อาจจะ",
    "must": "ต้อง",
    "have to": "จำเป็นต้อง / ต้อง",
    "has to": "จำเป็นต้อง / ต้อง",
    "had to": "จำเป็นต้อง / ต้อง (อดีต)",
    "should": "ควร",
    "would": "จะ / มักจะ (สมมุติ)",
    "will": "จะ",
    "shall": "จะ (ทางการ)",
    "do": "ทำ (ตัวช่วยไวยากรณ์)",
    "does": "ทำ (ตัวช่วยไวยากรณ์)",
    "did": "ทำ (อดีต, ตัวช่วยไวยากรณ์)",
    "be": "เป็น/อยู่/คือ",
    "am": "เป็น/อยู่/คือ",
    "is": "เป็น/อยู่/คือ",
    "are": "เป็น/อยู่/คือ",
    "was": "เป็น/อยู่/คือ",
    "were": "เป็น/อยู่/คือ",
    "have": "มี / ได้ทำ (สมบูรณ์)",
    "has": "มี / ได้ทำ (สมบูรณ์)",
    "had": "มี / ได้ทำ (อดีต)",
    "be able to": "สามารถ",
    "need to": "จำเป็นต้อง",
    "ought to": "ควรจะ",
    "used to": "เคย",
    "dare": "กล้า",
    "had better": "ควรจะ...ดีกว่า",
}

# Базовый RU-словарь для Vocabulary
RU_VOCAB = {
    "can": "может",
    "could": "мог(ла)/могли",
    "may": "может",
    "might": "возможно",
    "must": "должен",
    "have to": "должен/приходится",
    "has to": "должен/приходится",
    "had to": "должен был/пришлось",
    "should": "следует",
    "would": "бы",
    "will": "будет",
    "shall": "будет (офиц.)",
    "do": "делать (всп.)",
    "does": "делает (всп.)",
    "did": "сделал (всп.)",
    "be": "быть",
    "am": "есть",
    "is": "есть",
    "are": "есть",
    "was": "был",
    "were": "были",
    "have": "иметь",
    "has": "имеет",
    "had": "имел",
    "be able to": "может/в состоянии",
    "need to": "нужно/необходимо",
    "ought to": "следовало бы",
    "used to": "раньше делал/обычно",
    "dare": "осмеливаться",
    "had better": "лучше бы/следует",
}

# Простейший «переводчик» на RU (черновой): токен-замены для базовых слов. Остальное оставляем как есть.
RU_TOKEN_MAP = {
    "i": "я", "you": "ты", "we": "мы", "they": "они", "he": "он", "she": "она",
    "it": "это",
    "can": "может", "could": "мог(ла)/могли", "may": "может",
    "might": "возможно", "must": "должен",
    "have": "имеем/имеет/имею", "has": "имеет", "had": "имел/имели", "to": "",
    "be": "быть",
    "am": "есть", "is": "есть", "are": "есть", "was": "был", "were": "были",
    "will": "будет", "shall": "будет", "would": "бы", "should": "следует",
    "do": "делать", "does": "делает", "did": "сделал",
    "not": "не", "no": "нет", "yes": "да", "and": "и", "or": "или", "but": "но",
}

# Инициализируем переводчик: auto -> ru
TRANSLATOR = GoogleTranslator(source='auto', target='ru')


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


def clone_run(dst_p, src_run):
    r = dst_p.add_run(src_run.text)
    # базовые атрибуты
    try:
        r.font.bold = src_run.font.bold
        r.font.italic = src_run.font.italic
        r.font.underline = src_run.font.underline
        r.font.size = src_run.font.size
        r.font.all_caps = src_run.font.all_caps
        if src_run.font.color and src_run.font.color.rgb:
            r.font.color.rgb = src_run.font.color.rgb
    except Exception:
        pass
    return r


def clone_paragraph(dst_doc, src_p):
    p = dst_doc.add_paragraph()
    # копируем выравнивание, если нужно
    p.alignment = src_p.alignment
    for run in src_p.runs:
        clone_run(p, run)
    return p


def translate_ru(text: str) -> str:
    if not text:
        return ""
    try:
        return TRANSLATOR.translate(text)
    except Exception:
        # Фоллбек — вернуть исходный текст (чтобы не падать)
        return text


def add_ru_line_for_en_paragraph(dst_doc, src_p):
    """
    Переводим каждый EN-run целиком на русский и собираем RU строку из таких фрагментов,
    зеркалим подчёркнутые участки (чёрный bold+underline) и CAPS.
    """
    p = dst_doc.add_paragraph()
    # открывающая скобка (красный курсив)
    r0 = p.add_run("(")
    r0.font.italic = True
    r0.font.color.rgb = DARK_RED
    for run in src_p.runs:
        src_text = run.text
        if not src_text:
            continue
        ru_piece = translate_ru(src_text)
        # CAPS зеркалим
        if src_text.isupper():
            ru_piece = ru_piece.upper()
        r = p.add_run(ru_piece)
        # базово RU — тёмно-красный курсив
        r.font.italic = True
        r.font.color.rgb = DARK_RED
        # зеркалим подчёркивание (делаем чёрным, bold+underline)
        try:
            if run.font and run.font.underline:
                r.font.color.rgb = BLACK
                r.font.bold = True
                r.font.underline = True
                r.font.italic = False
        except Exception:
            pass
    # закрывающая скобка
    rZ = p.add_run(")")
    rZ.font.italic = True
    rZ.font.color.rgb = DARK_RED


def is_section_title(text: str) -> bool:
    if not text:
        return False
    t = text.strip()
    # Заголовки в уроках часто содержат эмодзи или оканчиваются на ':' как в "✍️ Examples:"
    return bool(t and (t.endswith(":") or t.startswith("#") or (
            len(t) <= 64 and any(ch for ch in t if ord(ch) > 1000))))


def is_examples_label(text: str) -> bool:
    return text.strip().endswith("Examples:")


def is_vocab_item(text: str) -> bool:
    # Примитивная эвристика: строка типа "A. can — может"
    t = text.strip()
    if re.match(r"^[A-Za-z]\.\s+", t):
        return True
    # или строка с EN — RU уже
    if " — " in t and not any(ch.isdigit() for ch in t.split(" — ")[0][:3]):
        return True
    return False


def normalize_key(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def append_th_to_vocab_line(dst_p):
    # Разбираем текущую строку, пытаемся получить EN термин
    full = dst_p.text
    parts = full.split(" — ")
    # EN часть до первого тире или вся строка
    en_part = parts[0] if parts else full
    en_term = re.sub(r"^[A-Za-z]\.\s+", "", en_part).strip()

    # Подбор переводов
    th = TH_VOCAB.get(normalize_key(en_term))
    if not th:
        for k in list(TH_VOCAB.keys()):
            if normalize_key(k) == normalize_key(en_term):
                th = TH_VOCAB[k]
                break
    ru = RU_VOCAB.get(normalize_key(en_term))
    if not ru:
        for k in list(RU_VOCAB.keys()):
            if normalize_key(k) == normalize_key(en_term):
                ru = RU_VOCAB[k]
                break

    # Если RU уже есть в строке — просто добавляем TH
    ru_added = False
    th_added = False
    if " — " in full:
        if th:
            rr = dst_p.add_run(" — ")
            rr.font.italic = True
            rr.font.color.rgb = DARK_GREEN
            tr = dst_p.add_run(th)
            tr.font.italic = True
            tr.font.color.rgb = DARK_GREEN
            tr.font.name = THAI_FONT_NAME
            th_added = True
        return ru_added, th_added

    # Если RU не было — добавляем RU и TH
    if ru:
        rr_sep = dst_p.add_run(" — ")
        rr_sep.font.italic = True
        rr_sep.font.color.rgb = DARK_RED
        rr_run = dst_p.add_run(ru)
        rr_run.font.italic = True
        rr_run.font.color.rgb = DARK_RED
        ru_added = True
    if th:
        th_sep = dst_p.add_run(" — ")
        th_sep.font.italic = True
        th_sep.font.color.rgb = DARK_GREEN
        tr = dst_p.add_run(th)
        tr.font.italic = True
        tr.font.color.rgb = DARK_GREEN
        tr.font.name = THAI_FONT_NAME
        th_added = True
    return ru_added, th_added


def build():
    start_ts = time.time()
    print("[lesson4] Start generation")
    src_path = os.path.join(os.getcwd(), SRC_NAME)
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source DOCX not found: {src_path}")
    print(f"[lesson4] Source: {SRC_NAME}")
    src = Document(src_path)

    out = new_doc()
    print("[lesson4] New document initialized")

    # Простая машина состояний по секциям
    section = None
    ru_lines = 0
    vocab_th_added = 0
    vocab_ru_added = 0

    total = len(src.paragraphs)
    print(f"[lesson4] Paragraphs: {total}")

    for idx, p in enumerate(src.paragraphs, 1):
        text = p.text or ""
        # Клонируем исходную строку как есть
        new_p = clone_paragraph(out, p)

        # Определяем смену секции по ключевым словам
        t = text.strip().lower()
        if "vocabulary" in t and len(t) < 64:
            if section != "vocab":
                print("[lesson4] --> Section: Vocabulary")
            section = "vocab"
        elif "vocabulary exercises" in t:
            if section != "vocab_ex":
                print("[lesson4] --> Section: Vocabulary Exercises")
            section = "vocab_ex"
        elif "practice" in t:
            if section != "practice":
                print("[lesson4] --> Section: Practice")
            section = "practice"
        elif "exit check" in t or "homework" in t:
            if section != "exit":
                print("[lesson4] --> Section: Exit check & Homework")
            section = "exit"
        elif "explanation" in t or "examples" in t:
            if section != "expl":
                print("[lesson4] --> Section: Explanation/Examples")
            section = "expl"

        # Если это пункт словаря — добавим TH
        if section == "vocab" and is_vocab_item(text):
            before = new_p.text
            # функция вернёт, добавляли ли RU/TH
            ru_added, th_added = append_th_to_vocab_line(new_p)
            if ru_added:
                vocab_ru_added += 1
            if th_added:
                vocab_th_added += 1
            continue  # для словаря RU-строку отдельную не вставляем (она уже на линии)

        # Для всех остальных контентных EN строк — добавляем RU строку
        stripped = text.strip()
        if not stripped:
            continue
        # не добавляем перевод к явным заголовкам и меткам типа "Examples:"
        if is_examples_label(text):
            continue
        # Для заголовков разделов не добавляем
        if stripped.endswith(":") and len(stripped) < 64:
            continue

        # Вставляем RU перевод под строкой
        add_ru_line_for_en_paragraph(out, p)
        ru_lines += 1

        # прогресс каждые 20 параграфов
        if idx % 20 == 0:
            print(f"[lesson4] Progress: {idx}/{total} paragraphs processed")

    out.save(OUT_NAME)
    dur = time.time() - start_ts
    print("[lesson4] Saved:", OUT_NAME)
    print(
        f"[lesson4] Summary: RU lines added={ru_lines}, vocab TH added={vocab_th_added}, vocab RU added={vocab_ru_added}")
    print(f"[lesson4] Done in {dur:.1f}s")


if __name__ == "__main__":
    build()
