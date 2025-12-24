"""
Document Management Module
Handles file uploads, parsing, and storage
"""

import os
import PyPDF2
import docx
import sqlite3
from datetime import datetime

class DocumentManager:
    """Manages document uploads and database operations"""
    
    def __init__(self, db_path='data/documents.db'):
        """Initialize document manager"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                content TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                word_count INTEGER,
                sentence_count INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def extract_text_from_pdf(self, filepath):
        """Extract text from PDF file"""
        text = ""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        return text
    
    def extract_text_from_docx(self, filepath):
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(filepath)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
        return text
    
    def extract_text_from_txt(self, filepath):
        """Extract text from TXT file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")
        return text
    
    def process_upload(self, filepath, filename):
        """Process uploaded file and extract text"""
        extension = filename.rsplit('.', 1)[1].lower()
        
        if extension == 'pdf':
            text = self.extract_text_from_pdf(filepath)
        elif extension == 'docx':
            text = self.extract_text_from_docx(filepath)
        elif extension == 'txt':
            text = self.extract_text_from_txt(filepath)
        else:
            raise Exception("Unsupported file format")
        
        return text
    
    def save_document(self, filename, filepath, content, word_count, sentence_count):
        """Save document metadata to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO documents (filename, filepath, content, word_count, sentence_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (filename, filepath, content, word_count, sentence_count))
        
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return doc_id
    
    def get_document(self, doc_id):
        """Retrieve document from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
        doc = cursor.fetchone()
        
        conn.close()
        return doc
    
    def get_all_documents(self):
        """Get all documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, filename, upload_date, word_count FROM documents ORDER BY upload_date DESC')
        docs = cursor.fetchall()
        
        conn.close()
        return docs
    
    def delete_document(self, doc_id):
        """Delete document from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        
        conn.commit()
        conn.close()