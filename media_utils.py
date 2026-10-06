from pathlib import Path
import cv2
import pytesseract
from PIL import Image


def extract_text_from_image(path):
    image = Image.open(Path(path)).convert('RGB')
    return pytesseract.image_to_string(image).strip()


def extract_text_from_video(path, sample_every_seconds=3):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError('Could not open uploaded video.')

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    interval = max(int(fps * sample_every_seconds), 1)
    frame_no = 0
    collected, seen = [], set()

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_no % interval == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            text = ' '.join(pytesseract.image_to_string(rgb).split())
            if text and text not in seen:
                seen.add(text)
                collected.append(text)
        frame_no += 1

    cap.release()
    return '\n'.join(collected)
