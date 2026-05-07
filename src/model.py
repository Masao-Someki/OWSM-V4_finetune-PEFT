import torch.nn as nn

from src import peft_model as _impl


class OWSMFinetune(_impl.OWSMFinetune):
    """Backward-compatible alias that keeps the legacy import path."""

    def __init__(self, model_tag):
        super().__init__(model_tag=model_tag, peft=None)


class OWSMV4BaseInferenceModel(nn.Module):
    """Keep legacy return shape from src.model."""

    def __init__(
        self,
        *,
        model_tag: str,
        lang_sym: str,
        checkpoint_path: str,
        device: str = "cpu",
    ) -> None:
        super().__init__()
        self._model = _impl.OWSMV4BaseInferenceModel(
            model_tag=model_tag,
            lang_sym=lang_sym,
            checkpoint_path=checkpoint_path,
            device=device,
        )

    def forward(self, speech, lang_sym=None):
        return self._model.s2t(speech, lang_sym=lang_sym)


owsm_output_fn = _impl.owsm_output_fn
