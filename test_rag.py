from utils.rag import generate_eligibility

user_profile = {
    "age": 25,
    "nationality": "India",
    "education": "Bachelor's Degree in Computer Science",
    "employment": "Software Engineer",
    "income": 75000,
    "country": "USA",
    "visa_type": "h1b"
}

response, docs = generate_eligibility(user_profile)

print(response)