# -*- coding: utf-8 -*-

"""
Shared function lib holds small shared functionaity used by multiple inspection functions.
"""

# Imports
import pandas as pd
import json
import traceback

# Local Imports
from errors import simpleErrors

# Get requested variables out of an args dictionary
def parseArgs(key, args):

    try:
        return args[key]
    except:
        errors = simpleErrors()
        errors.cannotParseAgs(key, args)


# Convert columns identified by index to string headers in the CSV
def colIndexToString(df, cols):

    newCols = []
    for col in cols:

        if type(col) == str:
            newCols.append(col)
        else:
            col = df.columns.values[col]
            newCols.append(col)

    return newCols


# Create single list of strings from mixed int&str col and col_optional args
def prepareColumnHeaders(df, args):

    # Add the column and optional columns to a single list
    if "cols" in args.keys():
        cols = parseArgs("cols", args)
    else:
        cols = []

    if "cols_optional" in args.keys():
        optCols = args["cols_optional"]

    # Remove any optional cols that aren't in this dataframe.
    for col in optCols:
        if col in df.columns.values:
            cols.append(optCols)

    # Run it through an index>string conversion to standardise
    cols = colIndexToString(df, cols)

    return cols


# Returns a single column dataframe from a list of columns. i.e ["col1", "col2"] becomes ["col1"]. Values are concatenated
def concatenateIntoFirstColumn(df, columnList):

    # Populate a new dataframe with just the first column
    newDataFrame = pd.DataFrame()

    startColumn = columnList[0]
    newDataFrame[startColumn] = df[startColumn]

    # If its a list of one, return it
    if len(columnList) == 1:
        newDataFrame.fillna("", inplace=True)
        return newDataFrame

    else:  # concatentate

        for column in columnList[1:]:
            newDataFrame[startColumn] = newDataFrame[startColumn] + df[column]

        # as always
        newDataFrame.fillna("", inplace=True)

        return newDataFrame
