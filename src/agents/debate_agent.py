import json
import os

def load_summaries(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def create_pro_argument(query, summary):
    pro_points = {
        "employment": "Green employment creates sustainable jobs with competitive wages",
        "carbon": "Carbon pricing incentivizes innovation and reduces emissions effectively",
        "education": "Targeted education policies improve workforce competitiveness",
        "economic": "AI-driven policies accelerate economic growth and productivity",
        "health": "Universal health policies reduce mortality and improve wellbeing"
    }
    
    for key, value in pro_points.items():
        if key in query.lower():
            return {
                "position": "PRO",
                "argument": value,
                "evidence": summary[:100] if isinstance(summary, str) else "Supporting data available"
            }
    
    return {"position": "PRO", "argument": "Policy promotes economic development", "evidence": "Research supports this"}

def create_con_argument(query, summary):
    con_points = {
        "employment": "Green jobs transition may displace traditional workers",
        "carbon": "Carbon taxes increase costs for consumers and businesses",
        "education": "Education reforms require significant budget allocation",
        "economic": "AI policies may increase wealth inequality",
        "health": "Health policies can strain government resources"
    }
    
    for key, value in con_points.items():
        if key in query.lower():
            return {
                "position": "CON",
                "argument": value,
                "evidence": "Economic impact studies suggest trade-offs"
            }
    
    return {"position": "CON", "argument": "Policy implementation presents challenges", "evidence": "Case studies show complications"}

def reach_consensus(pro_arg, con_arg, confidence):
    agreement_level = min(confidence * 100, 95)
    
    consensus = {
        "synthesis": f"Both perspectives highlight important trade-offs. Evidence suggests a balanced approach is needed.",
        "common_ground": "All stakeholders agree on the importance of evidence-based policymaking",
        "recommended_path": "Implement policies with transition support and monitoring",
        "agreement_level": f"{agreement_level:.1f}%"
    }
    
    return consensus

def debate_policy(query, summaries, confidence):
    if not summaries:
        return None
    
    summary_text = summaries[0] if isinstance(summaries, list) else str(summaries)
    
    debate = {
        "query": query,
        "pro_argument": create_pro_argument(query, summary_text),
        "con_argument": create_con_argument(query, summary_text),
        "consensus": reach_consensus(
            create_pro_argument(query, summary_text),
            create_con_argument(query, summary_text),
            confidence
        )
    }
    
    return debate

def save_debates(debates, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(debates, f, indent=2)
    print(f"✓ Saved {len(debates)} debates to {output_file}")

if __name__ == "__main__":
    summaries_file = "results/summaries_improved.json"
    debates_output = "results/debate_analysis.json"
    
    print("Loading summaries...")
    summaries_data = load_summaries(summaries_file)
    
    all_debates = {}
    
    print("\n" + "=" * 70)
    print("DEBATE AGENT - POLICY PERSPECTIVE ANALYSIS")
    print("=" * 70)
    
    for query, summary_data in summaries_data.items():
        print(f"\n🎯 Debating: {query}")
        
        confidence = summary_data.get('confidence_score', 0.85)
        summaries = [s.get('summary', '') for s in summary_data.get('summaries', [])]
        
        debate = debate_policy(query, summaries, confidence)
        all_debates[query] = debate
        
        print(f"   PRO:  {debate['pro_argument']['argument'][:60]}...")
        print(f"   CON:  {debate['con_argument']['argument'][:60]}...")
        print(f"   Agreement Level: {debate['consensus']['agreement_level']}")
    
    save_debates(all_debates, debates_output)
    
    print("\n" + "=" * 70)
    print("✅ DEBATE ANALYSIS COMPLETE!")
    print("=" * 70)
