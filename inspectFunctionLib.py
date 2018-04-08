# -*- coding: utf-8 -*-

"""
Hold individual inspection functions that may be called on by the config.json being used.
"""

# Imports


# Local Imports
from sharedFunctionLib import *


# ###################################################################################
# Confirm that all columns specified as mandatory are present in the column headers

def confirmMandatoryColumns(df, resultsDict, args):

    cols = parseArgs("cols", args)

    resultLabel = "The following mandatory columns are missing:"

    for col in cols:
        if col not in df.columns.values:

            if resultLabel not in resultsDict:
                resultsDict.update({resultLabel:[]})

            resultsDict[resultLabel].append(col)

    return resultsDict


# ###################################################################################
# Check PER_ROW that AT_LEAST-ONE of the columns in this group has a value
# example: you might need to have either an observation or a datamarker
def confirmAtLeastOnePopulated(df, resultsDict, args):

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
        resultLabel = "At least one of these columns '{cols}' should always have a value. The following rows (showing {a} out of {b}) do not: ".format(a=len(resultsList), b=totalResults,cols=",".join(cols)) + ".".join(cols)
        resultsDict.update({resultLabel:resultsList})

    return resultsDict





# Controller
# ==========
# quick lookup for functions by string name
funcController = {
    "confirmMandatoryColumns":confirmMandatoryColumns,
    "confirmAtLeastOnePopulated":confirmAtLeastOnePopulated
}








