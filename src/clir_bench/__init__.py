"""
clir_bench -- a domain-pluggable pipeline for multilingual CLIR benchmarks.

Importing this package is deliberately cheap: no argparse, no dataloaders, no
model stack. Submodules pull their own dependencies when actually used.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
