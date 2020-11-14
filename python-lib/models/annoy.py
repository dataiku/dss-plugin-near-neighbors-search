# -*- coding: utf-8 -*-

import numpy as np
from typing import AnyStr, Dict, List

import annoy
from tqdm import tqdm

from models.base import SimilaritySearchAlgorithm
from plugin_utils import time_logging


class AnnoyAlgorithm(SimilaritySearchAlgorithm):
    """Wrapper class for the Annoy Similarity Search algorithm"""

    def __init__(self, num_dimensions: int, **kwargs):
        super().__init__(num_dimensions)
        self.annoy_metric = kwargs.get("annoy_metric")
        self.annoy_num_trees = int(kwargs.get("annoy_num_trees", 10))
        self.index = annoy.AnnoyIndex(self.num_dimensions, metric=self.annoy_metric)

    def __str__(self):
        return "annoy"

    def get_config(self) -> Dict:
        return {
            "algorithm": self.__str__(),
            "num_dimensions": self.num_dimensions,
            "annoy_metric": self.annoy_metric,
            "annoy_num_trees": self.annoy_num_trees,
        }

    @time_logging(log_message="Building index and saving to disk")
    def build_save_index(self, vectors: np.array, file_path: AnyStr) -> None:
        self.index.on_disk_build(file_path)
        for i, vector in enumerate(tqdm(vectors, mininterval=1.0)):
            self.index.add_item(i, vector.tolist())
        self.index.build(n_trees=self.annoy_num_trees)

    @time_logging(log_message="Loading pre-computed index from disk")
    def load_index(self, file_path: AnyStr) -> None:
        self.index.load(file_path)

    def find_neighbors_vector(self, vectors: np.array, num_neighbors: int = 5) -> List:
        neighbors = [self.index.get_nns_by_vector(vector, num_neighbors) for vector in vectors]
        return neighbors
