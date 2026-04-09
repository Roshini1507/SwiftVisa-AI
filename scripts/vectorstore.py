import os
import sys
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from models.embeddings import load_embedding_model
from config.config import DATA_PATH, VECTORSTORE_PATH

embeddings = load_embedding_model()

all_documents = []

print("Loading PDFs...")

for filename in os.listdir(DATA_PATH):

    if filename.endswith(".pdf"):

        file_path = os.path.join(DATA_PATH, filename)

        loader = PyPDFLoader(file_path)
        documents = loader.load()

        for doc in documents:

            doc.metadata["source_file"] = filename

            parts = filename.replace(".pdf", "").split("_")

            if len(parts) >= 2:
                doc.metadata["country"] = parts[0].upper()
                doc.metadata["visa_type"] = "_".join(parts[1:]).upper()

        all_documents.extend(documents)


print("Splitting documents...")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)

chunks = splitter.split_documents(all_documents)

print("Creating embeddings...")

vectorstore = FAISS.from_documents(chunks, embeddings)

vectorstore.save_local(VECTORSTORE_PATH)

print("Vectorstore created successfully")