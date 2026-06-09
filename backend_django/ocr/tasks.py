from celery import shared_task

from .models import NumerisationOCR
from .services import run_ocr


@shared_task
def process_ocr_image(ocr_id: str) -> None:
    ocr = NumerisationOCR.objects.filter(id=ocr_id).first()
    if not ocr or not ocr.image:
        return
    text, data, score = run_ocr(ocr.image.path)
    ocr.ocr_text_brut = text
    ocr.donnees_extraites = data
    ocr.score_confiance = float(score)
    ocr.save(update_fields=['ocr_text_brut', 'donnees_extraites', 'score_confiance', 'updated_at'])

