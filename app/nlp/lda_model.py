import json
from typing import Dict, List, Tuple

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer


class LDAModeler:
    def __init__(self, n_topics: int = 5, max_features: int = 5000) -> None:
        self.n_topics = n_topics
        self.max_features = max_features
        self.vectorizer = CountVectorizer(max_features=self.max_features)
        self.model = LatentDirichletAllocation(n_components=self.n_topics, random_state=42)

    def fit_transform(self, documents: List[str]):
        dt_matrix = self.vectorizer.fit_transform(documents)
        topic_distributions = self.model.fit_transform(dt_matrix)
        return topic_distributions

    def transform(self, documents: List[str]):
        dt_matrix = self.vectorizer.transform(documents)
        return self.model.transform(dt_matrix)

    def get_topics(self, top_n: int = 10) -> List[Dict]:
        feature_names = self.vectorizer.get_feature_names_out()
        topics = []
        for idx, topic in enumerate(self.model.components_):
            top_features_idx = topic.argsort()[:-top_n - 1:-1]
            top_terms = [(feature_names[i], float(topic[i])) for i in top_features_idx]
            topics.append({"topic": idx, "terms": top_terms})
        return topics

    @staticmethod
    def serialize_distribution(dist) -> str:
        return json.dumps([float(x) for x in dist])
