from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ContentBasedFilter:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=300)
        self.tfidf_matrix = None
        self.place_ids = []
        self.fitted = False

    def fit(self, places: list):
        if not places:
            return
        
        corpus = []
        self.place_ids = []
        
        for p in places:
            tags = ' '.join(p.get('tags', []))
            text = f"{p.get('description', '')} {tags} {p.get('category', '')} {p.get('best_season', '')} {p.get('state', '')}"
            corpus.append(text.lower())
            self.place_ids.append(str(p['id']))
        
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        self.fitted = True

    def recommend(self, user_profile: dict, top_n=10, exclude_ids=None) -> list:
        if not self.fitted or len(self.place_ids) == 0:
            return []
        
        if exclude_ids is None:
            exclude_ids = []
        
        categories = ' '.join(user_profile.get('preferred_categories', []))
        liked = ' '.join(user_profile.get('liked_tags', []))
        budget = user_profile.get('budget', '')
        query = f"{categories} {liked} {budget} tourism travel india"
        
        user_vec = self.vectorizer.transform([query.lower()])
        scores = cosine_similarity(user_vec, self.tfidf_matrix).flatten()
        
        results = []
        for i, score in enumerate(scores):
            pid = self.place_ids[i]
            if pid not in exclude_ids:
                results.append({"place_id": pid, "score": float(score), "source": "cbf"})
        
        results.sort(key=lambda x: -x["score"])
        return results[:top_n]

    def get_similar(self, place_id: str, top_n=6) -> list:
        if not self.fitted or place_id not in self.place_ids:
            return []
        
        idx = self.place_ids.index(place_id)
        scores = cosine_similarity(self.tfidf_matrix[idx], self.tfidf_matrix).flatten()
        
        results = []
        for i, score in enumerate(scores):
            if self.place_ids[i] != place_id:
                results.append({"place_id": self.place_ids[i], "score": float(score), "source": "cbf_similar"})
        
        results.sort(key=lambda x: -x["score"])
        return results[:top_n]