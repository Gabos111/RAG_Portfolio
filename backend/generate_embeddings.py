import os
import json
import pandas as pd
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import torch

class EmbeddingsGenerator:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize the embeddings generator."""
        self.model_name = model_name
        # Check if CUDA (GPU) is available
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")
        
        # Load the model
        print(f"Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model.to(self.device)

    def load_chunks(self, file_path):
        """Load chunks from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            print(f"Loaded {len(chunks)} chunks from {file_path}")
            return chunks
        except Exception as e:
            print(f"Error loading chunks: {e}")
            return []

    def generate_embeddings(self, texts, batch_size=32):
        """Generate embeddings for the given texts."""
        embeddings = []
        
        try:
            for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
                # Get batch of texts
                batch_texts = texts[i:i+batch_size]
                
                # Generate embeddings for batch
                with torch.no_grad():  # Disable gradient calculation for inference
                    batch_embeddings = self.model.encode(
                        batch_texts,
                        show_progress_bar=False,
                        convert_to_tensor=True,
                        device=self.device
                    )
                    
                # Convert to numpy and add to list
                batch_embeddings = batch_embeddings.cpu().numpy()
                embeddings.extend(batch_embeddings.tolist())
                
                # Optional: Clear CUDA cache periodically
                if self.device == 'cuda' and i % (batch_size * 10) == 0:
                    torch.cuda.empty_cache()
                    
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            
        return embeddings

    def process_chunks(self, input_file, output_file):
        """Process chunks and generate embeddings."""
        # Load chunks
        chunks = self.load_chunks(input_file)
        if not chunks:
            return
        
        # Extract texts
        texts = [chunk['content'] for chunk in chunks]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.generate_embeddings(texts)
        
        # Verify results
        if len(embeddings) != len(chunks):
            print(f"Warning: Mismatch between embeddings ({len(embeddings)}) and chunks ({len(chunks)})")
            return
        
        # Create DataFrame
        df = pd.DataFrame(chunks)
        df['embedding'] = embeddings
        
        # Save results
        print(f"Saving results to {output_file}")
        df.to_pickle(output_file)
        
        # Print embedding information
        print("\nEmbedding Information:")
        print(f"Embedding dimension: {len(embeddings[0])}")
        print(f"Total embeddings: {len(embeddings)}")
        
        # Optional: Save a sample of embeddings in readable format
        sample_file = output_file.replace('.pkl', '_sample.json')
        sample_data = {
            'model_name': self.model_name,
            'embedding_dimension': len(embeddings[0]),
            'sample_chunks': []
        }
        
        for i in range(min(3, len(chunks))):
            sample_data['sample_chunks'].append({
                'content': chunks[i]['content'][:200] + '...',  # First 200 chars
                'embedding_preview': embeddings[i][:5] + ['...']  # First 5 dimensions
            })
            
        with open(sample_file, 'w') as f:
            json.dump(sample_data, f, indent=2)
        print(f"Sample data saved to {sample_file}")

def main():
    # Setup paths
    input_file = os.path.join('data', 'raw_processed', 'all_chunks.json')
    output_file = os.path.join('data', 'processed', 'chunks_with_embeddings.pkl')
    
    # Create generator
    generator = EmbeddingsGenerator()
    
    # Process chunks
    generator.process_chunks(input_file, output_file)

if __name__ == '__main__':
    main()