# SwiftVisa: AI-Based Visa Eligibility Screening Chatbot
SwiftVisa AI is an intelligent visa eligibility assistant that analyzes immigration policies and evaluates visa eligibility using RAG and LLM reasoning  based on official immigration policy documents and real-time web information. The system uses a conversational chatbot interface to collect user information and determine visa eligibility using grounded policy reasoning.
## Project Overview
SwiftVisa is a Streamlit-based chatbot that helps users understand whether they may qualify for a specific visa category.
### Core Technologies:
```
Streamlit (UI)
RAG (Retrieval-Augmented Generation)
Vector Embeddings(Sentence Transformers)
FAISS Vector Database
LLM (Google Gemini)
LangChain(Orchestration)
[!IMPORTANT]Instead of hallucinating answers, the chatbot retrieves official immigration policies and uses them to generate grounded responses.
```
## Features
1. Conversational Chatbot Interface: The assistant collects user information through a chat conversation instead of static forms.
```
Assistant: What is your age?
User: 25
```
2. Retrieval-Augmented Generation (RAG): The chatbot retrieves relevant immigration policies from a vector database built from visa policy documents.
3. Metadata-Based Document Filtering: Documents are filtered using metadata (e.g., Country, Visa type) to improve retrieval accuracy.
4. Analysis Response 
Concise/Detailed : Status, Explanation, Confidence Score(0-100)%, Relevance Score(0-100)%
5. Policy Source Transparency:
Users can view the specific policy documents used to generate the answer, ensuring transparency and explainability.
## Project Architecture
The flow of data through SwiftVisa:
```
User
 ↓
Streamlit Chat Interface (SwiftVisa Agent)
 ↓
User Profile Extraction
 ↓
RAG Retrieval System
 ↓
FAISS Vector Database
 ↓
Visa Policy Knowledge Base (PDF policies)
 ↓
Web Search (Fallback if context is insufficient)
 ↓
Gemini LLM
 ↓
Eligibility Analysis
 ↓
Structured Response to User
```
## Project Structure
```
project/
│
├── config/
│   └── config.py
│
├── models/
│   ├── llm.py
│   └── embeddings.py
│
├── utils/
│   ├── rag.py
│   └── web_search.py
│
├── prompts/
│   └── prompt.py
│
├── scripts/
│   └── build_vectorstore.py
│
├── data/
│
├── vectorstore/
│
├── app.py
├── test_rag.py
└── requirements.txt
```
## Installation
1. Clone the repository
```bash
git clone https://github.com/Roshini1507/SwiftVisa-AI.git
cd swiftvisa-ai
```
2. Create virtual environment
```bash
python -m venv .venv
```
3. Activate environment
Windows: 
```bash 
.venv\Scripts\activate
```
macOS/Linux: 
```bash
source .venv/bin/activate
```
4. Install dependencies
```bash
pip install -r requirements.txt
```
5. Run
```bash
streamlit run app.py
```
## Live Demo

https://roshini1507-swiftvisa-ai--app-9wvlbz.streamlit.app/
