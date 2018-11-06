# -*- coding: utf-8 -*-

import sys

# Keep all the error handling in one place
class simpleErrors(object):

    # User has selected an unexpected environment
    def envNotRecognised(self):
        raise ValueError("The environment you have provided is not recognised")

    # Data has an unacceptable level of sparsity
    def sparsityError(self, sparsity):
        raise ValueError("Unacceptable levels of sparsity found:" + str(sparsity * 100) + "%")

    # There are specific blank cells in positons that should never be blank
    def missingItems(self, errorText):
        raise ValueError(errorText)

    # There are unexpected columns in the CSV
    def unexpectedColumns(self, unexpectedCol):
        print("\n\nAborting. 1 or more expected columns are not present in the CSV.\n ")
        print("Listing:")
        for item in unexpectedCol:
            print("- " + item)
        sys.exit()

    # Throw an informative error if the
    def incorrectItems(self, notFoundList, uri):
        print("\n\nAborting. 1 or more items in the CSV are not present in the provided url validation source.\n ")
        print("Listing:")
        for item in notFoundList:
            print("- " + item)
        print("\n " + uri)
        sys.exit()

    # Specified "csv" doesn't contain .csv
    def inputNotCSV(self):
        raise ValueError("The input file specified needs to be a CSV with the .csv extension.")

    # Source not supported
    def typeNotSupported(self, type):
        raise ValueError("The source type '{t}' is not supported for validation.".format(t=type))

    # Specified config.json doesn't contain .json
    def inputNotJson(self, file):
        raise ValueError("The input file specified needs to be a Json file with the .json extension. Got: " + file)

    # Pandas is unable to load the provided CSV
    def cannotLoadCSV(self, err):
        print("\n\nAborting. Pandas is unable to load the provided CSV. Stack trace follows:\n ")
        print(err)
        sys.exit()

    # Cannot find the specified config.json file
    def cannotRequestJson(self, url):
        raise RuntimeError("Aborting, cannot access the requested config.json on this url: " + url)

    # Failed to load the json file.
    def cantLoadJsonFile(self, err):
        print("\n\nThe json file provided for config does exist, but we cannot load it. Stack trace follows:\n ")
        print(err)
        sys.exit()

    # Failure to parse args from the config file
    def cannotParseAgs(self, key, args):
        raise ValueError("Cannot find the expected key '{k}' in the args dict: ".format(k=key) + str(args))

