import os.path

from pick import pick
from zenlog import log


class Alias:
    def __init__(self):
        self.alias_map = []
        self.found = False

        self.alias_path = os.path.join(os.path.expanduser("~"), ".radio-active-alias")

    def write_stations(self, station_map):
        """Write stations file from generated map"""
        with open(self.alias_path, "w") as f:
            f.flush()
            for entry in station_map:
                f.write(
                    "{}=={}\n".format(
                        entry["name"].strip(), entry["uuid_or_url"].strip()
                    )
                )
        return True

    def generate_map(self):
        """parses the fav list file and generates a list"""
        # create alias map
        self.alias_map = []

        if os.path.exists(self.alias_path):
            log.debug(f"Alias file at: {self.alias_path}")
            try:
                with open(self.alias_path, "r+") as f:
                    alias_data = f.read().strip()
                    if alias_data == "":
                        log.debug("Empty alias list")
                        return
                    alias_list = alias_data.splitlines()
                    for alias in alias_list:
                        if alias.strip() == "":
                            # empty line pass
                            continue
                        temp = alias.split("==")
                        left = temp[0]
                        right = temp[1]
                        # may contain both URL and UUID
                        self.alias_map.append({"name": left, "uuid_or_url": right})
            except Exception as e:
                log.debug(f"could not get / parse alias data: {e}")

        else:
            log.debug("Alias file does not exist")

    def search(self, entry):
        """searches for an entry in the fav list with the name
        the right side may contain both url or uuid , need to check properly
        """
        log.debug("Alias search: {}".format(entry))
        if len(self.alias_map) > 0:
            log.debug("looking under alias file")
            for alias in self.alias_map:
                if alias["name"].strip() == entry.strip():
                    log.debug(
                        "Alias found: {} == {}".format(
                            alias["name"], alias["uuid_or_url"]
                        )
                    )
                    self.found = True
                    return alias

            log.debug("Alias not found")
        else:
            log.debug("Empty Alias file")
        return None

    def add_entry(self, left, right):
        """Adds a new entry to the fav list"""
        self.generate_map()
        if self.search(left) is not None:
            log.warning("An entry with same name already exists, try another name")
            return False
        else:
            with open(self.alias_path, "a+") as f:
                f.write("{}=={}\n".format(left.strip(), right.strip()))
                log.info("Current station added to your favorite list")
            return True

    def flush(self):
        """deletes all the entries in the fav list"""
        try:
            with open(self.alias_path, "w") as f:
                f.flush()
            log.info("All entries deleted in your favorite list")
            return 0
        except Exception as e:
            log.debug("Error: {}".format(e))
            log.error("could not delete your favorite list. something went wrong")
            return 1

    def remove_entries(self):
        # select entries from fav menu and remove them
        self.generate_map()

        if not self.alias_map:
            log.error("No stations to be removed!")
            return

        title = "Select stations to be removed. Hit 'SPACE' to select "
        options = [entry["name"] for entry in self.alias_map]
        selected = pick(
            options, title, indicator="->", multiselect=True, min_selection_count=1
        )

        # Extract integer numbers and create a new list
        indices_to_remove = [item[1] for item in selected if isinstance(item[1], int)]

        # remove selected entries from the map, and regenerate
        filtered_list = [
            self.alias_map[i]
            for i in range(len(self.alias_map))
            if i not in indices_to_remove
        ]

        log.debug(
            f"Current # of entries reduced to : {len(filtered_list)} from {len(self.alias_map)}"
        )

        self.write_stations(filtered_list)
        self.alias_map = filtered_list
        log.info("Stations removed successfully!")
