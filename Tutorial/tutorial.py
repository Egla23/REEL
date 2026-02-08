 # pip install chromadb sentence-transformers
'''
https://docs.trychroma.com/docs/overview/getting-started
'''

import chromadb
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB client
client = chromadb.PersistentClient(path='.chroma/')

# Load the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Example documents
sentences = [
    "Meet Your Wedding Vendors on Video Before You Book...",
    "A cat is playing with a toy.",
    "Dogs are loyal animals.",
    "The sun is shining brightly."
]

# Generate embeddings for the sentences
embeddings = embedding_model.encode(sentences)

# Create a collection
collection = client.get_or_create_collection("reel_collection")

ids = [str(i) for i in range(len(sentences))]
metadatas = [{"language": "EN", "info": f"some info about document {i}"} for i in range(len(sentences))]

# Add documents to the collection
collection.add(
    documents=sentences,
    embeddings=embeddings,
    ids=ids,
    metadatas=metadatas
)

print(client.list_collections())

# Query sentence
query = "Bears are cute animals."
query_embedding = embedding_model.encode([query])

# Perform a similarity search
results = collection.query(
  query_embeddings=query_embedding, 
  n_results=2,
  where={"language": "EN"},
#   where_document={"$contains":"toy"}
)  

# Print results
print("Query:", query)
print("\nTop similar sentences:")
for result in results['documents']:
    print(result)

# ----------------------------
'''
[x] RI
[x] Venue
[x] 50 guests
''' 
# Query by IDs with optional filtering
results = collection.get(
    ids=["1", "2", "3"],
)

# Print results
print("Documents with specified IDs:")
for result in results['documents']:
    print(result)
