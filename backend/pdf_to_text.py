import os
import PyPDF2
import re
from typing import List, Dict, Set
import json
from datetime import datetime
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class FinancialKeywords:
    """Comprehensive financial keyword categorization"""
    
    FINANCIAL_METRICS = {
        'revenue_terms': {
            'revenue', 'sales', 'turnover', 'top line', 'gross income',
            'operating income', 'net income', 'ebit', 'ebitda', 'profit margin',
            'gross margin', 'operating margin', 'net margin', 'recurring revenue',
            'non-recurring revenue', 'service revenue', 'product revenue',
            'subscription revenue', 'licensing revenue', 'royalty income'
        },
        'profitability': {
            'profit', 'earnings', 'net profit', 'gross profit', 'operating profit',
            'profit before tax', 'profit after tax', 'retained earnings',
            'earnings per share', 'eps', 'diluted eps', 'adjusted earnings',
            'normalized earnings', 'core earnings', 'operating earnings',
            'pretax income', 'after-tax income', 'net margin', 'profit growth'
        },
        'balance_sheet': {
            'assets', 'liabilities', 'equity', 'current assets', 'fixed assets',
            'current liabilities', 'long-term debt', 'shareholders equity',
            'working capital', 'inventory', 'accounts receivable', 'cash flow',
            'goodwill', 'intangible assets', 'tangible assets', 'current ratio',
            'debt-to-equity', 'quick ratio', 'capital expenditure', 'capex'
        },
        'cash_flow': {
            'operating cash flow', 'free cash flow', 'cash from operations',
            'investing cash flow', 'financing cash flow', 'cash position',
            'cash equivalents', 'cash reserves', 'cash generation', 
            'cash conversion', 'cash burn rate', 'working capital changes'
        }
    }
    
    COMPANY_STATE = {
        'financial_health': {
            'solvency', 'liquidity', 'bankruptcy risk', 'going concern',
            'financial stability', 'credit rating', 'default risk',
            'debt coverage', 'interest coverage', 'cash reserves',
            'capital adequacy', 'financial flexibility', 'debt capacity'
        },
        'growth_indicators': {
            'organic growth', 'inorganic growth', 'market expansion',
            'revenue growth', 'profit growth', 'customer growth',
            'user growth', 'subscriber growth', 'market share growth',
            'expansion rate', 'growth momentum', 'growth trajectory'
        },
        'operational_efficiency': {
            'cost efficiency', 'operational leverage', 'economies of scale',
            'productivity', 'capacity utilization', 'asset turnover',
            'inventory turnover', 'operating efficiency', 'cost optimization',
            'process improvement', 'automation', 'digitalization'
        },
        'market_position': {
            'market leader', 'market share', 'competitive position',
            'brand strength', 'market penetration', 'market presence',
            'industry ranking', 'market dominance', 'market influence',
            'competitive advantage', 'market power', 'pricing power'
        }
    }
    
    RISK_FACTORS = {
        'operational_risks': {
            'supply chain risk', 'operational disruption', 'cyber risk',
            'it systems risk', 'technology risk', 'production risk',
            'quality control', 'supplier dependency', 'labor risk',
            'workplace safety', 'environmental risk', 'regulatory compliance'
        },
        'financial_risks': {
            'credit risk', 'market risk', 'liquidity risk', 'interest rate risk',
            'currency risk', 'commodity risk', 'investment risk',
            'counterparty risk', 'derivative risk', 'hedging risk',
            'asset liability mismatch', 'capital risk'
        },
        'strategic_risks': {
            'competition risk', 'market saturation', 'technological disruption',
            'regulatory change', 'political risk', 'reputation risk',
            'business model risk', 'innovation risk', 'acquisition risk',
            'integration risk', 'succession risk', 'talent retention'
        }
    }
    
    BUSINESS_OUTLOOK = {
        'future_prospects': {
            'outlook', 'guidance', 'forecast', 'projection', 'target',
            'expected growth', 'future investment', 'strategic initiative',
            'planned expansion', 'future opportunities', 'growth potential',
            'market opportunity', 'development pipeline'
        },
        'challenges': {
            'headwind', 'challenge', 'obstacle', 'constraint', 'limitation',
            'competitive pressure', 'market uncertainty', 'cost pressure',
            'regulatory pressure', 'margin pressure', 'pricing pressure',
            'supply constraint', 'demand uncertainty'
        },
        'strategic_initiatives': {
            'strategic plan', 'transformation', 'restructuring', 'cost reduction',
            'efficiency program', 'innovation initiative', 'digital transformation',
            'market expansion', 'product development', 'r&d investment',
            'capital allocation', 'growth strategy'
        }
    }

