import os
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from media_utils import extract_text_from_image, extract_text_from_video
from verifier import analyze_news_text, fetch_latest_events

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {'png','jpg','jpeg','webp','bmp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4','avi','mov','mkv','webm'}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)


def extension_of(filename):
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/api/analyze')
def analyze():
    text = (request.form.get('text') or '').strip()
    file = request.files.get('file')
    extracted_text = ''
    media_type = 'text'

    if file and file.filename:
        filename = secure_filename(file.filename)
        ext = extension_of(filename)
        if ext not in ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS:
            return jsonify({'error':'Unsupported file type. Upload an image or video.'}), 400

        save_path = UPLOAD_DIR / filename
        file.save(save_path)
        try:
            if ext in ALLOWED_IMAGE_EXTENSIONS:
                media_type = 'image'
                extracted_text = extract_text_from_image(save_path)
            else:
                media_type = 'video'
                extracted_text = extract_text_from_video(save_path)
        finally:
            save_path.unlink(missing_ok=True)

    combined = '\n'.join(x for x in [text, extracted_text] if x.strip()).strip()
    if not combined:
        return jsonify({'error':'Enter news text or upload an image/video containing readable text.'}), 400

    result = analyze_news_text(combined)
    result['input_type'] = media_type
    result['extracted_text'] = extracted_text
    return jsonify(result)


@app.get('/api/events')
def events():
    country = (request.args.get('country') or 'in').lower()
    category = request.args.get('category') or 'general'
    try:
        return jsonify({'events': fetch_latest_events(country, category)})
    except Exception as exc:
        return jsonify({'events':[], 'warning':str(exc)})


@app.errorhandler(413)
def too_large(_):
    return jsonify({'error':'Maximum upload size is 50 MB.'}), 413


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT','5000')), debug=True)
