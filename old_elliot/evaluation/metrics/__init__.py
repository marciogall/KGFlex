"""
This is the metrics' module.

This module contains and expose the recommendation metrics.
Each metric is encapsulated in a specific package.

See the implementation of Precision metric for creating new per-user metrics.
See the implementation of Item Coverage for creating new cross-user metrics.
"""

__version__ = '0.1'
__author__ = 'Vito Walter Anelli, Claudio Pomo'
__email__ = 'vitowalter.anelli@poliba.it, claudio.pomo@poliba.it'

from old_elliot.evaluation.metrics.accuracy.ndcg import NDCG, NDCGRendle2020
from old_elliot.evaluation.metrics.accuracy.precision import Precision
from old_elliot.evaluation.metrics.accuracy.recall import Recall
from old_elliot.evaluation.metrics.accuracy.hit_rate import HR
from old_elliot.evaluation.metrics.accuracy.mrr import MRR
from old_elliot.evaluation.metrics.accuracy.map import MAP
from old_elliot.evaluation.metrics.accuracy.mar import MAR
from old_elliot.evaluation.metrics.accuracy.f1 import F1, ExtendedF1
from old_elliot.evaluation.metrics.accuracy.DSC import DSC
from old_elliot.evaluation.metrics.accuracy.AUC import LAUC, AUC, GAUC

from old_elliot.evaluation.metrics.rating.mae import MAE
from old_elliot.evaluation.metrics.rating.mse import MSE
from old_elliot.evaluation.metrics.rating.rmse import RMSE

from old_elliot.evaluation.metrics.coverage import ItemCoverage, UserCoverage, NumRetrieved, UserCoverageAtN

from old_elliot.evaluation.metrics.diversity.gini_index import GiniIndex
from old_elliot.evaluation.metrics.diversity.shannon_entropy import ShannonEntropy
from old_elliot.evaluation.metrics.diversity.SRecall import SRecall

from old_elliot.evaluation.metrics.novelty.EFD import EFD, ExtendedEFD
from old_elliot.evaluation.metrics.novelty.EPC import EPC, ExtendedEPC

from old_elliot.evaluation.metrics.bias import ARP, APLT, ACLT, PopRSP, PopREO, ExtendedPopRSP, ExtendedPopREO

from old_elliot.evaluation.metrics.fairness.MAD import UserMADrating, ItemMADrating, UserMADranking, ItemMADranking
from old_elliot.evaluation.metrics.fairness.BiasDisparity import BiasDisparityBR, BiasDisparityBS, BiasDisparityBD
from old_elliot.evaluation.metrics.fairness.rsp import RSP
from old_elliot.evaluation.metrics.fairness.reo import REO

from old_elliot.evaluation.metrics.statistical_array_metric import StatisticalMetric

_metric_dictionary = {
    "nDCG": NDCG,
    "nDCGRendle2020": NDCGRendle2020,
    "Precision": Precision,
    "Recall": Recall,
    "HR": HR,
    "MRR": MRR,
    "MAP": MAP,
    "MAR": MAR,
    "F1": F1,
    "ExtendedF1": ExtendedF1,
    "DSC": DSC,
    "LAUC": LAUC,
    "GAUC": GAUC,
    "AUC": AUC,
    "ItemCoverage": ItemCoverage,
    "UserCoverage": UserCoverage,
    "UserCoverageAtN": UserCoverageAtN,
    "NumRetrieved": NumRetrieved,
    "Gini": GiniIndex,
    "SEntropy": ShannonEntropy,
    "EFD": EFD,
    "ExtendedEFD": ExtendedEFD,
    "EPC": EPC,
    "ExtendedEPC": ExtendedEPC,
    "MAE": MAE,
    "MSE": MSE,
    "RMSE": RMSE,
    "UserMADrating": UserMADrating,
    "ItemMADrating": ItemMADrating,
    "UserMADranking": UserMADranking,
    "ItemMADranking": ItemMADranking,
    "BiasDisparityBR": BiasDisparityBR,
    "BiasDisparityBS": BiasDisparityBS,
    "BiasDisparityBD": BiasDisparityBD,
    "SRecall": SRecall,
    "ARP": ARP,
    "APLT": APLT,
    "ACLT": ACLT,
    "PopRSP": PopRSP,
    "PopREO": PopREO,
    "ExtendedPopRSP": ExtendedPopRSP,
    "ExtendedPopREO": ExtendedPopREO,
    "RSP": RSP,
    "REO": REO
}

_lower_dict = {k.lower(): v for k, v in _metric_dictionary.items()}


def parse_metrics(metrics):
    return [_lower_dict[m.lower()] for m in metrics if m.lower() in _lower_dict.keys()]


def parse_metric(metric):
    metric = metric.lower()
    return _lower_dict[metric] if metric in _lower_dict.keys() else None
