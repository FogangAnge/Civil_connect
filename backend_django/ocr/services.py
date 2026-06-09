import re

import pytesseract
from django.conf import settings
from PIL import Image, ImageEnhance, ImageFilter


def preprocess_image(img: Image.Image) -> Image.Image:
    img = img.convert('L')
    img = ImageEnhance.Contrast(img).enhance(1.8)
    img = img.filter(ImageFilter.SHARPEN)
    # binarisation simple
    img = img.point(lambda p: 255 if p > 160 else 0)
    return img


def parse_text(text: str) -> dict:
    def find(pattern: str):
        m = re.search(pattern, text, flags=re.IGNORECASE)
        return (m.group(1).strip() if m else '')

    return {
        'nom': find(r'Nom\s*:\s*([A-ZÉÈÊËÀÂÎÏÔÖÛÜÇ\- ]{2,})'),
        'prenoms': find(r'Pr[eé]noms?\s*:\s*([A-ZÉÈÊËÀÂÎÏÔÖÛÜÇ\- ]{2,})'),
        'date_naissance': find(r'Date\s+de\s+naissance\s*:\s*([0-9]{2}[\/\-][0-9]{2}[\/\-][0-9]{4})'),
        'lieu': find(r'Lieu\s*:\s*([A-ZÉÈÊËÀÂÎÏÔÖÛÜÇ0-9\- ]{2,})'),
        'pere': find(r'P[eè]re\s*:\s*([A-ZÉÈÊËÀÂÎÏÔÖÛÜÇ\- ]{2,})'),
        'mere': find(r'M[eè]re\s*:\s*([A-ZÉÈÊËÀÂÎÏÔÖÛÜÇ\- ]{2,})'),
    }


def compute_score(data: dict) -> float:
    keys = ['nom', 'prenoms', 'date_naissance', 'lieu', 'pere', 'mere']
    found = sum(1 for k in keys if (data.get(k) or '').strip())
    return found / float(len(keys))


def run_ocr(image_path: str) -> tuple[str, dict, float]:
    cmd = getattr(settings, 'TESSERACT_CMD', '') or None
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd
    img = Image.open(image_path)
    img = preprocess_image(img)
    config = '--oem 3 --psm 6 -l fra'
    text = pytesseract.image_to_string(img, config=config)
    data = parse_text(text)
    score = compute_score(data)
    return text, data, score

