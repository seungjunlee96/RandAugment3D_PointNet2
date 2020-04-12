import os

import hydra
import omegaconf
import pytorch_lightning as pl
import torch
from pytorch_lightning.loggers import TensorBoardLogger

torch.backends.cudnn.enabled = True
torch.backends.cudnn.benchmark = True


def wrap_tb_logger():
    orig_method = TensorBoardLogger.log_hyperparams

    def hydra_hparams(self, hparams):
        def _to_dot_dict(cfg):
            res = {}
            for k, v in cfg.items():
                if isinstance(v, omegaconf.DictConfig):
                    res.update(
                        {k + "." + subk: subv for subk, subv in _to_dot_dict(v).items()}
                    )
                elif isinstance(v, (str, int, float, bool)):
                    res[k] = v

            return res

        return orig_method(self, _to_dot_dict(hparams))

    TensorBoardLogger.log_hyperparams = hydra_hparams


@hydra.main("config/config.yaml")
def main(cfg):
    wrap_tb_logger()
    model = hydra.utils.instantiate(cfg.task_model, cfg)

    early_stop_callback = pl.callbacks.EarlyStopping(patience=5)
    checkpoint_callback = pl.callbacks.ModelCheckpoint(
        monitor="val_acc",
        mode="max",
        save_top_k=2,
        filepath=os.path.join(
            cfg.task_model.name, "{epoch}-{val_loss:.2f}-{val_acc:.3f}"
        ),
        verbose=True,
    )
    trainer = pl.Trainer(
        gpus=list(cfg.gpus),
        max_epochs=cfg.epochs,
        early_stop_callback=early_stop_callback,
        checkpoint_callback=checkpoint_callback,
        distributed_backend=cfg.distrib_backend,
    )

    trainer.fit(model)


if __name__ == "__main__":
    main()
