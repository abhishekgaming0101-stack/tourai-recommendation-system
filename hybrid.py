from content_based import ContentBasedFilter
from collaborative import CollaborativeFilter

class HybridEngine:
    def __init__(self):
        self.cbf = ContentBasedFilter()
        self.cf = CollaborativeFilter()

    def _get_alpha(self, rating_count: int) -> float:
        if rating_count < 5:
            return 0.85
        elif rating_count < 20:
            return 0.50
        else:
            return 0.25

    def _normalize(self, score_list: list, score_key: str) -> dict:
        if not score_list:
            return {}
        values = [x[score_key] for x in score_list]
        mn, mx = min(values), max(values)
        if mx == mn:
            return {x["place_id"]: 1.0 for x in score_list}
        return {x["place_id"]: (x[score_key] - mn) / (mx - mn) for x in score_list}

    def recommend(self, user_id: str, user_profile: dict,
                  rating_count: int, all_place_ids: list,
                  rated_place_ids: list, top_n=10) -> list:
        alpha = self._get_alpha(rating_count)
        beta = 1.0 - alpha

        cbf_results = self.cbf.recommend(user_profile, top_n=50, exclude_ids=rated_place_ids)
        cf_results = self.cf.recommend(user_id, all_place_ids, rated_place_ids, top_n=50)

        cbf_norm = self._normalize(cbf_results, "score")
        cf_norm = self._normalize(cf_results, "score")

        all_ids = set(list(cbf_norm.keys()) + list(cf_norm.keys()))

        blended = {}
        for pid in all_ids:
            cbf_s = cbf_norm.get(pid, 0)
            cf_s = cf_norm.get(pid, 0)
            blended[pid] = alpha * cbf_s + beta * cf_s

        ranked = sorted(blended.items(), key=lambda x: -x[1])[:top_n]

        return [
            {
                "place_id": pid,
                "hybrid_score": round(score, 4),
                "cbf_score": round(cbf_norm.get(pid, 0), 4),
                "cf_score": round(cf_norm.get(pid, 0), 4),
                "alpha": alpha,
                "beta": beta,
                "method": "hybrid" if rating_count >= 5 else "cbf_cold_start"
            }
            for pid, score in ranked
        ]