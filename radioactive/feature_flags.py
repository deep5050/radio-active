import os
from radioactive.paths import get_base_dir

# Default Defaults
MINIMAL_FEATURE = False
RECORDING_FEATURE = True
TRACK_FEATURE = True
SEARCH_FEATURE = True
CYCLE_FEATURE = True
INFO_FEATURE = True
TIMER_FEATURE = True
HISTORY_FEATURE = True


def load_features():
    global MINIMAL_FEATURE, RECORDING_FEATURE, TRACK_FEATURE, SEARCH_FEATURE, CYCLE_FEATURE, INFO_FEATURE, TIMER_FEATURE, HISTORY_FEATURE

    base_dir = get_base_dir()
    config_path = os.path.join(base_dir, "features.conf")

    if os.path.exists(config_path):
        flags = {}
        try:
            with open(config_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        # We only care about known flags
                        flags[key.strip()] = value.strip().lower() == "true"

            # Update globals
            if "MINIMAL_FEATURE" in flags:
                MINIMAL_FEATURE = flags["MINIMAL_FEATURE"]
            if "RECORDING_FEATURE" in flags:
                RECORDING_FEATURE = flags["RECORDING_FEATURE"]
            if "TRACK_FEATURE" in flags:
                TRACK_FEATURE = flags["TRACK_FEATURE"]
            if "SEARCH_FEATURE" in flags:
                SEARCH_FEATURE = flags["SEARCH_FEATURE"]
            if "CYCLE_FEATURE" in flags:
                CYCLE_FEATURE = flags["CYCLE_FEATURE"]
            if "INFO_FEATURE" in flags:
                INFO_FEATURE = flags["INFO_FEATURE"]
            if "TIMER_FEATURE" in flags:
                TIMER_FEATURE = flags["TIMER_FEATURE"]
            if "HISTORY_FEATURE" in flags:
                HISTORY_FEATURE = flags["HISTORY_FEATURE"]

        except Exception:
            pass

    else:
        # Create default features.conf
        try:
            with open(config_path, "w") as f:
                f.write(
                    "# Feature Configuration File\n"
                    "# Set features to true or false to enable/disable them\n"
                    "# If MINIMAL_FEATURE is true, it will override and disable all optional features (Recording, Track, Search, Cycle, Info, Timer, History)\n\n"
                    "MINIMAL_FEATURE=false\n"
                    "RECORDING_FEATURE=true\n"
                    "TRACK_FEATURE=true\n"
                    "SEARCH_FEATURE=true\n"
                    "CYCLE_FEATURE=true\n"
                    "INFO_FEATURE=true\n"
                    "TIMER_FEATURE=true\n"
                    "HISTORY_FEATURE=true\n"
                )
        except Exception:
            # If we can't write, just continue with defaults
            pass

    # Apply Minimal
    # If MINIMAL_FEATURE is true, it will override and disable all optional features
    if MINIMAL_FEATURE:
        RECORDING_FEATURE = False
        TRACK_FEATURE = False
        SEARCH_FEATURE = False
        CYCLE_FEATURE = False
        INFO_FEATURE = False
        TIMER_FEATURE = False
        HISTORY_FEATURE = False


load_features()
