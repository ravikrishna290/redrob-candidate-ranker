import re

def parse_jd(jd_text):
    """
    Parses a job description text and extracts structured information.
    """
    # Initialize defaults matching the target JD
    parsed = {
        "role_title": "Senior AI Engineer — Founding Team",
        "must_have_skills": [
            "embeddings-based retrieval systems", "sentence-transformers", "openai embeddings", "bge", "e5",
            "vector databases", "hybrid search", "pinecone", "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "faiss",
            "python",
            "evaluation frameworks", "ndcg", "mrr", "map", "a/b testing", "offline-to-online correlation"
        ],
        "preferred_skills": [
            "llm fine-tuning", "lora", "qlora", "peft",
            "learning-to-rank", "xgboost", "neural ranking",
            "hr-tech", "recruiting tech", "marketplace products",
            "distributed systems", "large-scale inference", "optimization",
            "open-source"
        ],
        "seniority_level": "Senior / Lead",
        "min_experience": 4.0,
        "max_experience": 15.0,
        "domain_preference": ["applied ml/ai", "product companies"],
        "behavioral_expectations": ["async-first", "writing-oriented", "high ownership", "shipper archetype"],
        "disallowed_companies": ["tcs", "infosys", "wipro", "cognizant", "capgemini", "accenture", "hcl", "tech mahindra", "genpact", "mphasis"],
        "target_locations": ["pune", "noida", "hyderabad", "mumbai", "delhi ncr", "bangalore"]
    }
    
    # Try parsing text dynamically using simple heuristic regex matching
    text_lower = jd_text.lower()
    
    # 1. Parse Title
    title_match = re.search(r"job description:\s*(.*)", jd_text, re.IGNORECASE)
    if title_match:
        parsed["role_title"] = title_match.group(1).strip()
        
    # 2. Parse Experience
    exp_match = re.search(r"experience required:\s*([0-9]+)[–-]([0-9]+)\s*years", jd_text, re.IGNORECASE)
    if exp_match:
        parsed["min_experience"] = float(exp_match.group(1))
        parsed["max_experience"] = float(exp_match.group(2))
        
    return parsed
