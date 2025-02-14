TEMPLATE = """experiment:
  version: 0.3.1
  dataset: sub-movielens1m-gallucci
  data_config:
    strategy: dataset
    dataset_path: ../data/{dataset}/{sub}/dataset_filtered_ordered_g{sub}.tsv
  splitting:
    test_splitting:
      strategy: random_subsampling
      test_ratio: 0.2
      folds: 1
  top_k: 10
  evaluation:
    cutoffs: [10, 5, 1]
    simple_metrics: [nDCGRendle2020, HR]
    relevance_threshold: 3
  gpu: 0
  external_models_path: ../external/models/__init__.py
  models:
    ItemKNN:
      meta:
        verbose: True
        save_recs: True
        validation_metric: nDCGRendle2020@10
        hyper_opt_alg: tpe
        hyper_max_evals: 10
      neighbors: [uniform, 5, 10]
      similarity: ['cosine', 'jaccard']
      implementation: standard
    UserKNN:
      meta:
        verbose: True
        save_recs: True
        validation_metric: nDCGRendle2020@10
        hyper_opt_alg: tpe
        hyper_max_evals: 1
      neighbors: [uniform, 5, 10]
      similarity: [cosine, jaccard]
      implementation: standard
    FunkSVD:
      meta:
        save_recs: True
        verbose: True
        hyper_max_evals: 1
        hyper_opt_alg: tpe
        validation_metric: nDCGRendle2020@10
      epochs: 10
      batch_size: 512
      factors: [16, 64, 128, 256]
      lr: [0.001, 0.003, 0.01]
      reg_w: 0.1
      reg_b: 0.001
    NeuMF:
      meta:
        hyper_max_evals: 1
        hyper_opt_alg: tpe
        validation_rate: 5
        validation_metric: nDCGRendle2020@10
      lr: [loguniform, -10, -1]
      batch_size: 512
      epochs: 10
      mf_factors: [quniform, 8, 32, 1]
      mlp_factors: [8, 16]
      mlp_hidden_size: [(32, 16, 8), (64, 32, 16)]
      prob_keep_dropout: [uniform, 0.5, 1]
      is_mf_train: True
      is_mlp_train: True
    MultiVAE:
      meta:
        save_recs: True
        verbose: True
        hyper_max_evals: 1
        hyper_opt_alg: tpe
        validation_rate: 5
        validation_metric: nDCGRendle2020@10
      lr: [loguniform, -11.5, 0]
      epochs: 10
      batch_size: 512
      intermediate_dim: [300, 400, 500]
      latent_dim: [100, 200, 300]
      dropout_pkeep: [uniform, 0.5, 1]
      reg_lambda: [loguniform, -11.5, 0]
       """
