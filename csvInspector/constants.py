# -*- coding: utf-8 -*-

import json, os, traceback, requests
from pathlib import Path

from errors import simpleErrors
from inspectFunctionLib import *

# Defaults
DEFAULT_CONFIG = "config_V4.json"


KNOWN_APIS = {
    "local":"http://localhost:23200",                   # router for local cmd
    "dev":"https://api.dev.cmd.onsdigital.co.uk/",      # cmd develop environment
    "prod":"http://api.cmd.onsdigital.co.uk/",          # cmd live/production
}

# Build a config object from the specified json file
class config(object):

    def __init__(self, configFile):

        # Errors
        self.errors = simpleErrors()

        # Basic Input
        self.configFileUrl = configFile
        self.configAsDict = self.getJson()


    # Read in and return the specified config.json as a dict
    def getJson(self):

        if ".json" not in self.configFileUrl:
            self.errors.inputNotJson()

        r = requests.get(self.configFileUrl)
        if r.status_code != 200:
            self.errors.cannotRequestJson(self.configFileUrl)

        return r.json()






