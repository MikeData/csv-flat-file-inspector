
# Imports
import pandas as pd

# Local imports
from constants import *
from errors import simpleErrors
from inspectFunctionLib import funcController
from pprint import pprint

class controller(object):

    def __init__ (self, source, configUrl, env):

        self.errors = simpleErrors()
        self.cfg = config(configUrl)

        if env not in KNOWN_APIS.keys():
            self.errors.resolveEnvironment(env)

        if ".csv" not in source:
            self.errors.inputNotCSV()

        try:
            self.df  = pd.read_csv(source)
        except:
            err = traceback.format_exc()
            self.errors.cannotLoadCSV(err)

        self.warnings = {}

        # Let's get to business
        self.inspect()


    # Call the action validation functions
    def inspect(self):

        for i in range(0, len(self.cfg.configAsDict["process_order_dict"])):

            funcDefinition = self.cfg.configAsDict["process_order_dict"][str(i)]
            funcName = funcDefinition["func"]
            funcArgs = funcDefinition["args"]
            self.warnings = funcController(funcName, self.df, self.warnings, funcArgs)

        return self.warnings


def inspector(source, configUrl, env="local"):
    return controller(source, configUrl, env).warnings
