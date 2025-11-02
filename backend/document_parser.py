"""
Document parser for PDF and DOCX files with encoding detection.
Supports multiple encodings: UTF-8, UTF-16, CP1251, KOI8-R, ISO-8859-5, MacRoman, ASCII.
"""
import os
from typing import Optional
import chardet
try:
    import fitz  # PyMuPDF - preferred for better PDF parsing
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    fitz = None

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    PyPDF2 = None

from docx import Document


class DocumentParser:
    """Parse PDF and DOCX documents with encoding detection."""
    
    # Supported encodings
    ENCODINGS = ['utf-8', 'utf-16', 'cp1251', 'koi8-r', 'iso-8859-5', 'macroman', 'ascii']
    
    def __init__(self):
        self.max_size = 120 * 50 * 1000  # ~120 pages estimate (50KB per page)
    
    def detect_encoding(self, text_bytes: bytes) -> str:
        """Detect encoding of text bytes."""
        result = chardet.detect(text_bytes)
        detected = result['encoding'].lower()
        
        # Normalize encoding names
        encoding_map = {
            'windows-1251': 'cp1251',
            'utf-8': 'utf-8',
            'utf-16': 'utf-16',
            'koi8-r': 'koi8-r',
            'iso-8859-5': 'iso-8859-5',
            'macroman': 'macroman',
            'ascii': 'ascii'
        }
        
        return encoding_map.get(detected, 'utf-8')
    
    def parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF file. Uses PyMuPDF if available, falls back to PyPDF2."""
        text_parts = []
        
        # Try PyMuPDF first (better quality)
        if HAS_PYMUPDF:
            try:
                doc = fitz.open(file_path)
                for page in doc:
                    text = page.get_text("text")
                    if text:
                        text_parts.append(text)
                doc.close()
                return '\n\n'.join(text_parts)
            except Exception as e:
                print(f"Warning: PyMuPDF failed, trying PyPDF2: {e}")
        
        # Fallback to PyPDF2
        if HAS_PYPDF2:
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                text_parts.append(page_text)
                        except Exception as e:
                            print(f"Warning: Could not extract page {page_num + 1}: {e}")
                
                return '\n'.join(text_parts)
            except Exception as e:
                raise ValueError(f"Error reading PDF with PyPDF2: {str(e)}")
        
        raise ValueError("No PDF parser available. Install PyMuPDF (pymupdf) or PyPDF2.")
    
    def parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs]
            return '\n'.join(paragraphs)
        
        except Exception as e:
            raise ValueError(f"Error reading DOCX: {str(e)}")
    
    def parse(self, file_path: str) -> str:
        """
        Parse document (PDF or DOCX) and return text.
        
        Args:
            file_path: Path to the document file
        
        Returns:
            Extracted text content
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file size (estimate: max 120 pages)
        file_size = os.path.getsize(file_path)
        if file_size > self.max_size:
            raise ValueError(f"File too large: {file_size} bytes. Maximum size: {self.max_size} bytes")
        
        # Parse based on file extension
        if file_path.lower().endswith('.pdf'):
            text = self.parse_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            text = self.parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        if not text or len(text.strip()) == 0:
            raise ValueError("Document appears to be empty or could not extract text")
        
        return text

