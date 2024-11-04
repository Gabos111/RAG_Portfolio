# src/retrieve_and_answer.py

import os
import argparse
from utils import (
    load_faiss_index,
    load_metadata,
    retrieve_relevant_chunks,
    construct_prompt,
    generate_answer
)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='RAG System Query')
    parser.add_argument('--query', type=str, required=True, help='User query')
    parser.add_argument('--top_k', type=int, default=10, help='Number of relevant chunks to retrieve')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo', help='OpenAI model to use')
    args = parser.parse_args()

    try:
        # Paths
        index_file = os.path.join('data', 'processed', 'faiss_index.bin')
        metadata_file = os.path.join('data', 'processed', 'chunks_metadata.pkl')

        # Load index and metadata
        print("Loading FAISS index and metadata...")
        index = load_faiss_index(index_file)
        df = load_metadata(metadata_file)

        # Retrieve relevant chunks
        print(f"\nRetrieving top {args.top_k} relevant chunks...")
        relevant_chunks = retrieve_relevant_chunks(args.query, df, index, top_k=args.top_k)

        # Construct prompt
        print("Constructing prompt...")
        prompt = construct_prompt(args.query, relevant_chunks)

        # Generate answer
        print(f"Generating answer using {args.model}...")
        answer = generate_answer(prompt, model=args.model)

        # Display the answer
        print("\nAnswer:")
        print("-" * 80)
        print(answer)
        print("-" * 80)

    except Exception as e:
        print(f"\nError: {e}")
        print("\nPlease make sure:")
        print("1. The FAISS index and metadata files exist")
        print("2. Your OpenAI API key is set correctly in .env")
        print("3. You have an active internet connection")

if __name__ == '__main__':
    main()