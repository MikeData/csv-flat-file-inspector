# -*- coding: utf-8 -*-

"""
Hold individual inspection functions that may be called on by the config.json being used.
"""

# Imports


# Local Imports
from sharedFunctionLib import *
from errors import simpleErrors
import requests

errors = simpleErrors()

# ###################################################################################
# Confirm that all columns specified as mandatory are present in the column headers

def confirmExpectedColumns(df, warnings, args):

    cols = parseArgs("cols", args)

    missing = []
    for col in cols:
        if col not in df.columns.values:
            missing.append(col)

    if len(missing) > 0:
        errors.unexpectedColumns(missing)

    return warnings


# ###################################################################################
# Check PER_ROW that AT_LEAST-ONE of the columns in this group has a value
# example: you might need to have either an observation or a datamarker
def confirmAtLeastOnePopulated(df, warnings, args):

    # Get columns
    cols = prepareColumnHeaders(df, args)

    # Create a sample frame with just the columns we are looking at merged into one
    # if there's only one columns - skip most of this
    sampleFrame = concatenateIntoFirstColumn(df, cols)

    # Return row indexes where the "cell" is still blank
    resultsList = sampleFrame[cols[0]][sampleFrame[cols[0]].astype(str) == ""]

    # Add one to row numbers, as headers are not indexed
    # i.e in pandas, row 1 of a spreadsheet is row 0
    resultsList = [x+1 for x in resultsList.index.values]
    totalResults = len(resultsList)

    # Limit result rows
    if len(resultsList) > 10:
        resultsList = resultsList[:10]

    if len(resultsList) > 0:
        errorText = "At least one of these columns '{cols}' should always have a value. The following rows (showing {a} out of {b}) do not: ".format(a=len(resultsList), b=totalResults,cols=",".join(cols)) + ".".join(cols)
        errors.missingItems(errorText)

    return warnings


# ###################################################################################
# Conpares a column of data to a trusted source
def compareItemsToSource(df, warnings, args):

    supportedTypes = ["json-api"]

    # Get type
    type = parseArgs("type", args)
    if type not in supportedTypes:
        errors.typeNotSupported(type)

    if type == "json-api":
        uri = parseArgs("uri", args)
        pattern = parseArgs("pattern", args)

        r = requests.get(uri)
        if r.status_code != 200:
            errors.cannotRequestJson(uri)

        data = r.json()

        iterationCounts = {"i":None, "j":None}
        iteratorList = ["i", "j"]

        steps = "data"
        correctItems = []
        for step in pattern.split(">"):

            if "EACH#" in step:
                it = iteratorList.pop(0)
                item = step[5:]
                iterationCounts[it] = len(eval(steps + '["' + item + '"]'))
                steps = steps + '["' + item + '"]' + "[" + it + "]"

            else:
                steps = steps + "['" + step + "']"

        if iterationCounts["i"] != None and iterationCounts["j"] != None:

            for i in range(0, iterationCounts["i"]):
                for j in iterationCounts["j"]:
                    correctItems.append(eval(steps))

        elif iterationCounts["i"] != None:

            for i in range(0, iterationCounts["i"]):
                correctItems.append(eval(steps))

        targetCol = type = parseArgs("target_col", args)
        col = df.columns.values[targetCol]
        itemsWeHave = df[col].unique()

        notFoundList = []
        for item in itemsWeHave:

            if item not in correctItems:
                notFoundList.append(item)

        if len(notFoundList) > 0:
            errors.incorrectItems(notFoundList, uri)

    return warnings


# ###################################################################################
# Check whether the level of sparsity in the dataset is enough to trigger a warning or error
def confirmAcceptableSparsity(df, warnings, args):

    warningLevel = parseArgs("warning_level", args)
    errorLevel = parseArgs("error_level", args)
    cols = parseArgs("cols", args)

    # Calculate sparsity
    rowCount = len(df)

    debug = []
    expected = 1
    for i in cols:
        dfCol = df.columns.values[i]
        expected = expected * len(df[dfCol].unique())
        debug.append(len(df[dfCol].unique()))

    sparsityAsZeroToOne = 1 - ((1 / rowCount) * expected)

    if sparsityAsZeroToOne > errorLevel:
        errors.sparsityError(sparsityAsZeroToOne)
    elif sparsityAsZeroToOne > warningLevel:
        warnings.update({"Sparsity is above the warning level":"Warning: {w}. Actual: {a}".format(w=warningLevel,a=sparsityAsZeroToOne)})

    return warnings


# Controller
# ==========
# A function controller, that calls functions based on name-as-string
def funcController(wantedFunc, df, resultsDict, args):

    funcLookup = {
        "confirmExpectedColumns": confirmExpectedColumns,
        "confirmAtLeastOnePopulated": confirmAtLeastOnePopulated,
        "confirmAcceptableSparsity": confirmAcceptableSparsity,
        "compareItemsToSource": compareItemsToSource
    }
    return funcLookup[wantedFunc](df, resultsDict, args)









