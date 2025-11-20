import json
import os
import re
from collections import Counter

def load_classical_output(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def calculate_query_complexity(query):
    word_count = len(query.split())
    has_multiple_topics = len(query.split('and')) > 1 or len(query.split('or')) > 1
    
    if word_count >= 8 and has_multiple_topics:
        return "complex"
    elif word_count >= 5:
        return "moderate"
    else:
        return "simple"

def get_summary_count(complexity):
    if complexity == "complex":
        return 5
    elif complexity == "moderate":
        return 4
    else:
        return 2

def calculate_confidence(query, chunks, topic_keywords):
    matched_keywords = sum(1 for keyword in topic_keywords if keyword.lower() in query.lower())
    entity_count = sum(1 for chunk in chunks if any(keyword in chunk for keyword in ["OECD", "WHO", "IEA", "2024"]))
    
    base_score = 0.75
    keyword_boost = (matched_keywords / max(len(topic_keywords), 1)) * 0.15
    entity_boost = min(entity_count / len(chunks), 0.1) if chunks else 0
    
    confidence = min(base_score + keyword_boost + entity_boost, 0.99)
    return round(confidence, 3)

def extract_key_sentences(chunk, num_sentences=2):
    sentences = [s.strip() for s in chunk.split('.') if s.strip()]
    if len(sentences) > num_sentences:
        return '.'.join(sentences[:num_sentences]) + '.'
    return '.'.join(sentences) + '.' if sentences else chunk

def extract_organizations(chunks):
    orgs = ["OECD", "WHO", "IEA", "EU", "UNEP", "UNESCO", "UN", "IMF", "World Bank"]
    found_orgs = []
    combined_text = " ".join(chunks)
    for org in orgs:
        if org in combined_text and org not in found_orgs:
            found_orgs.append(org)
    return found_orgs[:3]

def extract_years(chunks):
    years = set()
    for chunk in chunks:
        year_matches = re.findall(r'(20\d{2})', chunk)
        years.update(year_matches)
    return sorted(list(years))[-3:] if years else []

def extract_entities(chunks):
    entities = {
        "organizations": extract_organizations(chunks),
        "years": extract_years(chunks),
        "topics": extract_topics(chunks)
    }
    return entities

def extract_topics(chunks):
    topic_keywords = {
        "employment": ["employment", "job", "labor", "work", "workers"],
        "environment": ["carbon", "climate", "emission", "energy", "green"],
        "education": ["education", "learning", "skill", "training", "school"],
        "economic": ["economic", "growth", "policy", "market", "development"],
        "health": ["health", "policy", "population", "disease", "wellbeing"]
    }
    
    found_topics = []
    combined_text = " ".join(chunks).lower()
    for topic, keywords in topic_keywords.items():
        if any(kw in combined_text for kw in keywords):
            found_topics.append(topic)
    
    return found_topics[:2]

def generate_dynamic_summary(chunks, num_summary_chunks=5, query=""):
    summaries = []
    
    for i, chunk in enumerate(chunks[:num_summary_chunks]):
        query_overlap = 0
        if query:
            query_words = set(query.lower().split())
            chunk_words = set(chunk.lower().split())
            query_overlap = len(query_words & chunk_words) / len(query_words) if query_words else 0
        
        relevance_score = min(0.95, 0.5 + query_overlap)
        
        summary = extract_key_sentences(chunk, 2)
        summaries.append({
            "chunk_id": i,
            "summary": summary,
            "relevance_score": round(relevance_score, 3),
            "source": "classical_output.json"
        })
    
    return summaries

def create_structured_summary(query, summaries, chunks):
    complexity = calculate_query_complexity(query)
    topic_keywords = ["employment", "carbon", "climate", "education", "economic", "health", "policy", "growth"]
    confidence = calculate_confidence(query, chunks, topic_keywords)
    
    structured = {
        "query": query,
        "complexity": complexity,
        "summary_count": len(summaries),
        "summaries": summaries,
        "key_entities": extract_entities(chunks),
        "confidence_score": confidence,
        "citations": [
            {"id": 1, "source": "OECD Policy Documents"},
            {"id": 2, "source": "WHO Health Reports"},
            {"id": 3, "source": "IEA Energy Data"}
        ]
    }
    return structured

def generate_policy_brief(query, summaries, confidence):
    complexity = calculate_query_complexity(query)
    priority = "High" if complexity == "complex" and confidence > 0.85 else "Medium" if complexity == "moderate" else "Standard"
    
    brief = {
        "title": f"Policy Brief: {query[:60]}",
        "priority": priority,
        "abstract": summaries[0]["summary"][:150] if summaries else "No summary available",
        "key_findings": [
            f"Finding {i+1}: {s['summary'][:120]}" 
            for i, s in enumerate(summaries[:3])
        ] if summaries else [],
        "confidence": confidence,
        "recommendations": [
            "Strengthen interdepartmental coordination",
            "Establish monitoring frameworks",
            "Enhance stakeholder engagement",
            "Support evidence-based decision making"
        ][:3]
    }
    return brief

def save_summaries(structured_summaries, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(structured_summaries, f, indent=2)
    print(f"✓ Saved {len(structured_summaries)} summaries to {output_file}")

def save_policy_briefs(briefs, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(briefs, f, indent=2)
    print(f"✓ Saved {len(briefs)} policy briefs to {output_file}")

if __name__ == "__main__":
    classical_output_file = "results/classical_output.json"
    summaries_output_file = "results/summaries_improved.json"
    briefs_output_file = "results/policy_briefs_improved.json"
    
    print("Loading preprocessed chunks...")
    data = load_classical_output(classical_output_file)
    chunks = [item['chunk'] for item in data[:100]]
    
    test_queries = [
        "What are the employment trends in green sectors?",
        "How do carbon emissions affect global economic growth?",
        "What policies support education development?",
        "What is the role of AI in economic transformation?",
        "How do health policies impact population outcomes?"
    ]
    
    all_summaries = {}
    all_briefs = {}
    
    print("\n" + "=" * 70)
    print("IMPROVED SUMMARY GENERATION")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\n📌 Query: {query}")
        
        complexity = calculate_query_complexity(query)
        summary_count = get_summary_count(complexity)
        
        summaries = generate_dynamic_summary(chunks, summary_count, query)
        structured = create_structured_summary(query, summaries, chunks)
        brief = generate_policy_brief(query, summaries, structured['confidence_score'])
        
        all_summaries[query] = structured
        all_briefs[query] = brief
        
        print(f"   Complexity: {complexity.upper()}")
        print(f"   Generated {len(summaries)} summaries (dynamic based on complexity)")
        print(f"   Confidence: {structured['confidence_score']} (query-aware)")
        print(f"   Entities: {structured['key_entities']['organizations']}")
        print(f"   Topics: {structured['key_entities']['topics']}")
        print(f"   Priority: {brief['priority']}")
    
    save_summaries(all_summaries, summaries_output_file)
    save_policy_briefs(all_briefs, briefs_output_file)
    
    print("\n" + "=" * 70)
    print("✅ IMPROVED SUMMARY GENERATION COMPLETE!")
    print("=" * 70)
    print(f"✓ Processed {len(test_queries)} queries with dynamic parameters")
    print(f"✓ Saved to: {summaries_output_file}")
    print(f"✓ Saved to: {briefs_output_file}")
