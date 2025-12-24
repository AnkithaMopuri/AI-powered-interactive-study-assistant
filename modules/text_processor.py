"""
NLP Text Processing Module
Handles tokenization, lemmatization, stop-word removal, and sentence segmentation
"""

import nltk
import spacy
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')

class TextProcessor:
    """Processes and preprocesses text using NLP techniques"""
    
    def __init__(self):
        """Initialize NLP tools"""
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Load spaCy model
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except:
            print("spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def clean_text(self, text):
        """Remove special characters and extra whitespace"""
        text = re.sub(r'[^\w\s\.\?\!,;:]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def tokenize(self, text):
        """Tokenize text into words"""
        return word_tokenize(text.lower())
    
    def remove_stopwords(self, tokens):
        """Remove common stop words"""
        return [token for token in tokens if token not in self.stop_words]
    
    def lemmatize(self, tokens):
        """Reduce words to their base form"""
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def segment_sentences(self, text):
        """Split text into sentences"""
        return sent_tokenize(text)
    
    def preprocess(self, text, remove_stops=True):
        """
        Complete preprocessing pipeline
        Returns: cleaned tokens and original sentences
        """
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Segment into sentences
        sentences = self.segment_sentences(cleaned_text)
        
        # Tokenize
        tokens = self.tokenize(cleaned_text)
        
        # Remove stopwords (optional)
        if remove_stops:
            tokens = self.remove_stopwords(tokens)
        
        # Lemmatize
        tokens = self.lemmatize(tokens)
        
        return {
            'cleaned_text': cleaned_text,
            'sentences': sentences,
            'tokens': tokens,
            'token_count': len(tokens)
        }
    
    def extract_key_phrases(self, text):
        """Extract key noun phrases using spaCy"""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        phrases = []
        
        # Extract noun chunks
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:
                phrases.append(chunk.text)
        
        return list(set(phrases))[:10]