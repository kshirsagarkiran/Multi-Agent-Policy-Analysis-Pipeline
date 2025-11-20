import json
import os

def load_retrieval_results(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def decompose_query(query):
    sub_queries = []
    keywords = query.lower().split()
    
    if len(keywords) >= 2:
        for i in range(len(keywords)):
            sub_queries.append(" ".join(keywords[:i+1]))
    else:
        sub_queries.append(query)
    
    return sub_queries

def detect_query_language(query):
    if any(ord(char) > 127 for char in query):
        return "non-english"
    return "english"

def route_query(query, retrieval_data):
    language = detect_query_language(query)
    sub_queries = decompose_query(query)
    
    plan = {
        "original_query": query,
        "language": language,
        "sub_queries": sub_queries,
        "routing": [],
        "confidence": 0.85
    }
    
    if language == "english":
        if any(word in query.lower() for word in ["employment", "job", "work", "labor"]):
            plan["routing"].append("topic_0_employment")
        if any(word in query.lower() for word in ["carbon", "climate", "emission", "energy"]):
            plan["routing"].append("topic_3_environment")
        if any(word in query.lower() for word in ["education", "skill", "learning", "training"]):
            plan["routing"].append("topic_3_education")
        if any(word in query.lower() for word in ["ai", "artificial", "growth", "economic"]):
            plan["routing"].append("topic_4_economic")
        if any(word in query.lower() for word in ["health", "policy", "data", "who"]):
            plan["routing"].append("topic_2_health")
    
    if not plan["routing"]:
        plan["routing"].append("general")
    
    return plan

def create_query_plan(query):
    plan = {
        "query": query,
        "steps": [
            {"step": 1, "action": "detect_language", "status": "complete"},
            {"step": 2, "action": "decompose_query", "status": "complete"},
            {"step": 3, "action": "route_to_topics", "status": "complete"},
            {"step": 4, "action": "retrieve_relevant_chunks", "status": "pending"},
            {"step": 5, "action": "generate_summary", "status": "pending"}
        ]
    }
    return plan

def save_plan(plan, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(plan, f, indent=2)
    print(f"Saved query plan to {output_file}")

if __name__ == "__main__":
    test_queries = [
        "What are the employment trends in green sectors?",
        "How do carbon emissions affect global economic growth?",
        "What policies support education development?",
        "What is the role of AI in economic transformation?",
        "How do health policies impact population outcomes?"
    ]
    
    plans_output_file = "results/query_plans.json"
    all_plans = {}
    
    print("Planning Agent Started!")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nProcessing: {query}")
        routing = route_query(query, {})
        plan = create_query_plan(query)
        plan["routing"] = routing
        all_plans[query] = plan
        
        print(f"  Language: {routing['language']}")
        print(f"  Routes: {routing['routing']}")
        print(f"  Sub-queries: {routing['sub_queries'][:2]}...")
    
    save_plan(all_plans, plans_output_file)
    
    print("\n" + "=" * 60)
    print("Query Planning Complete!")
    print(f"Saved {len(all_plans)} query plans to {plans_output_file}")
