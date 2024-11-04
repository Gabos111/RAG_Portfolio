import os
import json
from datetime import datetime
import re
from collections import defaultdict
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pdf_to_text import FinancialKeywords
import numpy as np

class ArticleProcessor:
    def __init__(self, articles_dir: str, output_file: str):
        self.articles_dir = articles_dir
        self.output_file = output_file
        self.existing_chunks = self.load_existing_chunks()
        self.keywords = FinancialKeywords()  # Using your existing FinancialKeywords class
        
    def load_existing_chunks(self) -> List[Dict]:
        """Load existing chunks from the output file"""
        try:
            with open(self.output_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def find_keywords_in_text(self, text: str) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
        """Find all financial keywords in text with context"""
        text_lower = text.lower()
        findings = defaultdict(lambda: defaultdict(list))
        context_window = 100
        
        for category_group_name, category_group in {
            'FINANCIAL_METRICS': self.keywords.FINANCIAL_METRICS,
            'COMPANY_STATE': self.keywords.COMPANY_STATE,
            'RISK_FACTORS': self.keywords.RISK_FACTORS,
            'BUSINESS_OUTLOOK': self.keywords.BUSINESS_OUTLOOK
        }.items():
            for category_name, keywords in category_group.items():
                for keyword in keywords:
                    for match in re.finditer(r'\b' + re.escape(keyword) + r'\b', text_lower):
                        start = max(0, match.start() - context_window)
                        end = min(len(text), match.end() + context_window)
                        
                        findings[category_group_name][category_name].append({
                            'keyword': keyword,
                            'context': text[start:end].strip(),
                            'position': match.start(),
                            'sentence': self.find_containing_sentence(text, match.start())
                        })
        
        return dict(findings)

    def find_containing_sentence(self, text: str, position: int) -> str:
        """Find the full sentence containing the given position"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_pos = 0
        
        for sentence in sentences:
            sentence_length = len(sentence) + 2
            if current_pos <= position < current_pos + sentence_length:
                return sentence.strip()
            current_pos += sentence_length
        
        return ""

    def extract_company_from_header(self, header: str) -> str:
        """Extract company name from article header"""
        # Common company name patterns
        company_patterns = [
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'s",  # Pattern for possessive form
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Inc\.|Corp\.|Ltd\.|LLC|Group)",  # Pattern with suffix
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"  # Simple capitalized words
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, header)
            if match:
                return match.group(1)
        
        return "Unknown"

    def extract_date_from_header(self, date_str: str) -> str:
        """Extract year from date string"""
        match = re.search(r'(\d{4})', date_str)
        if match:
            return match.group(1)
        return "unknown"

    def process_article(self, header: str, date: str, content: str, article_number: int) -> Dict:
        """Process a single article and return chunk data"""
        company = self.extract_company_from_header(header)
        year = self.extract_date_from_header(date)
        
        chunk_id = f"{company}_{year}_article_{article_number:03d}"
        word_count = len(content.split())
        
        return {
            'chunk_id': chunk_id,
            'content': content,
            'word_count': word_count,
            'keyword_analysis': self.find_keywords_in_text(content),
            'company': company,
            'year': year,
            'source': f"article_{article_number}",
            'processing_date': datetime.now().isoformat()
        }

    def process_articles_directory(self):
        """Process all articles in the directory and add them to existing chunks"""
        article_chunks = []
        article_number = 1

        # Read all files in the articles directory
        for filename in os.listdir(self.articles_dir):
            if filename.endswith('.txt'):
                with open(os.path.join(self.articles_dir, filename), 'r') as f:
                    content = f.read()
                    
                    # Parse article content
                    # Assuming format: header\ndate\ncontent
                    parts = content.strip().split('\n', 2)
                    if len(parts) == 3:
                        header, date, article_content = parts
                        chunk = self.process_article(header, date, article_content, article_number)
                        article_chunks.append(chunk)
                        article_number += 1

        # Combine existing chunks with new article chunks
        all_chunks = self.existing_chunks + article_chunks
        
        # Calculate similarities for all chunks
        texts = [chunk['content'] for chunk in all_chunks]
        tfidf = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = tfidf.fit_transform(texts)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Update similarities
        similarities = {}
        for i, chunk in enumerate(all_chunks):
            similar_chunks = []
            for j in np.argsort(similarity_matrix[i])[-4:-1][::-1]:
                if i != j and similarity_matrix[i][j] > 0.3:
                    similar_chunks.append({
                        'chunk_id': all_chunks[j]['chunk_id'],
                        'similarity_score': float(similarity_matrix[i][j])
                    })
            similarities[chunk['chunk_id']] = similar_chunks
        
        # Save updated chunks
        with open(self.output_file, 'w') as f:
            json.dump(all_chunks, f, indent=2)
        
        # Save updated similarities
        similarities_file = os.path.join(os.path.dirname(self.output_file), 'similarities.json')
        with open(similarities_file, 'w') as f:
            json.dump(similarities, f, indent=2)
        
        print(f"Processed {len(article_chunks)} articles")
        print(f"Total chunks after processing: {len(all_chunks)}")
        print(f"Updated chunks saved to: {self.output_file}")
        print(f"Updated similarities saved to: {similarities_file}")

# Example usage
if __name__ == "__main__":
    processor = ArticleProcessor(
        articles_dir="./articles",
        output_file="./data/raw_processed/all_chunks.json"
    )
    processor.process_articles_directory()