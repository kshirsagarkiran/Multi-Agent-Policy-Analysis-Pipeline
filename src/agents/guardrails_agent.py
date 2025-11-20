import json
import os
import re

def load_validation_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def redact_pii(text):
    if not text:
        return text
    
    redacted = text
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    redacted = re.sub(email_pattern, '[EMAIL_REDACTED]', redacted)
    
    phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
    redacted = re.sub(phone_pattern, '[PHONE_REDACTED]', redacted)
    
    ssn_pattern = r'\b(?:\d{3}-\d{2}-\d{4}|\d{9})\b'
    redacted = re.sub(ssn_pattern, '[SSN_REDACTED]', redacted)
    
    ip_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    redacted = re.sub(ip_pattern, '[IP_REDACTED]', redacted)
    
    return redacted

def filter_sensitive_queries(query):
    sensitive_keywords = ["password", "credit card", "ssn", "secret", "private key"]
    
    is_sensitive = any(keyword in query.lower() for keyword in sensitive_keywords)
    
    filter_score = 0.95 if not is_sensitive else 0.40
    
    return {
        "is_sensitive": is_sensitive,
        "filter_score": filter_score,
        "action": "BLOCK" if is_sensitive else "ALLOW"
    }

def check_bias(text):
    bias_indicators = {
        "positive_bias": ["excellent", "outstanding", "perfect"],
        "negative_bias": ["terrible", "worthless", "useless"],
        "language_bias": ["obviously", "clearly", "everyone knows"]
    }
    
    bias_score = 1.0
    detected_biases = []
    
    for bias_type, keywords in bias_indicators.items():
        if any(keyword in text.lower() for keyword in keywords):
            bias_score -= 0.15
            detected_biases.append(bias_type)
    
    return {
        "bias_score": max(bias_score, 0.5),
        "detected_biases": detected_biases,
        "bias_level": "LOW" if bias_score > 0.8 else "MEDIUM" if bias_score > 0.6 else "HIGH"
    }

def apply_guardrails(query, data):
    guardrails_report = {
        "original_query": query,
        "pii_check": {
            "original": query,
            "redacted": redact_pii(query),
            "pii_found": query != redact_pii(query)
        },
        "sensitivity_filter": filter_sensitive_queries(query),
        "bias_analysis": check_bias(query),
        "safety_score": 0.95
    }
    
    if guardrails_report['pii_check']['pii_found']:
        guardrails_report['safety_score'] -= 0.10
    
    if guardrails_report['sensitivity_filter']['is_sensitive']:
        guardrails_report['safety_score'] -= 0.20
    
    if guardrails_report['bias_analysis']['bias_score'] < 0.7:
        guardrails_report['safety_score'] -= 0.15
    
    guardrails_report['safety_score'] = max(guardrails_report['safety_score'], 0.3)
    
    guardrails_report['recommendation'] = "APPROVED" if guardrails_report['safety_score'] > 0.80 else "REVIEW REQUIRED"
    
    return guardrails_report

def save_guardrails_report(reports, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(reports, f, indent=2)
    print(f"✓ Saved guardrails report to {output_file}")

if __name__ == "__main__":
    validation_file = "results/validation_metrics.json"
    guardrails_output = "results/guardrails_report.json"
    
    print("Loading validation metrics...")
    validation_data = load_validation_data(validation_file)
    
    test_queries = [
        "What are the employment trends in green sectors?",
        "How do carbon emissions affect global economic growth?",
        "What policies support education development?",
        "What is the role of AI in economic transformation?",
        "How do health policies impact population outcomes?"
    ]
    
    all_reports = {}
    
    print("\n" + "=" * 70)
    print("GUARDRAILS AGENT - SAFETY & PRIVACY PROTECTION")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\n🔒 Scanning: {query[:50]}...")
        
        guardrails = apply_guardrails(query, validation_data)
        all_reports[query] = guardrails
        
        print(f"   PII Found: {guardrails['pii_check']['pii_found']}")
        print(f"   Sensitivity: {guardrails['sensitivity_filter']['action']}")
        print(f"   Bias Level: {guardrails['bias_analysis']['bias_level']}")
        print(f"   Safety Score: {guardrails['safety_score']:.3f}")
        print(f"   Status: {guardrails['recommendation']}")
    
    save_guardrails_report(all_reports, guardrails_output)
    
    print("\n" + "=" * 70)
    print("✅ GUARDRAILS CHECK COMPLETE!")
    print("=" * 70)
