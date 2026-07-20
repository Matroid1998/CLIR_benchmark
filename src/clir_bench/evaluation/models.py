"""
Loading embedding models and datasets on a compute node.

Three things here are workarounds rather than design, and all three were found
the expensive way -- by a run that produced numbers instead of an error:

  1. ``mteb.get_model`` is preferred over constructing a SentenceTransformer,
     because the registry entry carries the model's query/document prompts,
     ``trust_remote_code`` and late-interaction wrapper. Loading such a model
     directly still works and still returns embeddings, they are just the wrong
     ones. A plain SentenceTransformer is the fallback only for models MTEB has
     no entry for.
  2. ``position_ids`` buffers can arrive uninitialised -- see
     :func:`repair_position_ids_buffers`.
  3. In strict offline mode the datasets library lies about a repo's config
     names -- see :func:`resolve_loader_configs`.

Nothing in this module is imported at package import time: ``mteb``, ``torch``
and ``sentence_transformers`` are pulled in inside the functions that need them,
so the CLI stays fast on a machine that will never load a model.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, Optional

from datasets import get_dataset_config_names

# Relative to the project root, so a cluster job and a workstation share one
# download cache instead of re-fetching tens of gigabytes into ~/.cache.
CACHE_RELPATH = ".cache/huggingface"

# Some models registering a NON-persistent ``position_ids = arange(max_pos)`` buffer in
# __init__ are left with that buffer UNINITIALISED (garbage memory) by transformers 5.x
# after loading. The model then indexes its RoPE table with garbage position ids and
# crashes on the first encode -- an out-of-bounds IndexError on CPU, or an opaque
# "CUDA error: device-side assert triggered" on GPU. gte-multilingual-base hits exactly
# this, and before the repair it was the source of a whole set of published-looking but
# meaningless scores. Fix: re-fill the buffer after loading.
MODELS_NEEDING_POSITION_IDS_REPAIR = frozenset(
    {
        "Alibaba-NLP/gte-multilingual-base",
    }
)


def repair_position_ids_buffers(model: Any) -> int:
    """Re-initialise garbage 1-D integer ``position_ids`` buffers to a correct ``arange``.

    Returns how many buffers were repaired. Called ONLY for models in
    :data:`MODELS_NEEDING_POSITION_IDS_REPAIR`, so it cannot overwrite a
    position_ids buffer that legitimately holds something other than a range.
    Handles both the MTEB wrapper (whose module hangs off ``.model``) and a plain
    SentenceTransformer (an ``nn.Module`` itself).
    """
    import torch

    module = model if isinstance(model, torch.nn.Module) else getattr(model, "model", None)
    if not isinstance(module, torch.nn.Module):
        return 0
    fixed = 0
    for sub in module.modules():
        buf = sub._buffers.get("position_ids")
        if isinstance(buf, torch.Tensor) and buf.dim() == 1 and not torch.is_floating_point(buf):
            sub.register_buffer(
                "position_ids",
                torch.arange(buf.numel(), dtype=buf.dtype, device=buf.device),
                persistent=False,
            )
            fixed += 1
    if fixed:
        print(
            f"[fixup] re-initialised {fixed} position_ids buffer(s) for `{model}` "
            "(transformers non-persistent-buffer bug)"
        )
    return fixed


def configure_hf_cache(project_root: Path, *, relative: str = CACHE_RELPATH) -> Path:
    """Point every Hugging Face cache variable at one directory in the project.

    Set before any model is loaded. Compute nodes typically have a small home
    quota and a large project filesystem, so leaving the caches at their defaults
    is how a job dies at 90% of a download.

    Returns the sentence-transformers cache folder, which has to be passed
    explicitly to ``SentenceTransformer(cache_folder=...)``.
    """
    cache_dir = Path(project_root) / relative
    sentence_transformers_dir = cache_dir / "sentence_transformers"
    hub_dir = cache_dir / "hub"
    transformers_dir = cache_dir / "transformers"
    for directory in (cache_dir, sentence_transformers_dir, hub_dir, transformers_dir):
        directory.mkdir(parents=True, exist_ok=True)

    os.environ["HF_HOME"] = str(cache_dir)
    os.environ["HF_HUB_CACHE"] = str(hub_dir)
    os.environ["TRANSFORMERS_CACHE"] = str(transformers_dir)
    os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(sentence_transformers_dir)
    return sentence_transformers_dir


def load_model(
    model_name: str,
    *,
    cache_dir: Path,
    meta_factory: Optional[Callable[[Any], Any]] = None,
) -> tuple[Any, Any]:
    """Load a model and its metadata, preferring MTEB's registry loader.

    ``meta_factory`` builds metadata for a model MTEB does not know (in practice
    ``MTEB.create_model_meta``); without it such a model gets ``None`` metadata,
    which callers must tolerate.
    """
    import mteb

    try:
        model = mteb.get_model(model_name)
        model_meta = mteb.get_model_meta(model_name)
    except Exception:
        # Not in MTEB's registry (or its loader raised): fall back to a plain
        # SentenceTransformer. trust_remote_code is required by several custom
        # architectures and is safe here -- the model ids are a curated list.
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(
            model_name, cache_folder=str(cache_dir), trust_remote_code=True
        )
        model_meta = meta_factory(model) if meta_factory is not None else None

    if model_name in MODELS_NEEDING_POSITION_IDS_REPAIR:
        repair_position_ids_buffers(model)
    return model, model_meta


def dataset_cache_config_names(dataset_repo: str) -> list[str]:
    """Config names materialised in the local datasets cache (offline-safe)."""
    from datasets import config as datasets_config

    cache_root = Path(datasets_config.HF_DATASETS_CACHE) / dataset_repo.replace("/", "___")
    if not cache_root.is_dir():
        return []
    return sorted(path.name for path in cache_root.iterdir() if path.is_dir())


def resolve_loader_configs(dataset_repo: str, revision: str) -> list[str]:
    """Real config names of a dataset repo, robust to strict offline mode.

    With ``HF_HUB_OFFLINE=1`` -- the normal state of a compute node --
    ``get_dataset_config_names`` answers ``['default']`` instead of failing, so
    its answer is trusted only when it looks real; otherwise the config
    directories already present in the local datasets cache are used.
    """
    try:
        configs = [
            name
            for name in get_dataset_config_names(dataset_repo, revision=revision)
            if name != "default"
        ]
    except Exception:
        configs = []
    if configs:
        return configs
    return dataset_cache_config_names(dataset_repo)


@contextmanager
def offline_safe_loader_configs(dataset_repo: str, revision: str) -> Iterator[list[str]]:
    """Make MTEB's retrieval loader see a repo's real config names while it runs.

    The ``['default']`` answer described above is worse than a plain failure: it
    makes MTEB's ``RetrievalDatasetLoader`` believe ``default`` is a valid config
    and skip its ``default`` -> ``qrels`` fallback, so it then tries to load a
    config that does not exist and the job dies on a node with no internet. The
    real names are substituted for the duration of the load and the original
    function is always restored, so online behaviour is unchanged.
    """
    import mteb.abstasks.retrieval_dataset_loaders as loaders

    real_configs = resolve_loader_configs(dataset_repo, revision)
    original = loaders.get_dataset_config_names
    if real_configs:
        def _patched(path, revision=None, *args, **kwargs):  # noqa: ANN001 - upstream signature
            return list(real_configs)

        loaders.get_dataset_config_names = _patched
    try:
        yield real_configs
    finally:
        loaders.get_dataset_config_names = original


__all__ = [
    "CACHE_RELPATH",
    "MODELS_NEEDING_POSITION_IDS_REPAIR",
    "configure_hf_cache",
    "dataset_cache_config_names",
    "load_model",
    "offline_safe_loader_configs",
    "repair_position_ids_buffers",
    "resolve_loader_configs",
]
