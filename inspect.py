# -*- coding: utf-8 -*-

# Imports
import pandas as pd


# Imports from local
from constants import config, DEFAULT_CONFIG
from inspectFunctionLib import funcController
from errors import simpleErrors



class inspection(object):

    def __init__(self, fileName, configFile=DEFAULT_CONFIG):
        self.fileName = fileName
        self.errors = simpleErrors()

        # Load the config
        self.configFile = configFile
        self.cfg = config(configFile)

        # Simple validation of input
        self.validateInput()

        # Load csv into a dataframe
        self.df = pd.read_csv(fileName)

        # Results go here...
        self.resultsDict = {}

        # run
        self.inspect()



    def validateInput(self):

        if ".csv" not in self.fileName:
            self.errors.inputNotCSV()

        if ".json" not in self.configFile:
            self.errors.inputNotJson(self.configFile)


    def inspect(self):

        for funcAndArgsDict in self.cfg.orderAndArgs:

            # Seperate the dictionary
            func = [k for k in funcAndArgsDict.keys()][0]
            args = funcAndArgsDict[func]

            funcController[func](self.df, self.resultsDict, args)






inspection("BlueBook.csv")


