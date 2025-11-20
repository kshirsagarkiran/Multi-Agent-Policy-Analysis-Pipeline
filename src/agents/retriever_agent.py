import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def load_classical_output(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def extract_chunks(data):
    chunks = [item['chunk'] for item in data]
    return chunks

def build_bm25_index(chunks):
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', min_df=2)
    tfidf_matrix = vectorizer.fit_transform(chunks)
    return vectorizer, tfidf_matrix

def bm25_retrieval(query, vectorizer, tfidf_matrix, chunks, top_k=5):
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = scores.argsort()[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        results.append({
            "chunk": chunks[idx],
            "score": float(scores[idx]),
            "index": int(idx)
        })
    return results

def dense_retrieval_mock(query, chunks, top_k=5):
    query_words = set(query.lower().split())
    scores = []
    for chunk in chunks:
        chunk_words = set(chunk.lower().split())
        overlap = len(query_words & chunk_words)
        scores.append(overlap)
    
    scores = np.array(scores)
    top_indices = scores.argsort()[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        results.append({
            "chunk": chunks[idx],
            "score": float(scores[idx]),
            "index": int(idx)
        })
    return results

def hybrid_retrieval(query, vectorizer, tfidf_matrix, chunks, top_k=5, alpha=0.6):
    bm25_results = bm25_retrieval(query, vectorizer, tfidf_matrix, chunks, top_k)
    dense_results = dense_retrieval_mock(query, chunks, top_k)
    
    bm25_dict = {r['index']: r['score'] for r in bm25_results}
    dense_dict = {r['index']: r['score'] for r in dense_results}
    
    all_indices = set(bm25_dict.keys()) | set(dense_dict.keys())
    
    hybrid_scores = {}
    for idx in all_indices:
        bm25_score = bm25_dict.get(idx, 0)
        dense_score = dense_dict.get(idx, 0)
        hybrid_scores[idx] = alpha * bm25_score + (1 - alpha) * dense_score
    
    sorted_indices = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    results = []
    for idx, score in sorted_indices:
        results.append({
            "chunk": chunks[idx],
            "hybrid_score": float(score),
            "index": int(idx)
        })
    return results

def test_retrieval(vectorizer, tfidf_matrix, chunks):
    test_queries = [
        "employment and job market",
        "carbon emissions and climate",
        "education and skills development",
        "AI and economic growth",
        "health policy and data"
    ]
    
    results_summary = {}
    for query in test_queries:
        results = hybrid_retrieval(query, vectorizer, tfidf_matrix, chunks, top_k=3)
        results_summary[query] = results
    
    return results_summary

def save_retrieval_diagnostics(results_summary, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    diagnostics = {}
    for query, results in results_summary.items():
        diagnostics[query] = {
            "top_results": [
                {
                    "chunk_preview": r["chunk"][:100] + "...",
                    "score": r["hybrid_score"]
                }
                for r in results
            ]
        }
    
    with open(output_file, 'w') as f:
        json.dump(diagnostics, f, indent=2)
    
    print(f"Saved retrieval diagnostics to {output_file}")

if __name__ == "__main__":
    classical_output_file = "results/classical_output.json"
    diagnostics_output_file = "results/retrieval_diagnostics.json"
    
    print("Loading preprocessed chunks...")
    data = load_classical_output(classical_output_file)
    chunks = extract_chunks(data)
    
    print(f"Building BM25 index for {len(chunks)} chunks...")
    vectorizer, tfidf_matrix = build_bm25_index(chunks)
    
    print("Testing hybrid retrieval with sample queries...")
    results_summary = test_retrieval(vectorizer, tfidf_matrix, chunks)
    
    print("Saving retrieval diagnostics...")
    save_retrieval_diagnostics(results_summary, diagnostics_output_file)
    
    print("\nRetrieval Agent Complete!")
    print("Sample Query Results:")
    for query, results in results_summary.items():
        print(f"\nQuery: '{query}'")
        for i, result in enumerate(results, 1):
            print(f"  Result {i}: Score={result['hybrid_score']:.4f}")
            print(f"    Preview: {result['chunk'][:80]}...")
