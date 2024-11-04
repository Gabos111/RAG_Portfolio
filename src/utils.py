# src/utils.py

import os
import faiss
import numpy as np
import pandas as pd
import tiktoken
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Load the same embedding model used for chunk embeddings
embedding_model_name = 'all-MiniLM-L6-v2'
embedding_model = SentenceTransformer(embedding_model_name)

def load_faiss_index(index_file):
    """Load FAISS index from file."""
    index = faiss.read_index(index_file)
    return index

def load_metadata(metadata_file):
    """Load metadata DataFrame from file."""
    df = pd.read_pickle(metadata_file)
    return df

def get_query_embedding(query):
    """Generate embedding for the query using the same model."""
    embedding = embedding_model.encode([query], convert_to_numpy=True)
    # Normalize the embedding
    faiss.normalize_L2(embedding)
    return embedding.astype('float32')

def retrieve_relevant_chunks(query, df, index, top_k=10):
    """Retrieve top_k relevant chunks for a query."""
    query_embedding = get_query_embedding(query)
    distances, indices = index.search(query_embedding, top_k)
    results = df.iloc[indices[0]].copy()
    results['similarity'] = distances[0]
    return results

def construct_prompt(question, relevant_chunks, max_tokens=3000):
    """Construct the prompt for the LLM."""
    # Start building the prompt
    prompt = "You are an expert financial analyst. Answer the question based on the provided information.\n\n"
    prompt += f"Question: {question}\n\n"
    prompt += "Context:\n"

    # Tokenizer for counting tokens
    tokenizer = tiktoken.get_encoding('cl100k_base')

    token_count = len(tokenizer.encode(prompt))
    for idx, row in relevant_chunks.iterrows():
        chunk_text = row['content']
        source = row.get('source', 'Unknown source')
        tokens = len(tokenizer.encode(chunk_text))
        
        if token_count + tokens > max_tokens:
            break
            
        prompt += f"[{source}]: {chunk_text}\n\n"
        token_count += tokens

    prompt += (
        "\nInstructions:\n"
        "1. Base your answer solely on the provided context.\n"
        "2. If the context doesn't contain enough information, say so.\n"
        "3. Cite sources when possible.\n"
        "4. Provide detailed financial analysis when relevant.\n\n"
        "Answer: "
    )

    return prompt

def generate_answer(prompt, model="gpt-3.5-turbo", temperature=0, max_tokens=500):
    """Generate answer using OpenAI's API with the new client."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful financial analyst assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "Sorry, I encountered an error while generating the answer. Please try again."