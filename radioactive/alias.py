import os.path

from zenlog import log


class Alias:
    def __init__(self):
        self.alias_map = []
        self.found = False

        self.alias_path = os.path.join(os.path.expanduser("~"), ".radio-active-alias")

    def generate_map(self):
        """parses the fav list file and generates a list"""
        # create alias map
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
