"""
Toolbox main file managed by mlxpy to handle experiments configurations
"""

import logging
import logging.config

import mlxp


def set_seeds(seed):
    import torch
    import numpy as np

    torch.manual_seed(seed)
    np.random.seed(seed)


@mlxp.launch(
    config_path="./config",
    seeding_function=set_seeds,
)
def unmixing(ctx: mlxp.Context) -> None:

    cfg = ctx.config
    mode = cfg.mode

    logging.config.dictConfig(cfg)

    log = logging.getLogger(__name__)
    log.debug(f"Config:\n{cfg}")
    log.info(f"Unmixing mode: {mode.upper()}")

    if mode == "blind":
        from src.blind import main as _main
    elif mode == "supervised":
        from src.supervised import main as _main
    elif mode == "semi":
        from src.semisupervised import main as _main
    elif mode == "pruning":
        from src.pruning import main as _main
    else:
        raise ValueError(f"Mode {mode} is invalid")

    try:
        _main(ctx)
    except Exception:
        log.error("Exception occured", exc_info=True)


if __name__ == "__main__":
    unmixing()
