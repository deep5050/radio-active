"""Sanity check that feature flags import across Python versions."""

from radioactive import feature_flags as ff


def test_feature_flags_are_bools():
    for name in dir(ff):
        if name.isupper() and not name.startswith("_"):
            assert isinstance(getattr(ff, name), bool), name
