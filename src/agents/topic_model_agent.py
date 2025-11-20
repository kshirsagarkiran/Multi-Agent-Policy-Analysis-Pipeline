import json
import os
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import numpy as np


def load_classical_output(file_path):
    """Load preprocessed chunks"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def extract_chunks(data):
    """Extract text chunks from data"""
    chunks = [item['chunk'] for item in data]
    return chunks


def create_overlapping_chunks(chunks, overlap_chars=200):
    """Create overlapping chunks with 200 character sliding window"""
    print(f"\n🔄 Creating overlapping chunks with {overlap_chars} character overlap...")
    
    combined_text = " ".join(chunks)
    overlapping_chunks = []
    
    # Calculate chunk size and step
    chunk_size = len(combined_text) // len(chunks) if len(chunks) > 0 else 1000
    step_size = chunk_size - overlap_chars
    
    if step_size <= 0:
        step_size = max(1, chunk_size // 2)
    
    # Create overlapping windows
    start = 0
    while start < len(combined_text):
        end = min(start + chunk_size, len(combined_text))
        overlapping_chunks.append(combined_text[start:end])
        start += step_size
    
    print(f"   ✓ Original chunks: {len(chunks)}")
    print(f"   ✓ Overlapping chunks: {len(overlapping_chunks)}")
    print(f"   ✓ Overlap size: {overlap_chars} chars")
    print(f"   ✓ Step size: {step_size} chars")
    print(f"   ✓ Avg chunk size: {chunk_size} chars")
    
    return overlapping_chunks


def perform_topic_modeling(chunks, n_topics=5):
    """Perform LDA topic modeling"""
    print(f"\n🧠 Performing topic modeling on {len(chunks)} chunks...")
    
    vectorizer = CountVectorizer(max_features=1000, stop_words='english', min_df=2)
    doc_term_matrix = vectorizer.fit_transform(chunks)
    
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=20)
    lda.fit(doc_term_matrix)
    
    topics = {}
    feature_names = vectorizer.get_feature_names_out()
    for topic_idx, topic in enumerate(lda.components_):
        top_words = [feature_names[i] for i in topic.argsort()[-10:]]
        topics[f"Topic_{topic_idx}"] = top_words
    
    print(f"   ✓ Extracted {n_topics} topics")
    return lda, vectorizer, topics, doc_term_matrix


def visualize_embeddings(doc_term_matrix, lda, chunks):
    """Visualize topic embeddings with t-SNE"""
    print("\n📈 Visualizing embeddings...")
    
    doc_embeddings = lda.transform(doc_term_matrix)
    
    # Adjust perplexity based on sample size
    perplexity = min(30, max(5, len(chunks) - 1))
    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
    tsne_embeddings = tsne.fit_transform(doc_embeddings)
    
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(tsne_embeddings[:, 0], tsne_embeddings[:, 1], 
                         c=doc_embeddings.argmax(axis=1), cmap='viridis', alpha=0.6, s=60)
    plt.colorbar(scatter, label='Topic')
    plt.title('Topic Distribution Visualization (t-SNE)')
    plt.xlabel('t-SNE 1')
    plt.ylabel('t-SNE 2')
    plt.grid(True, alpha=0.3)
    
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/embedding_map.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved embedding_map.png")
    plt.close()


def save_topics(topics, output_file):
    """Save topics to JSON"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(topics, f, indent=2)
    print(f"   ✓ Saved topics to {output_file}")


def save_overlap_config(overlap_chars, num_chunks, output_file):
    """Save overlap configuration and metadata"""
    config = {
        "overlap_configuration": {
            "overlap_characters": overlap_chars,
            "original_chunks": num_chunks,
            "method": "sliding_window_200_chars"
        }
    }
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"   ✓ Saved overlap config to {output_file}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔍 TOPIC MODELING WITH 200-CHARACTER CHUNK OVERLAP")
    print("="*70)
    
    classical_output_file = "results/classical_output.json"
    topics_output_file = "results/topics.json"
    config_output_file = "results/topic_modeling_config.json"
    
    # Load data
    print("\n📂 Loading preprocessed chunks...")
    data = load_classical_output(classical_output_file)
    chunks = extract_chunks(data)
    print(f"   ✓ Loaded {len(chunks)} chunks")
    
    # Create overlapping chunks with 200 character overlap
    overlapping_chunks = create_overlapping_chunks(chunks, overlap_chars=200)
    
    # Perform topic modeling
    lda, vectorizer, topics, doc_term_matrix = perform_topic_modeling(overlapping_chunks, n_topics=5)
    
    # Visualize embeddings
    visualize_embeddings(doc_term_matrix, lda, overlapping_chunks)
    
    # Save topics
    save_topics(topics, topics_output_file)
    
    # Save configuration
    save_overlap_config(200, len(chunks), config_output_file)
    
    print("\n" + "="*70)
    print("✅ TOPIC MODELING COMPLETE!")
    print("="*70)
    
    print("\n📋 Topics Extracted:")
    for topic_name, words in topics.items():
        print(f"   {topic_name}: {', '.join(words)}")
    
    print("\n📊 Output Files:")
    print("   ✓ results/topics.json")
    print("   ✓ results/embedding_map.png")
    print("   ✓ results/topic_modeling_config.json")
    
    print("\n" + "="*70)
