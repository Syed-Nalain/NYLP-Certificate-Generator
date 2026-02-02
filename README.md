# NYLP Certificate generator

NYLP Certificate generator — automatic PDF certificate generation tool.  
Made by Nalain-e-Muhammad

Quick start
1. Create and activate a virtual environment:
   - python -m venv venv
   - venv\Scripts\activate

2. Install dependencies:
   - pip install -r requirements.txt

3. Place any .ttf fonts into the `fonts/` folder to make them available in the app.

4. Run the application:
   - python pdf_templater.py

Notes
- The app no longer writes an export note file; exported PDFs are written to the selected output directory.