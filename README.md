# WorldLens - Global News Verifier

WorldLens is a student project that accepts news as text, image, or video and helps the user investigate whether a claim is supported, disputed, or still unverified.

## Features
- Text claim verification
- OCR from uploaded images
- OCR from sampled video frames
- Optional Google Fact Check Tools API lookup
- Optional NewsAPI related coverage and latest headlines
- Simple wording/context red-flag analysis
- Flask + HTML + CSS + JavaScript interface

## Important limitation
This project is not a perfect fake-news detector. A reliable decision requires evidence and source verification. Without external API keys, the result is only a preliminary assessment.

## Project structure
```text
WorldLens/
├── app.py
├── verifier.py
├── media_utils.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

## Setup
1. Install Python 3.10+.
2. Install Tesseract OCR.
   - Ubuntu: `sudo apt install tesseract-ocr`
   - Windows: install Tesseract and add it to PATH.
3. Create a virtual environment.
4. Run `pip install -r requirements.txt`.
5. Copy `.env.example` to `.env` and add optional API keys.
6. Run `python app.py`.
7. Open `http://127.0.0.1:5000`.

## GitHub
Upload this project to your public repository named `upskillcampus` together with your final internship PDF report.
