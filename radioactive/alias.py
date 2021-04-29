import os.path

from zenlog import log


class Alias:
    def __init__(self):
        self.alias_map = []
        self.found = False

        self.alias_path = os.path.join(os.path.expanduser("~"),
                                       "radio-active-alias.txt")

    def generate_map(self):
        # create alias map
        if os.path.exists(self.alias_path):
            # log.debug("Alias file exists")
            try:
                with open(self.alias_path, "r") as f:
                    alias_data = f.read()
                    alias_list = alias_data.splitlines()
                    for alias in alias_list:
                        temp = alias.split("=")
                        left = temp[0]
                        right = temp[1]
                        self.alias_map.append({"name": left, "uuid": right})

                # log.debug(json.dumps(alias_map, indent=3))
            except Exception as e:
                log.warning("could not get / parse alias data")
            # log.debug(json.dumps(self.alias_map))
        else:
            log.warning("Alias file does not exist")

        # log.debug(json.dumps(self.alias_map, indent=3))

    def search(self, entry):
        if len(self.alias_map) > 0:
            log.debug("looking under alias file")
            for alias in self.alias_map:
                if alias["name"] == entry:
                    log.debug("Alias found: {} = {}".format(
                        alias["name"], alias["uuid"]))
                    self.found = True
                    return alias

            log.debug("Alias not found")
        else:
            log.debug("Empty Alias file")

        return None
