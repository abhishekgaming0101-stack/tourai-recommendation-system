import pandas as pd
import numpy as np

class CollaborativeFilter:
    def __init__(self, n_factors=20, n_epochs=15, lr=0.005, reg=0.02):
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.lr = lr
        self.reg = reg
        self.fitted = False
        self.global_mean = 3.0

    def fit(self, ratings: list):
        if len(ratings) < 3:
            self.fitted = False
            return
        
        df = pd.DataFrame(ratings)
        
        self.user_ids = list(df['user_id'].unique())
        self.place_ids = list(df['place_id'].unique())
        self.user_map = {u: i for i, u in enumerate(self.user_ids)}
        self.place_map = {p: i for i, p in enumerate(self.place_ids)}
        
        n_users = len(self.user_ids)
        n_places = len(self.place_ids)
        
        self.P = np.random.normal(0, 0.1, (n_users, self.n_factors))
        self.Q = np.random.normal(0, 0.1, (n_places, self.n_factors))
        self.bu = np.zeros(n_users)
        self.bi = np.zeros(n_places)
        self.global_mean = df['rating'].mean()
        
        for epoch in range(self.n_epochs):
            for _, row in df.iterrows():
                u = self.user_map[row['user_id']]
                i = self.place_map[row['place_id']]
                r = row['rating']
                
                pred = self.global_mean + self.bu[u] + self.bi[i] + np.dot(self.P[u], self.Q[i])
                err = r - pred
                
                self.bu[u] += self.lr * (err - self.reg * self.bu[u])
                self.bi[i] += self.lr * (err - self.reg * self.bi[i])
                
                P_old = self.P[u].copy()
                self.P[u] += self.lr * (err * self.Q[i] - self.reg * self.P[u])
                self.Q[i] += self.lr * (err * P_old - self.reg * self.Q[i])
        
        self.fitted = True

    def predict(self, user_id: str, place_id: str) -> float:
        if not self.fitted:
            return self.global_mean
        if user_id not in self.user_map or place_id not in self.place_map:
            return self.global_mean
        
        u = self.user_map[user_id]
        i = self.place_map[place_id]
        pred = self.global_mean + self.bu[u] + self.bi[i] + np.dot(self.P[u], self.Q[i])
        return float(np.clip(pred, 1, 5))

    def recommend(self, user_id: str, all_place_ids: list, rated_place_ids: list, top_n=10) -> list:
        if not self.fitted or user_id not in self.user_map:
            return []
        
        unrated = [pid for pid in all_place_ids if pid not in rated_place_ids]
        
        results = []
        for pid in unrated:
            score = self.predict(user_id, pid)
            results.append({"place_id": pid, "score": score, "source": "cf"})
        
        results.sort(key=lambda x: -x["score"])
        return results[:top_n]