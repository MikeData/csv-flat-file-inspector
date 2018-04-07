import pandas as pd
import sys
from functools import reduce

# Main Vaidation Function. All validation calls are made here
# Returns a Tuple of plain-english descriptions of issues encountered.
def validateV4(df):

    # Assuming for now, can change as Needed
    mandatoryColumns = ['Time', 'Time_codelist', 'Geography', 'Geography_codelist']

    """
    Sequence of Checks
    ==================

    Function        |  Description (what its checking for)
    ---------------------------------------
    structure       |  Has V4_x column, has 2 Time and 2 Geography columns, has 2 columns per other dimension.
    emptyObs        |  If we dont have a data marker columns, make sure every row has an observation.
    emptyODM        |  If we do have data markers, make sure that EITHER it or obs have a value of some kind.
    addColCount     |  Check that V4_x numbering correctly matches number of additional pre-time columns.
    missingCells    |  Make sure that if a column is used (any cells with text) it has text for ALL rows.
    twoColDims      |  Make sure that evey dimension has at least one populated column.
    cleanCheck      |  Check for any invisible text-junk. Trailing whitespace, line endings etc
    sparsity        |  Warn if sparsity is detected.
    duplication     |  Check for any duplicated rows (in terms of dim combinations - disregards everything pre-Time)
    timeCheck       |  Make sure we've got no decimals in the Time column, and other oddities (Q6, 5 digit years etc)
    consistentCodes |  Where both codelist and labels are provided. Make sure there is a consistent 1-to-1 relationship.
    """

    # Add 2 to all values in a series (0 indexed frames + header row). Return as a coma delimited string
    def offset(Series):
        myList = []
        for s in Series:
            myList.append(str(s + 2))
        return ", ".join(myList)


    # Check the basic structure of the V$ loadfile
    def structure(df, fb):

        # Check the obs column for correct V4_ header
        obsColName = df.columns.values[0]
        if 'V4_' not in obsColName:
            fb = fb + ('Observation column header is wrong. Got {oc}'.format(oc=obsColName),)

        # check for the other mandatory headers
        for mc in mandatoryColumns:
            if mc not in df.columns.values:
                fb = fb + ('Cannot find a "{mc}" column. This is required'.format(mc=mc),)

        startOfTopics = df.columns.get_loc('Geography') + 1

        colsToCheck = df.columns.values[startOfTopics:]
        if len(colsToCheck) % 2 != 0:
            fb = fb + ('Every dimension needs to be represented by two columns but we have an odd number. Columns: ' + ", ".join(colsToCheck),)

        return fb


    #  we dont have data markings, check we have a value for observation
    def emptyObs(df, fb):
        if 'Data_Marking' not in df.columns.values:
            tempDf = df[df.columns.values[0]].map(lambda x: x == '')   # creates a series of True/False
            if len(tempDf[tempDf==True]) > 0:
                feedB = offset(tempDf[tempDf==True].index)
                fb = fb + ('Missing Observations, row numbers:' + feedB,)
        return fb


    # we do have data markings, make sure that EITHER (but not both) obs or data marking have a value
    def emptyODM(df, fb):
        if 'Data Marking' in df.columns.values:
            # Pretty much mash both columns together and see if the length > 0
            df['both'] = df[df.columns.values[0]].astype(str) + df['Data Marking'].astype(str)
            tempDf = df['both'].map(lambda x: len(str(x.strip())) < 1)   # creates a series of True/False
            if len(tempDf[tempDf==True]) > 0:
                feedB = offset(tempDf[tempDf==True].index)
                fb = fb + ('Both Obs and Data Markings are blank, row numbers: ' + feedB,)
        return fb


    # check that the number of additional pre-time columns is correct in the 2st column header (i.e V4_x)
    def addColCount(df, fb):

        # safety
        if 'Time_codelist' not in df.columns.values:
            return fb + ('Error: No "Time_codelist" found! This is a mandatory column.',)

        colCount = df.columns.get_loc('Time_codelist') - 1

        try:
            addCols = int(df.columns.values[0][-1:])
        except:
            fb = fb + ('This observation Column (first column) doesent appear to end in a number:' + df.columns.values[0],)
            return fb

        if addCols != colCount:
            fbList = df.columns.values[1:colCount+1]
            fb = fb + ('Additional column count wrong, {cc} expected (stated after underscore in first column header) but got: '.format(cc=str(addCols)) + ", ".join(fbList),)

        return fb


    # Check that when a column is used (has ANY non blank cells) it has values for ALL cells
    def missingCells(df, fb):

        try:
            def checkOneColumn(df, fb, col):
                # are there any values?
                tempSeries = df[col].map(lambda x: len(str(x.strip())) > 0)   # creates a series of True/False
                if len(tempSeries[tempSeries==True]) != len(df) and len(tempSeries[tempSeries==False]) != len(df):

                    if len(tempSeries[tempSeries==True]) > len(tempSeries[tempSeries==False]):
                        feedB = offset(tempSeries[tempSeries==False].index)
                        fb = fb + ('Blanks in Cells that are in use, column "{col}", row numbers: '.format(col=col) + feedB,)
                    else:
                        feedB = offset(tempSeries[tempSeries==True].index)
                        fb = fb + ('Some values in a largely empty column, name: "{col}", row numbers: '.format(col=col) + feedB,)
                return fb

            # from Time_codelist onwards
            start = df.columns.get_loc('Time_codelist')

            for col in df.columns.values[start:]:
                fb = checkOneColumn(df, fb, col)

        except:
            pass

        return fb

    # Make sure that each dimension (after geography) has AT LEAST one populated column
    # If its not FULLY populated (i. bits missing) other checks will flag it. This is just finding double blank columns.
    def twoColDims(df, fb):

        topicStart = df.columns.get_loc('Time') + 4

        # only execute if even number of columns (if there are not other checks will flag it)
        if len(df.columns.values[topicStart - 1:]) % 2 == 0:
            for coli in range(topicStart, len(df.columns.values), 2):
                notBlankCodeCount = len([x for x in df.iloc[:,coli-1].unique() if x != ''])
                notBlankNameCount = len([x for x in df.iloc[:,coli].unique() if x != ''])

                # Find Blanks
                if notBlankCodeCount == 0 and notBlankNameCount == 0: # they're both blank!
                    h = df.columns.values
                    fb = fb + ('Detected a topic dimension with two blank columns. "{h1}" and "{h2}" respectively.'.format(h1=h[coli-1], h2=h[coli]),)
        return fb

    # Make sure that NONE of the cells have trailing whitespace etc
    def cleanCheck(df, fb):
        missEntry = []
        for col in df.columns.values:
            for cell in df[col]:
                if type(cell) == str and cell != cell.strip():
                    statement = 'Non visible characters detected. Column "{col}" value "{val}".'.format(col=col, val=cell)
                    if statement not in missEntry:
                        missEntry.append(statement)
        for me in missEntry:
            fb = fb + (me,)
        return fb

    # Warn if the dataset appears to have sparsity
    def sparsity(df, fb):

        cube = 1 * len(df['Geography_codelist'].unique())
        cube *= len(df['Time'].unique())

        topicStart = df.columns.get_loc('Time') + 4
        for coli in range(topicStart, len(df.columns),2):
            if len(df[df.columns.values[coli]].unique()) > 1:
                cube *= len(df[df.columns.values[coli]].unique())
            else:
                cube *= len(df[df.columns.values[coli-1]].unique())

        if cube != len(df):
            fb = fb + ('Sparsity Detected. We have {r} rows but a datacube with {c} combinations'.format(c=cube, r=len(df)),)
        return fb


    # Check for any rows that have duplication (not incuding everything pre timecodelist)
    def duplication(df, fb):
        """
        We're gonna use pandas Dataframe.duplicate() for this. More efficient than anything I can scratch-build.
        """
        for coli in range(df.columns.get_loc('Time')-1,0, -1):  # go in reverse so we dont muddle the index mid-drop
            print('Dropping: ', df.columns.values[coli])
            df = df.drop(df.columns.values[coli], axis=1)
        dupes = df.duplicated()[df.duplicated()==True]
        if len(dupes) > 0:
            fb = fb + ('The following rows are duplicates of other rows: ' + offset(dupes.index)[:10],)
        return fb


    # Make sure none of the time cells have been taken as decimal
    def timeCheck(df, fb):

        # -------------
        # DECIMAL TIME
        decTime = []

        for cell in df['Time']:
            if '.' in cell and cell not in decTime:
                decTime.append(cell)
        if len(decTime) > 0:
            fb = fb + ('Decimal Time Detected: ' + ", ".join(decTime),)

        # -----------------------
        # YEARS MUST BE 4 DIGITS
        not4Years = []
        for cell in df['Time'][df['Time_codelist'] == 'Year']:
            if len(cell) != 4 and cell not in not4Years:
                not4Years.append(cell)
            else:
                try:
                    cell = int(cell)   # to catch any masquerading 4 char strings
                except:
                    if cell not in not4Years:
                        not4Years.append(cell)
        if len(not4Years) > 0:
            fb = fb + ('Time type is year but the following to not appear to be 4 digit numbers: ' + ", ".join(not4Years),)

        # -----------------------------------------
        # QUARTER TYPES MUST HAVE Q1, Q2, Q3 or Q4
        notQuarters = []
        for cell in df['Time'][df['Time_codelist'] == 'Quarter']:
            found = [x for x in cell.split() if x in ['Q1', 'Q2', 'Q3', 'Q4']]
            if len(found) == 0 and cell not in notQuarters:
                notQuarters.append(cell)
        if len(notQuarters) > 0:
            fb = fb + ('Time types given as "Quarter" but these cell dont have a valid quarter specified: ' + ", ".join(notQuarters),)

        return fb


    # Checks that where codes:lables are used for a dimension they are consistent
    def consistentCodes(df, fb):

        # if something is double mapped, whats it double mapped to?
        def whichOther(df, repeatValue, detectedInCol, mappedToCol):
            mappedTo = df[df[detectedInCol] == repeatValue]
            mappedTo = mappedTo[mappedToCol].unique()
            return mappedTo

        start = df.columns.get_loc('Geography')
        for coli in range(start+2, len(df.columns.values),2):

            # save some typing ...
            codeColName = df.columns.values[coli-1]
            labelColName = df.columns.values[coli]

            # Make sure neither column is blank - that'll throw a false postitive
            # i.e "" is mapped to X, Y and Z
            noBlanks = True
            if len(df[codeColName].unique()) == 0 or len(df[labelColName].unique()) == 0:
                noBlanks = False

            if list(df[labelColName].unique())[0] == '':
                noBlanks = False

            if list(df[codeColName].unique())[0] == '':
                noBlanks = False

            if noBlanks:

                #print (len(df[codeColName].unique()), df[codeColName].unique())
                #print (len(df[labelColName].unique()), df[labelColName].unique())

                # mash together, get unqiue combos then split out into two lists
                # if an item appears more than once in either list....its mapped to more than 1 thing - bad!
                df['both'] = df[codeColName] + '|' + df[labelColName]
                combos = df['both'].unique()
                codes = [x.split('|')[0] for x in combos]
                labels = [x.split('|')[1] for x in combos]

                # did any codes appear more than once?
                if len(codes) != len(set(codes)):
                    repeatValue = [x for x in codes if len([y for y in codes if y == x]) != 1][0]
                    other = whichOther(df, repeatValue, codeColName, labelColName)
                    fb = fb + ('The code "{c}" is mapped to all the following codes: {o}'.format(c=repeatValue,o=other),)

                # did any labels appear more than once?
                if len(labels) != len(set(labels)):
                    repeatValue = [x for x in labels if len([y for y in labels if y == x]) != 1][0]
                    other = whichOther(df, repeatValue, labelColName, codeColName)
                    fb = fb + ('The label "{c}" is mapped to all the following codes: {o}'.format(c=repeatValue,o=other),)

        return fb


     # #########################
     # CALL ON FUNCTIONS IN TURN
     # #########################
     fb = ()  # feedback goes here. Simple one line plain english statments.
     for func in [structure, emptyObs, emptyODM, addColCount, missingCells,
                  twoColDims, cleanCheck, sparsity, duplication, timeCheck, consistentCodes]:
         fb = func(df, fb)

     return fb
  
