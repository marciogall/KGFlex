"""
Module description:

"""

__version__ = '0.1'
__author__ = 'Vito Walter Anelli, Claudio Pomo, Daniele Malitesta'
__email__ = 'vitowalter.anelli@poliba.it, claudio.pomo@poliba.it, daniele.malitesta@poliba.it'

import scipy.sparse as sp
from tqdm import tqdm

from old_elliot.utils.write import store_recommendation

import numpy as np
import random

from old_elliot.dataset.samplers import custom_sampler as cs

from old_elliot.recommender import BaseRecommenderModel
from old_elliot.recommender.recommender_utils_mixin import RecMixin

from old_elliot.recommender.graph_based.lightgcn.LightGCN_model import LightGCNModel
from old_elliot.recommender.base_recommender_model import init_charger

np.random.seed(42)
random.seed(0)


class LightGCN(RecMixin, BaseRecommenderModel):
    r"""
    LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation

    For further details, please refer to the `paper <https://dl.acm.org/doi/10.1145/3397271.3401063>`_

    Args:
        lr: Learning rate
        epochs: Number of epochs
        factors: Number of latent factors
        batch_size: Batch size
        l_w: Regularization coefficient
        n_layers: Number of embedding propagation layers
        n_fold: Number of folds to split the adjacency matrix into sub-matrices and ease the computation

    To include the recommendation model, add it to the config file adopting the following pattern:

    .. code:: yaml

      models:
        LightGCN:
          meta:
            save_recs: True
          lr: 0.0005
          epochs: 50
          batch_size: 512
          factors: 64
          batch_size: 256
          l_w: 0.1
          n_layers: 1
          n_fold: 5
    """
    @init_charger
    def __init__(self, data, config, params, *args, **kwargs):
        """
        """
        self._random = np.random
        self._random_p = random

        self._ratings = self._data.train_dict
        self._sampler = cs.Sampler(self._data.i_train_dict)

        if self._batch_size < 1:
            self._batch_size = self._num_users

        ######################################

        self._params_list = [
            ("_learning_rate", "lr", "lr", 0.0005, None, None),
            ("_factors", "latent_dim", "factors", 64, None, None),
            ("_n_layers", "n_layers", "n_layers", 1, None, None),
            ("_l_w", "l_w", "l_w", 0.1, None, None),
            ("_n_fold", "n_fold", "n_fold", 1, None, None),
        ]
        self.autoset_params()

        self._adjacency, self._laplacian = self._create_adj_mat()

        self._model = LightGCNModel(
            num_users=self._num_users,
            num_items=self._num_items,
            learning_rate=self._learning_rate,
            embed_k=self._factors,
            n_layers=self._n_layers,
            l_w=self._l_w,
            n_fold=self._n_fold,
            adjacency=self._adjacency,
            laplacian=self._laplacian
        )

    def _create_adj_mat(self):
        adjacency = sp.dok_matrix((self._num_users + self._num_items,
                                   self._num_users + self._num_items), dtype=np.float32)
        adjacency = adjacency.tolil()
        ratings = self._data.sp_i_train.tolil()

        adjacency[:self._num_users, self._num_users:] = ratings
        adjacency[self._num_users:, :self._num_users] = ratings.T
        adjacency = adjacency.todok()

        def normalized_adj_bi(adj):
            # This is exactly how it's done in the paper. Different normalization approaches might be followed.
            rowsum = np.array(adj.sum(1))
            rowsum += 1e-7  # to avoid division by zero warnings

            d_inv_sqrt = np.power(rowsum, -0.5).flatten()
            d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.
            d_mat_inv_sqrt = sp.diags(d_inv_sqrt)
            bi_adj = adj.dot(d_mat_inv_sqrt).transpose().dot(d_mat_inv_sqrt)
            return bi_adj.tocoo()

        laplacian = normalized_adj_bi(adjacency)

        return adjacency.tocsr(), laplacian.tocsr()

    @property
    def name(self):
        return "LightGCN" \
               + "_e:" + str(self._epochs) \
               + "_bs:" + str(self._batch_size) \
               + f"_{self.get_params_shortcut()}"

    def train(self):
        if self._restore:
            return self.restore_weights()

        best_metric_value = 0
        for it in range(self._epochs):
            loss = 0
            steps = 0
            with tqdm(total=int(self._data.transactions // self._batch_size), disable=not self._verbose) as t:
                for batch in self._sampler.step(self._data.transactions, self._batch_size):
                    steps += 1
                    loss += self._model.train_step(batch)
                    t.set_postfix({'loss': f'{loss.numpy() / steps:.5f}'})
                    t.update()

            if not (it + 1) % self._validation_rate:
                recs = self.get_recommendations(self.evaluator.get_needed_recommendations())
                result_dict = self.evaluator.eval(recs)
                self._results.append(result_dict)

                print(f'Epoch {(it + 1)}/{self._epochs} loss {loss / steps:.5f}')

                if self._results[-1][self._validation_k]["val_results"][self._validation_metric] > best_metric_value:
                    print("******************************************")
                    best_metric_value = self._results[-1][self._validation_k]["val_results"][self._validation_metric]
                    if self._save_weights:
                        self._model.save_weights(self._saving_filepath)
                    if self._save_recs:
                        store_recommendation(recs, self._config.path_output_rec_result + f"{self.name}-it:{it + 1}.tsv")

    def get_recommendations(self, k: int = 100):
        predictions_top_k = {}
        for index, offset in enumerate(range(0, self._num_users, self._params.batch_size)):
            offset_stop = min(offset+self._params.batch_size, self._num_users)
            predictions = self._model.predict(offset, offset_stop)
            v, i = self._model.get_top_k(predictions, self.get_train_mask(offset, offset_stop), k=k)
            items_ratings_pair = [list(zip(map(self._data.private_items.get, u_list[0]), u_list[1]))
                                  for u_list in list(zip(i.numpy(), v.numpy()))]
            predictions_top_k.update(dict(zip(range(offset, offset_stop), items_ratings_pair)))
        return predictions_top_k
