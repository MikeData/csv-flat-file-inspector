# -*- coding: utf-8 -*-

from errors import simpleErrors
import pandas as pd


# ==================
# Reusable functions

# Get variables out of an args dictionary
def parseArgs(key, args):

    errors = simpleErrors()

    try:
        return args[key]
    except:
        errors.cannotParseAgs(key, args)


# Convert columns identified by index to headers in the CSV
def colIndexToString(df, cols):

    newCols = []
    for col in cols:

        if type(col) == str:
            newCols.append(col)
        else:
            col = df.columns.get_loc(col)
            newCols.append(col)

    return newCols



# Individual File Inspection Functions

# ###################################################################################
# Confirm that all columns specified as mandatory are present in the column headers

def confirmMandatoryColumns(df, resultDict, args):

    cols = parseArgs("cols", args)
    for col in cols:
        if col not in df.columns.values:

            if "confirmMandatoryColumns" not in resultDict:
                resultDict.update({"The following mandatory columns are missing:":[]})

            resultDict["confirmMandatoryColumns"].append(col)

    return resultDict


# ###################################################################################
# Check PER_ROW that AT_LEAST-ONE of the columns in this group has a value
# example: you might need to have either an observation or a datamarker
def confirmAtLeastOnePopulated(df, resultsDict, args):

    cols = parseArgs("cols", args)

    # Run it through an index>string conversion...just in case
    cols = colIndexToString(cols)

    # Create a sample frame with just the columns we are looking at merged into one
    # if there's only one columns - skip most of this

    if len(cols) > 1:
        sampleFrame[col] = df[col][0]
        sampleFrame.fillna("", inplace=True)

        for col in cols[1:]:
            sampleFrame[col] = sampleFrame[col] + df[col]

    else: # only one column
        sampleFrame[col] = df[col]
        col = [col]


    # Now we have a single column, look for blanks
    sampleFrame.fillna("", inplace=True)

    # Return row indexes where the "cell" is still blank
    resultFrame = sampleFrame[sampleFrame[col] == ""]

    return list(sampleFrame.index)





# Controller
# ==========
# quick lookup for functions by string name
funcController = {
    "confirmMandatoryColumns":confirmMandatoryColumns,
    "confirmAtLeastOnePopulated":confirmAtLeastOnePopulated
}








