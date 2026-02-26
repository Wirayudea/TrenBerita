from typing import List

from sklearn.cluster import KMeans


class KMeansClusterer:
    def __init__(self, n_clusters: int = 5) -> None:
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=self.n_clusters, random_state=42)

    def fit_predict(self, features) -> List[int]:
        return self.model.fit_predict(features).tolist()

    def predict(self, features) -> List[int]:
        return self.model.predict(features).tolist()
