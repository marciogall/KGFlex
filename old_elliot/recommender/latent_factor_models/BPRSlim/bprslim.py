"""
Module description:

"""


__version__ = '0.1'
__author__ = 'Felice Antonio Merra, Vito Walter Anelli, Claudio Pomo'
__email__ = 'felice.merra@poliba.it, vitowalter.anelli@poliba.it, claudio.pomo@poliba.it'

import pickle

import numpy as np
from tqdm import tqdm

from old_elliot.dataset.samplers import custom_sampler as cs
from old_elliot.recommender.base_recommender_model import init_charger
from old_elliot.recommender.base_recommender_model import BaseRecommenderModel
from old_elliot.recommender.latent_factor_models.BPRSlim.bprslim_model import BPRSlimModel
from old_elliot.recommender.recommender_utils_mixin import RecMixin
from old_elliot.utils.write import store_recommendation

np.random.seed(42)


class BPRSlim(RecMixin, BaseRecommenderModel):
    r"""
    BPR Sparse Linear Methods

    For further details, please refer to the `paper <http://glaros.dtc.umn.edu/gkhome/node/774>`_

    Args:
        factors: Number of latent factors
        lr: Learning rate
        lj_reg: Regularization coefficient for positive items
        li_reg: Regularization coefficient for negative items

    To include the recommendation model, add it to the config file adopting the following pattern:

    .. code:: yaml

      models:
        AMF:
          meta:
            save_recs: True
          epochs: 10
          batch_size: 512
          factors: 10
          lr: 0.001
          lj_reg: 0.001
          li_reg: 0.1
    """

    @init_charger
    def __init__(self, data, config, params, *args, **kwargs):
        self._random = np.random

        self._params_list = [
            ("_lr", "lr", "lr", 0.001, None, None),
            ("_lj_reg", "lj_reg", "ljreg", 0.001, None, None),
            ("_li_reg", "li_reg", "lireg", 0.1, None, None),
        ]

        self.autoset_params()

        if self._batch_size < 1:
            self._batch_size = self._data.transactions

        self._ratings = self._data.train_dict
        self._sp_i_train = self._data.sp_i_train
        self._i_items_set = list(range(self._num_items))

        self._sampler = cs.Sampler(self._data.i_train_dict)

        self._model = BPRSlimModel(self._data, self._num_users, self._num_items, self._lr, self._lj_reg, self._li_reg, self._sampler, random_seed=42)

    @property
    def name(self):
        return "BPRSlim" \
               + "_e:" + str(self._epochs) \
               + "_bs:" + str(self._batch_size) \
               + f"_{self.get_params_shortcut()}"

    def get_recommendations(self, k: int = 100):
        return {u: self._model.get_user_recs(u, k) for u in self._ratings.keys()}

    def predict(self, u: int, i: int):
        """
        Get prediction on the user item pair.

        Returns:
            A single float vaue.
        """
        return self._model.predict(u, i)

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
                    t.set_postfix({'loss': f'{loss / steps:.5f}'})
                    t.update()

            if not (it + 1) % self._validation_rate:

                print("Computing recommendations..")
                recs = self.get_recommendations(self.evaluator.get_needed_recommendations())
                result_dict = self.evaluator.eval(recs)
                self._results.append(result_dict)
                print(f'Finished')

                print(f'Epoch {(it + 1)}/{self._epochs} loss {loss  / steps:.3f}')

                if self._results[-1][self._validation_k]["val_results"][self._validation_metric] > best_metric_value:
                    print("******************************************")
                    best_metric_value = self._results[-1][self._validation_k]["val_results"][self._validation_metric]
                    if self._save_weights:
                        with open(self._saving_filepath, "wb") as f:
                            pickle.dump(self._model.get_model_state(), f)
                    if self._save_recs:
                        store_recommendation(recs, self._config.path_output_rec_result + f"{self.name}-it:{it + 1}.tsv")

    def restore_weights(self):
        try:
            with open(self._saving_filepath, "rb") as f:
                self._model.set_model_state(pickle.load(f))
            print(f"Model correctly Restored")

            recs = self.get_recommendations(self.evaluator.get_needed_recommendations())
            result_dict = self.evaluator.eval(recs)
            self._results.append(result_dict)

            print("******************************************")
            if self._save_recs:
                store_recommendation(recs, self._config.path_output_rec_result + f"{self.name}.tsv")
            return True

        except Exception as ex:
            print(f"Error in model restoring operation! {ex}")

        return False
