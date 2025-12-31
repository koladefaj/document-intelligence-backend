import pytesseract
from PyPDF2 import PdfReader
from PIL import Image
from pdf2image import convert_from_path
import pandas as pd
import os
import tempfile
from google import genai
from app.infrastructure.config import settings
from docx import Document as DocxReader



class DocumentProcessor:
    def __init__(self):
        # Initialize the client once during startup
        # Strip quotes in case they exist in the .env file
        self.api_key = settings.gemini_api.strip('"')
        self.client = genai.Client(api_key=self.api_key)


    def extract_text(self, file_path: str) -> str:
        """Handles normal digital PDFs"""
        try:
            # Only try Pdf reading if its pdf
            if not file_path.lower().endswith(".pdf"):
                return ""
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
        except Exception:
            return ""


    def ocr_text(self, file_path: str) -> str:
        """OCR for images or scanned PDFs"""
        # if it's a PDF convert each page to image
        text = ""
        try:
            if file_path.lower().endswith(".pdf"):
                pages = convert_from_path(file_path)
                for page in pages:
                    with tempfile.NamedTemporaryFile(suffix="png", delete=False) as tmp:
                        page.save(tmp.name, "PNG")
                        text += pytesseract.image_to_string(Image.open(tmp.name), lang="eng")
                        os.remove(tmp.name)
            elif file_path.lower().endswith((".png", ".jpg", ".jpeg")):
                text = pytesseract.image_to_string(Image.open(file_path), lang="eng")

        except Exception as e:
            print(f"OCR Error: {e}")

        return text
    
    def get_ai_summary(self, text: str) -> str:
        """Uses Gemini's Free Tier to summarize the document"""

        if not text or len(text.strip()) < 50:
            return "Text too short to summarize."

        try:
            model = 'gemini-1.5-flash'
            prompt = f"Summarize this document professionally in 3-5 bullet points:\n\n{text[:15000]}"
            
            response = self.client.models.generate_content(model=model, contents=prompt)
            return response.text
        except Exception as e:
            print(f"gemini error: {e}")
            raise e

    def analyze_text(self, text: str) -> dict:
        """Return metadata / structure"""

        summary = self.get_ai_summary(text)
        
        safe_text = text if text else ""

        return {
            "summary": summary,
            "word_count": len(safe_text.split()),
            "contains_email": "@" in safe_text,
            "contains_money": any(symbol in safe_text for symbol in ["$", "USD"])
        }

    def process(self, file_path: str) -> dict:
        text = ""
        ext = file_path.lower()

        try:
            if ext.endswith(".pdf"):
                text = self.extract_text(file_path)
            
            elif ext.endswith((".docx", ".doc")):
                doc = DocxReader(file_path)
                text = "\n".join([p.text for p in doc.paragraphs])
            
            elif ext.endswith((".xlsx", ".xls", ".csv")):
                # For Excel, we convert the rows to a text string
                df = pd.read_excel(file_path) if not ext.endswith(".csv") else pd.read_csv(file_path)
                text = df.to_string()
            
            elif ext.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

            # FALLBACK: If it's an image or a scanned PDF (text is still empty)
            if not text or not text.strip():
                if ext.endswith((".png", ".jpg", ".jpeg", ".pdf")):
                    text = self.ocr_text(file_path)

        except Exception as e:
            print(f"Extraction error: {e}")
            text = ""

        return {
            "raw_text": text,
            "analysis": self.analyze_text(text)
        }