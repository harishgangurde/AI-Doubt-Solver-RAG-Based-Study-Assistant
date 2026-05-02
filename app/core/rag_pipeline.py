from app.database.vector_store import search_similar_chunks
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rewrite_query(query):
    return f"Explain clearly: {query}"

def get_context(query, user_id, doc_id):
    query = rewrite_query(query)

    chunks = search_similar_chunks(query, user_id, doc_id, top_k=10)

    pairs = [(query, c["content"]) for c in chunks]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    top_chunks = [c[0] for c in ranked[:5]]

    return top_chunks, "\n\n".join([c["content"] for c in top_chunks])