import os
import faiss
import json
import uuid
import sys
import argparse
import datetime
import pandas as pd
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_index(is_demo: bool = False):
    logger.info("Starting RAG index build process...")
    
    if is_demo:
        logger.warning("DEMO/DUMMY DATA — NOT FOR PRODUCTION")
        
    model_name = os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    rag_dir = os.path.join(os.getcwd(), "backend", "data", "rag")
    os.makedirs(rag_dir, exist_ok=True)
    
    docs_file = os.path.join(rag_dir, "documents.jsonl")
    index_file = os.path.join(rag_dir, "index.faiss")
    manifest_file = os.path.join(rag_dir, "manifest.json")
    
    occupations_path = os.path.join(os.getcwd(), "data", "processed", "prism_education_career", "occupations.csv")
    skills_path = os.path.join(os.getcwd(), "data", "processed", "prism_education_career", "skills.csv")
    education_path = os.path.join(os.getcwd(), "data", "processed", "prism_education_career", "education_pathways.csv")
    progression_path = os.path.join(os.getcwd(), "data", "processed", "prism_education_career", "career_progression.csv")
    market_path = os.path.join(os.getcwd(), "data", "processed", "prism_india_jobs", "india_job_market_2024_2026.csv")
    
    documents = []
    
    def process_csv(path, doc_type, title_col, text_cols, source_label, synthetic=False):
        if not os.path.exists(path):
            logger.warning(f"File not found: {path}")
            return 0
        df = pd.read_csv(path)
        count = 0
        for _, row in df.iterrows():
            doc_id = str(uuid.uuid4())
            title = str(row.get(title_col, f"Unknown {doc_type}"))
            text_parts = []
            for col in text_cols:
                if col in row and pd.notna(row[col]):
                    text_parts.append(f"{col}: {row[col]}")
            text = f"{doc_type.capitalize()}: {title}\n" + "\n".join(text_parts)
            
            meta = {"source": source_label, "file": os.path.basename(path)}
            if synthetic:
                meta["status"] = "SYNTHETIC_PROTOTYPE"
                
            documents.append({
                "doc_id": doc_id,
                "doc_type": doc_type,
                "title": title,
                "text": text,
                "metadata": meta
            })
            count += 1
        return count

    occ_count = process_csv(occupations_path, "occupation", "occupation_name", ["occupation_category", "industry", "career_family", "future_growth_category", "primary_indian_hubs"], "prism_education_career")
    skill_count = process_csv(skills_path, "skill", "skill_name", ["skill_category", "description"], "prism_education_career")
    edu_count = process_csv(education_path, "education_pathway", "degree", ["field_of_study", "specialization", "education_stream", "common_indian_degree", "common_indian_exam_route"], "prism_education_career")
    prog_count = process_csv(progression_path, "career_progression", "progression_id", ["from_occupation_id", "to_occupation_id", "transition_type", "difficulty_level", "typical_time_years"], "prism_education_career")
    market_count = process_csv(market_path, "market_signal", "Job_Title", ["Company", "Industry", "City", "Salary_LPA", "Skills_Required"], "prism_india_jobs", synthetic=True)

    if not is_demo and occ_count == 0 and skill_count == 0:
        logger.error("FATAL: Required canonical GoGuide data (occupations/skills) not found.")
        logger.error("Paths checked: " + occupations_path + ", " + skills_path)
        sys.exit(1)

    if is_demo and len(documents) == 0:
        for i in range(10):
            documents.append({
                "doc_id": str(uuid.uuid4()),
                "doc_type": "occupation",
                "title": f"Mock Occupation {i}",
                "text": f"This is a mock occupation {i} description.",
                "metadata": {"source": "mock", "status": "SYNTHETIC_PROTOTYPE"}
            })
        for i in range(5):
            documents.append({
                "doc_id": str(uuid.uuid4()),
                "doc_type": "market_signal",
                "title": f"Market Signal {i}",
                "text": f"High demand for Mock Occupation {i} in India.",
                "metadata": {"source": "prism_india_jobs", "status": "SYNTHETIC_PROTOTYPE"}
            })
            
    if len(documents) == 0:
        logger.error("FATAL: Zero documents generated.")
        sys.exit(1)
        
    logger.info(f"Generated {len(documents)} semantic documents. Loading embedding model: {model_name}...")
    model = SentenceTransformer(model_name)
    texts = [d["text"] for d in documents]
    embeddings = model.encode(texts)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    
    logger.info("Saving index and documents...")
    faiss.write_index(index, index_file)
    with open(docs_file, "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc) + "\n")
            
    manifest = {
        "embedding_model": model_name,
        "document_count": len(documents),
        "creation_timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "index_version": "1.0",
        "schema_version": "1.0",
        "is_demo": is_demo
    }
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print("\n===========================================")
    if is_demo:
        print("DEMO/DUMMY DATA — NOT FOR PRODUCTION")
    print("RAG build complete")
    print(f"Total documents: {len(documents)}")
    print(f"Occupations: {len([d for d in documents if d['doc_type'] == 'occupation'])} (Source: {occupations_path})")
    print(f"Skills: {len([d for d in documents if d['doc_type'] == 'skill'])} (Source: {skills_path})")
    print(f"Education pathways: {len([d for d in documents if d['doc_type'] == 'education_pathway'])} (Source: {education_path})")
    print(f"Progression signals: {len([d for d in documents if d['doc_type'] == 'career_progression'])} (Source: {progression_path})")
    print(f"Market signals: {len([d for d in documents if d['doc_type'] == 'market_signal'])} (Source: {market_path})")
    print(f"Index: {index_file}")
    print(f"Embedding model: {model_name}")
    print("===========================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Use demo dummy data if real data is absent")
    args = parser.parse_args()
    build_index(args.demo)
