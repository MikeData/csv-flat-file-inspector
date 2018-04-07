# -*- coding: utf-8 -*-

import sys

# Keep all the error handling in one place
class simpleErrors(object):


    # Specified "csv" doesn't contain .csv
    def inputNotCSV(self):
        raise ValueError("The input file specified needs to be a CSV with the .csv extension.")


    # Specified config.json doesn't contain .json
    def inputNotJson(self, file):
        raise ValueError("The input file specified needs to be a Json file with the .json extension. Got: " + file)


    # Cannot find the specified config.json file
    def cantFindConfigJson(self, path):
        raise RuntimeError("Aborting, cannot find config.json as the specified path: " + path)


    # Failed to load the json file.
    def cantLoadJsonFile(self, err):
        print("\n\nThe json file provided for config does exists, but we cannot load it. stack trace:\n ")
        print(err)
        sys.exit()


    # Failure to parse args from the config file
    def cannotParseAgs(self, key, args):
        raise ValueError("Cannot find the expected key '{k}' in the args dict: ".format(k=key) + str(args))

