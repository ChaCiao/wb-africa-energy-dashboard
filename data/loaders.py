import os
import functools
import pandas as pd

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
_REQUIRED = ["access.csv", "tariffs.csv", "transition.csv", "institutions.csv"]


def _ensure_csvs():
    """Auto-generate mock CSVs if any are missing."""
    if any(not os.path.exists(os.path.join(DATA_DIR, f)) for f in _REQUIRED):
        from data.generate_mock_data import generate_all
        generate_all()


_ensure_csvs()


@functools.lru_cache(maxsize=1)
def load_access():
    return pd.read_csv(os.path.join(DATA_DIR, "access.csv"))


@functools.lru_cache(maxsize=1)
def load_tariffs():
    return pd.read_csv(os.path.join(DATA_DIR, "tariffs.csv"))


@functools.lru_cache(maxsize=1)
def load_transition():
    return pd.read_csv(os.path.join(DATA_DIR, "transition.csv"))


@functools.lru_cache(maxsize=1)
def load_institutions():
    return pd.read_csv(os.path.join(DATA_DIR, "institutions.csv"))
