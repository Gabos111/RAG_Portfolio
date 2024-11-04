# src/build_vector_db.py

import os
import faiss
import numpy as np
import pandas as pd

def main():
    # Paths
    embeddings_file = os.path.join('data', 'processed', 'chunks_with_embeddings.pkl')
    index_file = os.path.join('data', 'processed', 'faiss_index.bin')
    metadata_file = os.path.join('data', 'processed', 'chunks_metadata.pkl')

    # Load DataFrame
    print("Loading embeddings DataFrame...")
    df = pd.read_pickle(embeddings_file)

    # Prepare embeddings matrix
    print("Preparing embeddings matrix...")
    embedding_matrix = np.vstack(df['embedding'].values).astype('float32')

    # Normalize embeddings for cosine similarity
    print("Normalizing embeddings...")
    faiss.normalize_L2(embedding_matrix)

    # Create FAISS index (Inner Product for cosine similarity)
    print("Creating FAISS index...")
    dimension = embedding_matrix.shape[1]
    index = faiss.IndexFlatIP(dimension)

    # Add embeddings to the index
    print("Adding embeddings to the index...")
    index.add(embedding_matrix)

    # Save the index
    print(f"Saving FAISS index to {index_file}...")
    faiss.write_index(index, index_file)

    # Save metadata
    print(f"Saving metadata to {metadata_file}...")
    df.drop(columns=['embedding'], inplace=True)
    df.to_pickle(metadata_file)

    print("Vector database built and metadata saved successfully.")

if __name__ == '__main__':
    main()
