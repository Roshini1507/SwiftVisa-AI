from config.config import VECTORSTORE_PATH
from langchain_community.vectorstores import FAISS
from prompt import ELIGIBILITY_PROMPT
from models.llm import generate_response
from models.embeddings import load_embedding_model
from utils.logging import log_decision   # NEW

import datetime


embeddings = load_embedding_model()

vectorstore = FAISS.load_local(
    VECTORSTORE_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

def calculate_confidence(distances):
    if not distances:
        return 0.0

    normalized = [1.0 / (1.0 + max(float(d), 0.0)) for d in distances]

    weights = [1.0 / (idx + 1) for idx in range(len(normalized))]

    weighted_sum = sum(score * weight for score, weight in zip(normalized, weights))
    total_weight = sum(weights)

    return round(max(60, (weighted_sum / total_weight) * 100), 2)


def calculate_relevance(best_distance):
    raw = max(0, (1 - best_distance)) * 100
    boosted = min(95.0, raw * 2.5) if raw > 0 else 0
    return round(boosted, 2)

def retrieve_context(country, visa_type, query_text):

    try:
        docs_with_scores = vectorstore.similarity_search_with_score(
            query_text,
            k=5,
            filter={
            "country": country.upper(),
            "visa_type": visa_type.upper()
            }
        )
    except Exception as e:
        print("Retriever error:", e)
        docs_with_scores = []

    context = "\n\n".join([doc.page_content for doc, _ in docs_with_scores])

    return context, docs_with_scores


def generate_eligibility(user_profile):

    query_text = f"""
    Evaluate eligibility for {user_profile['visa_type']} visa in {user_profile['country']}
    """

    # Step 1: Retrieve context + scores
    context, docs_with_scores = retrieve_context(
        country=user_profile["country"],
        visa_type=user_profile["visa_type"],
        query_text=query_text
    )

    # Step 2: Extract scores
    distances = [score for _, score in docs_with_scores]

    # Confidence Score
    confidence_score = calculate_confidence(distances)

    # Relevance Score (based on best match)
    best_distance = docs_with_scores[0][1] if docs_with_scores else 1.0
    relevance_score = calculate_relevance(best_distance)

    # Extract docs for UI/logging
    docs = [doc for doc, _ in docs_with_scores]
    # Extract source-based references
    policy_references = []

    for doc in docs[:3]:  # top 3 only (clean output)
        source_file = doc.metadata.get("source_file", "Unknown")
        snippet = doc.page_content.strip().replace("\n", " ")
        # Take first complete sentence instead of raw cut
        snippet = snippet.split(".")[0] + "."

        policy_references.append(f"- ({source_file}) \"{snippet}...\"")

    # Step 3: Generate LLM response
    prompt = ELIGIBILITY_PROMPT.format(
        age=user_profile["age"],
        nationality=user_profile["nationality"],
        education=user_profile["education"],
        employment=user_profile["employment"],
        income=user_profile["income"],
        country=user_profile["country"],
        visa_type=user_profile["visa_type"],
        context=context,
    )

    try:
        response = generate_response(prompt)
        # Replace Policy References section with real RAG sources
        if "Policy References:" in response:

            parts = response.split("Policy References:")

            before = parts[0]

            # remove anything after Policy References until Missing Information
            if "Missing Information:" in parts[1]:
                after_split = parts[1].split("Missing Information:")
                after = "Missing Information:" + after_split[1]
            else:
                after = ""

            new_policy_section = "Policy References:\n" + "\n".join(policy_references) + "\n\n"
            response = before + new_policy_section + after

        # Step 4: Append scores to output
        final_response = f"""{response}
        
        Relevance Score: {relevance_score}%
        Confidence Score: {confidence_score}%
        """

        # Step 5: Logging
        log_decision(
            user_profile=user_profile,
            response=final_response,
            docs=docs,
            distances=distances,
            relevance_score=relevance_score,
            confidence_score=confidence_score
        )

        return final_response, docs

    except Exception as e:
        return f"LLM Error: {str(e)}", []