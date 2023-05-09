"""
Sparse or semi-supervised unmixing methods main source file
"""

import logging

from hydra.utils import instantiate

from src.utils.aligners import AbundancesAligner
from src.utils.metrics import SREAggregator, RMSEAggregator

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main(cfg):
    logger.debug("Sparse Unmixing --- start...")

    # Instantiate objects
    extractor = instantiate(cfg.extractor)
    noise = instantiate(cfg.noise)
    # Metrics
    SRE = SREAggregator()
    RMSE = RMSEAggregator()

    for run in range(cfg.runs):

        hsi = instantiate(
            cfg.data,
            noise=noise,
        )

        if run == 0:
            # Log some info
            logger.info(hsi)
            hsi.plot_endmembers()
            hsi.plot_abundances()

        # Reload new model for each run
        model = instantiate(cfg.model, hsi=hsi, root_matlab=cfg.MATLAB_root)
        # # Apply noise to HSI
        # hsi.apply_noise(seed=cfg.seed + run)

        # # Project the data using SVD
        # if cfg.projection:
        #     hsi.apply_projection()

        # Sample HSI (using expanded abundances)
        Y, _, A_ref, D = hsi.sample(
            # expand_abundances=True,
            seed=cfg.seed + run,
            projection=cfg.projection,
        )

        # Compute abundances
        A_hat = model.compute_abundances(Y, D)

        # Align endmembers based on abundances MSE
        # aligner = AbundancesAligner(Aref=A_ref)
        # A1 = aligner.fit_transform(A_hat)

        # Use only first p abundances to compute metric
        # A_gt = A_ref[: hsi.p]
        # A2 = A1[: hsi.p]
        A_gt = A_ref
        A2 = A_hat[: hsi.p]

        hsi.plot_abundances(A0=A2, run=run)

        # Compute metrics
        SRE.add_run(run, A2, A_gt, hsi.labels)  # NOTE Order is important here
        RMSE.add_run(run, A2, A_gt, hsi.labels)

    # Aggregate metrics
    SRE.aggregate()
    RMSE.aggregate()

    logger.debug("Sparse Unmixing --- end...")