class EnhancedFinancialReportProcessor:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.keywords = FinancialKeywords()
        self.tfidf = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
        os.makedirs(output_dir, exist_ok=True)

    def find_keywords_in_text(self, text: str) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
        """Find all financial keywords in text with context"""
        text_lower = text.lower()
        findings = defaultdict(lambda: defaultdict(list))
        
        # Define context window size (in characters)
        context_window = 100
        
        # Search through all keyword categories
        for category_group_name, category_group in {
            'FINANCIAL_METRICS': self.keywords.FINANCIAL_METRICS,
            'COMPANY_STATE': self.keywords.COMPANY_STATE,
            'RISK_FACTORS': self.keywords.RISK_FACTORS,
            'BUSINESS_OUTLOOK': self.keywords.BUSINESS_OUTLOOK
        }.items():
            for category_name, keywords in category_group.items():
                for keyword in keywords:
                    for match in re.finditer(r'\b' + re.escape(keyword) + r'\b', text_lower):
                        # Get surrounding context
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
            sentence_length = len(sentence) + 2  # +2 for the delimiter and space
            if current_pos <= position < current_pos + sentence_length:
                return sentence.strip()
            current_pos += sentence_length
        
        return ""

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file with enhanced error handling"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                if reader.is_encrypted:
                    print(f"Warning: {file_path} is encrypted. Attempting to decrypt...")
                    try:
                        reader.decrypt('')
                    except:
                        raise ValueError("PDF is encrypted and couldn't be decrypted")
                
                text = ''
                for page in reader.pages:
                    try:
                        text += page.extract_text() + '\n'
                    except Exception as e:
                        print(f"Warning: Couldn't extract text from a page: {str(e)}")
                        continue
                
                return text
                
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            return ""

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,;:?!-]', '', text)
        return text.strip()

    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Split text into chunks with keyword analysis"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        chunk_number = 1
        
        current_chunk = []
        current_length = 0
        max_length = 500
        overlap = 50
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            if current_length + sentence_words > max_length and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunk_id = f"{metadata['company']}_{metadata['year']}_{chunk_number:03d}"
                
                # Analyze keywords in chunk
                keyword_analysis = self.find_keywords_in_text(chunk_text)
                
                chunk = {
                    'chunk_id': chunk_id,
                    'content': chunk_text,
                    'word_count': current_length,
                    'keyword_analysis': keyword_analysis,
                    **metadata
                }
                
                chunks.append(chunk)
                chunk_number += 1
                
                overlap_sentences = current_chunk[-2:] if len(current_chunk) > 2 else []
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s.split()) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_words
        
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'chunk_id': f"{metadata['company']}_{metadata['year']}_{chunk_number:03d}",
                'content': chunk_text,
                'word_count': current_length,
                'keyword_analysis': self.find_keywords_in_text(chunk_text),
                **metadata
            })
        
        return chunks

    def process_single_file(self, filename: str) -> List[Dict]:
        """Process a single PDF file"""
        file_path = os.path.join(self.input_dir, filename)
        
        raw_text = self.extract_text_from_pdf(file_path)
        if not raw_text:
            print(f"Warning: No text extracted from {filename}")
            return []
            
        cleaned_text = self.clean_text(raw_text)
        
        metadata = {
            'company': filename.split('_')[0] if '_' in filename else filename.split('.')[0],
            'year': re.search(r'20\d{2}', filename).group(0) if re.search(r'20\d{2}', filename) else 'unknown',
            'source': filename,
            'processing_date': datetime.now().isoformat()
        }
        
        return self.chunk_text(cleaned_text, metadata)

    def process_all_files(self) -> None:
        """Process all PDF files with keyword analysis"""
        all_chunks = []
        processing_stats = defaultdict(int)
        keyword_stats = defaultdict(lambda: defaultdict(int))
        
        for filename in os.listdir(self.input_dir):
            if filename.endswith('.pdf'):
                try:
                    print(f"Processing {filename}...")
                    chunks = self.process_single_file(filename)
                    
                    if chunks:
                        all_chunks.extend(chunks)
                        
                        # Save individual file chunks
                        output_file = os.path.join(
                            self.output_dir, 
                            f"{filename.replace('.pdf', '_chunks.json')}"
                        )
                        with open(output_file, 'w') as f:
                            json.dump(chunks, f, indent=2)
                        
                        # Collect keyword statistics
                        for chunk in chunks:
                            for category_group, categories in chunk['keyword_analysis'].items():
                                for category, findings in categories.items():
                                    keyword_stats[category_group][category] += len(findings)
                        
                        processing_stats['successful_files'] += 1
                        processing_stats['total_chunks'] += len(chunks)
                    else:
                        processing_stats['failed_files'] += 1
                        
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
                    processing_stats['failed_files'] += 1
        
        if all_chunks:
            # Calculate similarities
            print("Calculating similarities between chunks...")
            texts = [chunk['content'] for chunk in all_chunks]
            tfidf_matrix = self.tfidf.fit_transform(texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
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
            
            # Save results
            print("Saving processed data...")
            with open(os.path.join(self.output_dir, 'all_chunks.json'), 'w') as f:
                json.dump(all_chunks, f, indent=2)
            
            with open(os.path.join(self.output_dir, 'similarities.json'), 'w') as f:
                json.dump(similarities, f, indent=2)
        
        # Save processing statistics with keyword analysis
        stats = {
            'processing_stats': {
                'total_files': processing_stats['successful_files'] + processing_stats['failed_files'],
                'successful_files': processing_stats['successful_files'],
                'failed_files': processing_stats['failed_files'],
                'total_chunks': processing_stats['total_chunks']
            },
            'keyword_stats': keyword_stats
        }
        
        with open(os.path.join(self.output_dir, 'processing_stats.json'), 'w') as f:
            json.dump(stats, f, indent=2)
        
        print("\nProcessing Summary:")
        print(f"Successfully processed: {processing_stats['successful_files']} files")
        print(f"Failed to process: {processing_stats['failed_files']} files")
        print(f"Total chunks created: {processing_stats['total_chunks']}")
        print("\nKeyword Statistics:")
        for category_group, categories in keyword_stats.items():
            print(f"\n{category_group}:")
            for category, count in categories.items():
                print(f"  - {category}: {count} mentions")
        print(f"\nOutput saved to: {self.output_dir}")
        
        # Create a detailed analysis report
        report_content = f"""
# Financial Report Analysis Summary
Generated on: {datetime.now().isoformat()}

## Processing Statistics
- Total Files Processed: {processing_stats['successful_files'] + processing_stats['failed_files']}
- Successfully Processed: {processing_stats['successful_files']}
- Failed to Process: {processing_stats['failed_files']}
- Total Chunks Created: {processing_stats['total_chunks']}

## Keyword Analysis Summary
"""
        for category_group, categories in keyword_stats.items():
            report_content += f"\n### {category_group}\n"
            for category, count in categories.items():
                report_content += f"- {category}: {count} mentions\n"
        
        report_content += """
## Output Files
- all_chunks.json: Contains all processed text chunks with keyword analysis
- similarities.json: Cross-reference index of similar chunks
- processing_stats.json: Detailed processing statistics
- Individual JSON files for each processed document

## Keyword Categories Analyzed
1. FINANCIAL_METRICS
   - Revenue terms
   - Profitability
   - Balance sheet
   - Cash flow

2. COMPANY_STATE
   - Financial health
   - Growth indicators
   - Operational efficiency
   - Market position

3. RISK_FACTORS
   - Operational risks
   - Financial risks
   - Strategic risks

4. BUSINESS_OUTLOOK
   - Future prospects
   - Challenges
   - Strategic initiatives

## Usage Instructions
The processed data can be used for:
1. Financial analysis and trends identification
2. Risk assessment and monitoring
3. Performance comparison across companies
4. Strategic planning and market analysis
5. Automated report generation
"""
        
        # Save the analysis report
        with open(os.path.join(self.output_dir, 'analysis_report.md'), 'w') as f:
            f.write(report_content)

# Example usage
if __name__ == "__main__":
    processor = EnhancedFinancialReportProcessor(
        input_dir="data/raw/reports",
        output_dir="data/raw_processed"
    )
    processor.process_all_files()