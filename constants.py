# -*- coding: utf-8 -*-

import json, os, traceback
from pathlib import Path

from errors import simpleErrors
from inspectFunctionLib import *

# Defaults
DEFAULT_CONFIG = "config_V4.json"


# Build a config object from the specified json file
class config(object):

    def __init__(self, configFile):

        # Errors
        self.errors = simpleErrors()

        # Basic Input
        self.configFileName = configFile
        self.configAsJson = self.readJson()

        # Attach the methods we'll use and the order and args we'll use
        self.orderAndArgs = self.createOrderAndArgs()


    # Read in and return the specified config.json as a dict
    def readJson(self):

        # get the filepath of this script then. Replace with config filename
        path = "/".join(os.path.realpath(__file__).split("/")[:-1]) + "/" + self.configFileName

        # Error if the file required isn't there
        location = Path(path)
        if location.is_file() == False:
            self.errors.cantFindConfigJson(path)

        # Read in the json file
        with open(path, "r") as f:
            try:
                jsonAsDict = json.load(f)
            except:

                # Failed to load the json. Raise with a little context
                err = traceback.format_exc()
                self.errors.cantLoadJsonFile(err)

        return jsonAsDict



    # Attach the methods and store the order of calling them
    def createOrderAndArgs(self):

        # OrderAndArgs will be a tuple of dicts of method:args
        # i.e (inspectCols:{args), checkFooter{args})

        for i in range(0, len(self.configAsJson["processOrderDict"])):

            i = str(i)
            funcName = self.configAsJson["processOrderDict"][i]["func"]
            funcArgs = self.configAsJson["processOrderDict"][i]["args"]

            if i == "0": # First time only
                orderAndArgs = ({funcName:funcArgs})
            else:
                orderAndArgs = (orderAndArgs, {funcName:funcArgs})

        return orderAndArgs





