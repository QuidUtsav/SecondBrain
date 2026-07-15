import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

def build_faiss_index(chunks):
    
    embeddings = np.array([c["embedding"] for c in chunks],dtype=np.float32)
    index = faiss.IndexFlatL2(384)
    index.add(embeddings)
    return index

def search_index(index, query_embedding, chunks, top_k=3):
    
    query_embedding=query_embedding.reshape(1,-1).astype(np.float32)
    distance, indices = index.search(query_embedding,top_k)
    result = [chunks[i] for i in indices[0]]
    return result

STOP_WORDS = {"is", "in", "the", "a", "an", "of", "and", "to", "it", "what", "how", "why"}

def tokenize_for_bm25(text):
    return [w.lower() for w in text.split() if w.lower() not in STOP_WORDS]

def build_bm25_index(chunks):
    
    tokenized_corpus = [tokenize_for_bm25(chunk["text"]) for chunk in chunks]
    
    bm25= BM25Okapi(tokenized_corpus)

    return bm25
 
def search_bm25(bm25, query, chunks, top_k=3):
    
    tokenized_query = query.split(" ")
    
    scores = bm25.get_scores(tokenized_query)
    sorted_scores_indices =np.argsort(scores)[-top_k:][::-1]
    return [chunks[i] for i in sorted_scores_indices]
    
def hybrid_search(faiss_index, bm25, query, query_embedding, chunks, top_k=3, k=60):
        
    faiss_result = search_index(faiss_index,query_embedding,chunks,top_k=len(chunks))
    faiss_rank = {chunk["chunk_id"]: rank for rank, chunk in enumerate(faiss_result)}
    print(f"FAISS ranking on each chunk id:{faiss_rank}")
    
    bm25_result = search_bm25(bm25,query,chunks,top_k=len(chunks))
    bm25_rank = {chunk["chunk_id"]: rank for rank, chunk in enumerate(bm25_result)}
    print(f"BM25 ranking on each chunk id:{bm25_rank}")
    scores=[]
    print("RRF scores")
    for i,chunk in enumerate(chunks):
        rrf = 1/(k+faiss_rank[chunk["chunk_id"]])+1/(k+bm25_rank[chunk["chunk_id"]])
        print(rrf)
        scores.append((rrf,chunk))
    
    scores.sort(key= lambda x:x[0], reverse=1)
    return scores[0:top_k]

