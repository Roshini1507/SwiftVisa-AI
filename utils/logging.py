import json
import os
from datetime import datetime

LOG_FILE = "logs/decision_log.json"


def log_decision(user_profile, response, docs, distances, relevance_score, confidence_score):

    os.makedirs("logs", exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "user_profile": user_profile,

        "response": response,

        # NEW: Scores
        "relevance_score": relevance_score,
        "confidence_score": confidence_score,

        # NEW: Raw retrieval distances
        "retrieval_distances": distances,

        # Sources
        "sources": [
            {
                "source_file": doc.metadata.get("source_file", "Unknown"),
                "country": doc.metadata.get("country", ""),
                "visa_type": doc.metadata.get("visa_type", ""),
                "content_preview": doc.page_content[:200]
            }
            for doc in docs
        ]
    }

    # Load existing logs
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                data = json.load(f)
            except:
                data = []
    else:
        data = []

    data.append(log_entry)

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4, default=str)