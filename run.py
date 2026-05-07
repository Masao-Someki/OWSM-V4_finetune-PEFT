from egs3.TEMPLATE.asr.run import (
    DEFAULT_STAGES,
    build_parser,
    main,
    parse_cli_and_stage_args,
)
from espnet3.systems.base.system import BaseSystem  # Example import


def _patch_local_parallel_behavior() -> None:
    """Enable parallel runner when parallel.env=local and n_workers>1.

    Upstream BaseRunner treats env=local as always sequential. For this project we
    want local Dask workers when n_workers is set above 1.
    """
    from espnet3.parallel import base_runner as _base_runner

    if getattr(_base_runner, "_local_parallel_patch_applied", False):
        return

    original_call = _base_runner.BaseRunner.__call__

    def _patched_call(self, indices):
        indices = list(indices)
        if self.batch_size is not None:
            if self.batch_size <= 0:
                raise ValueError("batch_size must be a positive integer.")
            indices = _base_runner._chunk_indices(indices, self.batch_size)
        if self.async_mode:
            import asyncio

            return asyncio.run(self._run_async(indices))

        par_config = _base_runner.get_parallel_config()
        if par_config is None:
            return self._run_local(indices)

        env = getattr(par_config, "env", "local")
        n_workers = int(getattr(par_config, "n_workers", 1))
        if env == "local" and n_workers > 1:
            return self._run_parallel(indices)
        if env == "local":
            return self._run_local(indices)
        return self._run_parallel(indices)

    _base_runner.BaseRunner.__call__ = _patched_call
    _base_runner._local_parallel_patch_applied = True
    _base_runner._local_parallel_original_call = original_call


if __name__ == "__main__":
    _patch_local_parallel_behavior()
    parser = build_parser(
        stages=DEFAULT_STAGES,
        add_arguments=None,  # You can create your parser and put here if needed
    )
    args, stages_to_run = parse_cli_and_stage_args(parser, stages=DEFAULT_STAGES)

    main(
        args=args,
        system_cls=BaseSystem,
        stages=stages_to_run,
    )
