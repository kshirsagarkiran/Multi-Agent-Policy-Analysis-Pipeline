import json
import os
from datetime import datetime
from pathlib import Path

class MemoryAgent:
    """
    Advanced Memory Management Agent
    Tracks pipeline history, query patterns, and adaptive parameters
    """
    
    def __init__(self):
        self.memory_file = Path("results/memory_log.json")
        self.history_file = Path("results/query_history.json")
        self.params_file = Path("results/adaptive_parameters.json")
        self.load_or_initialize()
    
    def load_or_initialize(self):
        """Load existing memory or initialize new"""
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
        else:
            self.memory = {
                "created": datetime.now().isoformat(),
                "queries": [],
                "learned_patterns": [],
                "confidence_history": []
            }
    
    def store_query_result(self, query, result, confidence):
        """Store query execution result"""
        entry = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "confidence": confidence,
            "result_preview": str(result)[:100],
            "success": confidence > 0.80
        }
        self.memory["queries"].append(entry)
    
    def learn_patterns(self):
        """Extract patterns from historical queries"""
        if len(self.memory["queries"]) < 3:
            return []
        
        patterns = {
            "average_confidence": sum(q["confidence"] for q in self.memory["queries"]) / len(self.memory["queries"]),
            "success_rate": sum(1 for q in self.memory["queries"] if q["success"]) / len(self.memory["queries"]),
            "total_queries": len(self.memory["queries"]),
            "query_types": self.classify_queries()
        }
        return patterns
    
    def classify_queries(self):
        """Classify queries by type"""
        classification = {
            "employment": 0,
            "environment": 0,
            "education": 0,
            "economic": 0,
            "health": 0
        }
        
        keywords = {
            "employment": ["employment", "job", "work", "labor"],
            "environment": ["carbon", "climate", "emission", "energy"],
            "education": ["education", "learning", "skill"],
            "economic": ["economic", "growth", "policy"],
            "health": ["health", "policy", "population"]
        }
        
        for query_entry in self.memory["queries"]:
            query = query_entry["query"].lower()
            for category, keywords_list in keywords.items():
                if any(kw in query for kw in keywords_list):
                    classification[category] += 1
        
        return classification
    
    def adapt_parameters(self):
        """Adapt parameters based on learned patterns"""
        patterns = self.learn_patterns()
        
        if not patterns:
            base_alpha = 0.6
            base_chunk_size = 500
            base_summary_count = 3
        else:
            success_rate = patterns["success_rate"]
            
            # Adapt alpha (retrieval weight) based on success
            base_alpha = 0.5 + (success_rate * 0.3)
            
            # Adapt chunk size based on query complexity
            avg_confidence = patterns["average_confidence"]
            base_chunk_size = int(300 + (avg_confidence * 200))
            
            # Adapt summary count based on query types
            dominant_type = max(patterns["query_types"], key=patterns["query_types"].get)
            base_summary_count = 2 if dominant_type == "simple" else 4
        
        adaptive_params = {
            "alpha": round(base_alpha, 3),
            "chunk_size": base_chunk_size,
            "summary_count": base_summary_count,
            "learning_rate": 0.1,
            "confidence_threshold": 0.80,
            "timestamp": datetime.now().isoformat()
        }
        
        return adaptive_params
    
    def save_memory(self):
        """Save memory to disk"""
        os.makedirs("results", exist_ok=True)
        
        # Save memory log
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
        
        # Save learned patterns
        patterns = self.learn_patterns()
        with open(self.history_file, 'w') as f:
            json.dump(patterns, f, indent=2)
        
        # Save adaptive parameters
        adaptive_params = self.adapt_parameters()
        with open(self.params_file, 'w') as f:
            json.dump(adaptive_params, f, indent=2)
        
        print(f"✓ Memory saved: {self.memory_file}")
        print(f"✓ Patterns saved: {self.history_file}")
        print(f"✓ Parameters saved: {self.params_file}")

def main():
    """Main execution"""
    print("\n" + "="*70)
    print("💾 MEMORY AGENT - ADAPTIVE LEARNING & TRACKING")
    print("="*70)
    
    agent = MemoryAgent()
    
    # Simulate storing query results
    test_queries = [
        ("What are the employment trends in green sectors?", {"status": "success"}, 0.869),
        ("How do carbon emissions affect global economic growth?", {"status": "success"}, 0.906),
        ("What policies support education development?", {"status": "success"}, 0.869),
        ("What is the role of AI in economic transformation?", {"status": "success"}, 0.869),
        ("How do health policies impact population outcomes?", {"status": "success"}, 0.869)
    ]
    
    print("\n📝 Recording query results...")
    for query, result, confidence in test_queries:
        agent.store_query_result(query, result, confidence)
        print(f"  ✓ Stored: {query[:50]}... (confidence: {confidence})")
    
    print("\n🧠 Learning patterns from history...")
    patterns = agent.learn_patterns()
    print(f"  • Average Confidence: {patterns['average_confidence']:.3f}")
    print(f"  • Success Rate: {patterns['success_rate']:.1%}")
    print(f"  • Total Queries: {patterns['total_queries']}")
    print(f"  • Query Types: {patterns['query_types']}")
    
    print("\n⚙️  Adapting parameters based on learning...")
    params = agent.adapt_parameters()
    print(f"  • Alpha (retrieval weight): {params['alpha']}")
    print(f"  • Chunk Size: {params['chunk_size']}")
    print(f"  • Summary Count: {params['summary_count']}")
    print(f"  • Confidence Threshold: {params['confidence_threshold']}")
    
    print("\n💾 Saving memory artifacts...")
    agent.save_memory()
    
    print("\n" + "="*70)
    print("✅ MEMORY AGENT COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    main()
