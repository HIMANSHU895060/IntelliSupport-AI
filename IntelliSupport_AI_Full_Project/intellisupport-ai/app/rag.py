import re, math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import settings
DOCS = [
 {"id":"KB-001","title":"Password reset","text":"To reset your password, choose Forgot password on the sign-in page. Check spam if the reset email is missing. Never share your password or one-time code."},
 {"id":"KB-002","title":"API rate limit and HTTP 429","text":"HTTP 429 indicates too many requests. Check the API quota and rate limit headers. Retry with exponential backoff and jitter. Contact support if quota is unexpectedly exhausted."},
 {"id":"KB-003","title":"Billing and refunds","text":"Billing disputes and refund requests must be reviewed by an authorized billing specialist. The AI assistant cannot approve refunds or promise a refund outcome."},
 {"id":"KB-004","title":"Account access","text":"Confirm you are using the registered email address, check keyboard layout, and use password reset if needed. Account changes require identity verification."},
 {"id":"KB-005","title":"Service incident","text":"For suspected service outages, capture timestamps, region, affected service, request IDs and error messages. Critical incidents must be escalated to on-call support."},
 {"id":"KB-006","title":"Contact support","text":"Provide the affected product, steps to reproduce, expected result, actual result, timestamp and relevant non-sensitive error details."}
]
def chunks(text, size=420, overlap=70):
    words = text.split()
    out=[]; start=0
    while start < len(words):
        part=" ".join(words[start:start+size])
        if part: out.append(part)
        start += max(1, size-overlap)
    return out
class RAGEngine:
    def __init__(self):
        self.records=[]
        for doc in DOCS:
            for i, chunk in enumerate(chunks(doc["text"], 60, 10)):
                self.records.append({**doc, "chunk_id":i, "chunk":chunk})
        self.vectorizer=TfidfVectorizer(ngram_range=(1,2), stop_words="english")
        self.matrix=self.vectorizer.fit_transform([x["title"]+" "+x["chunk"] for x in self.records])
        self.semantic_model=None
        try:
            from sentence_transformers import SentenceTransformer
            self.semantic_model=SentenceTransformer(settings.rag_embedding_model)
            self.embeddings=self.semantic_model.encode([x["title"]+" "+x["chunk"] for x in self.records], normalize_embeddings=True)
        except Exception:
            self.embeddings=None
    def search(self, query, k=4):
        q=self.vectorizer.transform([query])
        lexical=cosine_similarity(q,self.matrix)[0]
        semantic=None
        if self.semantic_model is not None and self.embeddings is not None:
            import numpy as np
            v=self.semantic_model.encode([query], normalize_embeddings=True)[0]
            semantic=np.dot(self.embeddings,v)
        scored=[]
        for i, rec in enumerate(self.records):
            score=float(0.55*lexical[i] + 0.45*semantic[i]) if semantic is not None else float(lexical[i])
            if score > 0: scored.append({**rec,"score":round(score,4),"source":rec["id"]})
        scored.sort(key=lambda x:x["score"], reverse=True)
        return scored[:k]
rag=RAGEngine()
