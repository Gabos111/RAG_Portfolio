# src/retrieve_and_answer.py

import os
import argparse
from backend.utils import (
    load_faiss_index,
    load_metadata,
    retrieve_relevant_chunks,
    construct_prompt,
    generate_answer
)

def retrieve_and_answer(query, top_k=10, model='gpt-3.5-turbo'):
    try:
        # Paths
        index_file = os.path.join('data', 'processed', 'faiss_index.bin')
        metadata_file = os.path.join('data', 'processed', 'chunks_metadata.pkl')

        # Load index and metadata
        print("Loading FAISS index and metadata...")
        index = load_faiss_index(index_file)
        df = load_metadata(metadata_file)

        # Retrieve relevant chunks
        print(f"\nRetrieving top {top_k} relevant chunks...")
        relevant_chunks = retrieve_relevant_chunks(query, df, index, top_k=top_k)

        # Construct prompt
        print("Constructing prompt...")
        prompt = construct_prompt(query, relevant_chunks)

        # Generate answer
        print(f"Generating answer using {model}...")
        answer = generate_answer(prompt, model=model)

        return answer

    except Exception as e:
        print(f"\nError in retrieve_and_answer: {e}")
        print("\nPlease make sure:")
        print("1. The FAISS index and metadata files exist")
        print("2. Your OpenAI API key is set correctly in .env")
        print("3. You have an active internet connection")
        return "An error occurred while processing your request."