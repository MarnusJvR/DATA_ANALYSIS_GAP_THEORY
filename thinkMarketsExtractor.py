import pandas
from datetime import date
from datetime import datetime
import datetime
import numpy
import csv
import os.path

# Voley Drive is gapclose then return to 50% top open the trade. TP is at 2R\
# Straight drive is price going to 50% then returning to open position to open the trade


def operator(pair):
    print(pair)
    # halveGapValue is gold standard list for halvegapvalues
    # halveGapValue = 50% of the gap value (Open + prevclose)/2
    # prevClosingValueC = previous closing values defined line 158
    # closingval = previous closing values for DF1 NOT df2
    # openListDF2 = open values of DF2
    # gapClosedNumStr contains a string of all the positions where price goes through gap close
    # priceMoveOpenCount contains all values where price returns through open
    # halveHitPosStr contains all values of going through 50% value
    def floatConverter(listConvert):
        convertedList = []
        for items in listConvert:
            convertedString = ''
            for chars in items:
                if chars != ',':
                    convertedString = convertedString + chars
                else:
                    convertedString = convertedString + '.'
            convertedList.append(convertedString)
        return convertedList
    # set your values here
    checkSetUS = False
    if pair == 'US3030':
        fileExtractname = pair + '.csv'
        stoploss = 100
        negativegapsizesetnumber = -15
        gapsizesetnumber = 15
        checkSetUS = True
    else:
        if pair == 'DE3030':
            fileExtractname = pair + '.csv'
            stoploss = 100
            negativegapsizesetnumber = -15
            gapsizesetnumber = 15
            checkSetUS = True
        else:
            fileExtractname = pair + ' 1 min.csv'
    # fileExtractname ='EURNZD30.csv'
    fileAll = 'dfall.csv'
    testval = pair[3:]
    if not checkSetUS:
        if testval == 'JPY':
            stoploss = 0.15
            negativegapsizesetnumber = -0.15
            gapsizesetnumber = 0.15
        else:
            stoploss = 0.0015
            negativegapsizesetnumber = -0.0015
            gapsizesetnumber = 0.0015
    # this is the amount of candles you want to check
    rangeHigh = 4000
    # take the opening value of the first itteration and stick it in here. this avoids a false open gap
    # Creating the dataframe
    df1 = pandas.read_csv(fileExtractname, header = None)
    # dfall = pandas.read_csv(fileAll, header = None)
    # setting the columns
    df1.columns = ["DateTime","Opening Value", "High","low","Close Value"]
    #
    # This whole data set is in reverse
    #
    dateList = list(df1.loc[:, 'DateTime'])
    closingValues = list(df1.loc[:, 'Close Value'])
    # myopeningnumberlist = list(df1.loc[:, 'Opening Value'])
    openValueList = list(df1.loc[:, 'Opening Value'])
    # openValueList = floatConverter(openValueList)
    highList = list(df1.loc[:, 'High'])
    # highList = floatConverter(highList)
    lowList = list(df1.loc[:, 'low'])
    # lowList = floatConverter(lowList)
    dateString = ''
    dateStringList = []
    finalDateStr = ''
    timeString = ''
    timeStringList = []
    # This takes input of dateTime Strings like: 2020/10/30 16:55
    #
    # Extract string values for time and date
    #
    for items in dateList:
        dateString = items[:10]
        # Currently date is in this format: 2020/08/03
        # I need it in this format:2004.06.17
        for letters in dateString:
            if letters != '/':
                finalDateStr = finalDateStr + letters
            else:
                finalDateStr = finalDateStr + '.'
        dateStringList.append(finalDateStr)
        timeString = items[11:]
        timeStringList.append(timeString)
        finalDateStr = ''
    # Currently date is in this format: 2020/08/03
    # I need it in this format:2004.06.17
    # conversion list
    # loop through list to convert strings to date structures
    actualDateList = []
    for dates in dateStringList:
        new_date_object = datetime.datetime.strptime(dates, '%Y.%m.%d').date()
        actualDateList.append(new_date_object)
    df1["DATE_OBJECT"] = actualDateList
    #
    # EXTRACT TIME
    #
    df1["Time"] = timeStringList
    df1 = df1.drop("DateTime",1)
    weekdayList = []
    # Here I create the weekday field
    count = 0
    for date in actualDateList:
        weekday = date.weekday()
        weekdayList.append(weekday)
        count = count + 1
    df1['Weekday'] = weekdayList
    # Here I push the opening value of the first itteration into the list to not effect outcome
    closingvalueinsertfirstitteration  = openValueList[0]
    closingValues.insert(0, closingvalueinsertfirstitteration)
    closingValues.pop()
    df1['PREV_CLOSING_VAL'] = closingValues
    # But I already have pair value I dont need this
    currencyPairing = pair
    df1.to_csv('fullset.csv')
    difList = []
    count = 0
    # gap size is calculated by taking the current opening value and subtracting the prev closing value
    # If the prev closing value was higher than opening number EXPECT NEGATIVE NUMBER
    # If opening is higher than pre closing expect POSITIVE NUMBER
    # Here I am still working with df1
    for num in openValueList:
        newvalue = round((float(num) - float(closingValues[count])),10)
        count = count + 1
        difList.append(newvalue)

    df1['GAP_SIZE'] = difList
    # here I need to progresively elemenate weekdays.
    # there might be a more effective way to do this
    # Monday= 0 Tuesday = 1 Wednesday = 2 Thursday = 3 Friday = 4
    # We want closing on 4 ! opening on 1 !
    df2 = df1[df1.Weekday != 1]
    df2 = df2[df2.Weekday != 2]
    df2 = df2[df2.Weekday != 3]
    df2 = df2[df2.Weekday != 5]
    df2 = df2[df2.Weekday != 6]
    closingList = list(df2.loc[:,'Close Value'])
    # Now its time to check where gaps had opened.
    # Only checking on the over-weekend gap
    df2.to_csv('DF2.csv')
    gapList = list(df2.loc[:, 'GAP_SIZE'])
    myTime = list(df2.loc[:, 'Time'])
    myDate = list(df2.loc[:, 'DATE_OBJECT'])


    thisCount = 0
    gapIdentifyer = []
    if pair == 'DE3030' or pair == 'US3030':
        for nums in gapList:
            date2 = myDate[thisCount]
            year = date2.year
            date2 = myDate[thisCount]
            openTime = myTime[thisCount]
            prevDate = myDate[thisCount - 1]
            closingTime = myTime[thisCount - 1]
            newDate = date2 - prevDate
            if year >= 2015:
                if newDate.days == 3:
                    if nums >= gapsizesetnumber or nums <= negativegapsizesetnumber:
                        gapIdentifyer.append("GAP")
                    else:
                        gapIdentifyer.append("NONE")
                else:
                    gapIdentifyer.append("NONE")
            else:
                gapIdentifyer.append('NONE')
            thisCount = thisCount + 1
    else:
        for nums in gapList:
            date2 = myDate[thisCount]
            year = date2.year
            openTime = myTime[thisCount]
            prevDate = myDate[thisCount - 1]
            closingTime = myTime[thisCount - 1]
            newDate = date2 - prevDate
            if newDate.days == 3:
                if nums >= gapsizesetnumber or nums <= negativegapsizesetnumber:
                    gapIdentifyer.append("GAP")
                else:
                    gapIdentifyer.append("NONE")
            else:
                gapIdentifyer.append("NONE")
            thisCount = thisCount + 1

    df2["GAP_CLASS"] = gapIdentifyer
    gapClassList = list(df2.loc[:,'GAP_CLASS'])
    gapCounter = 0
    for gaps in gapClassList:
        if gaps == 'GAP':
            gapCounter=gapCounter+1
    print('TOTAL GAPS : ' + str(gapCounter))
    # now to move into gapclosings
    count = 0
    High = list(df2.loc[:, 'High'])
    Low = list(df2.loc[:, 'low'])
    gapsizelist = list(df2.loc[:,'GAP_SIZE'])
    prevClosingValueC = list(df2.loc[:, 'PREV_CLOSING_VAL'])
    counter = 0
    gapS = 0
    tradeList =[]
    GapClosedNum =[]
    gapClosedNumStr = []
    # this loops check what gaps was closed
    stopNumber = len(Low)
    stopHighNumber = len(High)
    gapB = False
    forgaplist = []
    stopList = len(Low)

    for gaps in gapClassList:
        gapsizeCheck = gapsizelist[counter]
        if gaps == 'GAP':
            if gapsizeCheck > 0:
                for i in range(0, rangeHigh):
                    if counter + i < stopList:
                        if Low[counter + i] <= (prevClosingValueC[counter]):
                            forgaplist.append(i)
                            gapB = True
                if not gapB:
                    tradeList.append('NONE')
                    GapClosedNum.append('NONE')
                    gapClosedNumStr.append('NONE')
                else:
                    mynum = forgaplist[0]
                    gapCloseStr = ''
                    for numbers in forgaplist:
                        gapCloseStr = gapCloseStr + str(numbers) + ','
                    gapClosedNumStr.append(gapCloseStr)
                    tradeList.append('GAP CLOSED')
                    GapClosedNum.append(mynum)
            if gapsizeCheck < 0:
                for i in range(0, rangeHigh):
                    if counter + i < stopList:
                        if High[counter + i] >= (prevClosingValueC[counter]):
                            forgaplist.append(i)
                            gapB = True
                if not gapB:
                    tradeList.append('NONE')
                    GapClosedNum.append('NONE')
                    gapClosedNumStr.append('NONE')
                else:
                    mynum = forgaplist[0]
                    gapCloseStr = ''
                    for numbers in forgaplist:
                        gapCloseStr = gapCloseStr + str(numbers) + ','
                    gapClosedNumStr.append(gapCloseStr)
                    tradeList.append('GAP CLOSED')
                    GapClosedNum.append(mynum)
        else:
            tradeList.append('NONE')
            GapClosedNum.append('NONE')
            gapClosedNumStr.append('NONE')
        gapB = False
        counter = counter + 1
        forgaplist.clear()
        mynum = 0

    # Function that will generate stoploss values
    # takes trade open value and sl size
    def stopLossValues(tradeOpenList, SLsize):
        stopLossFunc = []
        counter = 0
        myBool = False
        stopFunc = 0
        for gaps in gapClassList:
            gapsizeCheck = gapsizelist[counter]
            if gaps == 'GAP':
                if gapsizeCheck > 0:
                    stopFunc = tradeOpenList[counter] - SLsize
                    stopLossFunc.append(stopFunc)
                if gapsizeCheck < 0:
                    stopFunc = tradeOpenList[counter] + SLsize
                    stopLossFunc.append(stopFunc)
            else:
                stopLossFunc.append('NONE')
            counter = counter + 1
        return stopLossFunc


    def checkStopLossPositions(stopLossImport):
        # stopLossImport must contain a list of actual price values
        counter = 0
        customStopStr = []
        # this loops check what gaps was closed
        gapB = False
        forgaplist = []
        for gaps in gapClassList:
            gapsizeCheck = gapsizelist[counter]
            if gaps == 'GAP':
                if gapsizeCheck > 0:
                    for i in range(0, rangeHigh):
                        if counter + i < stopList:
                            if Low[counter + i] <= (stopLossImport[counter]):
                                forgaplist.append(i)
                                gapB = True
                    if not gapB:
                        customStopStr.append('NONE')
                    else:
                        Str = ''
                        for numbers in forgaplist:
                            Str = Str + str(numbers) + ','
                        customStopStr.append(Str)
                if gapsizeCheck < 0:
                    for i in range(0, rangeHigh):
                        if counter + i < stopList:
                            if High[counter + i] >= (stopLossImport[counter]):
                                forgaplist.append(i)
                                gapB = True
                    if not gapB:
                        customStopStr.append('NONE')
                    else:
                        Str = ''
                        for numbers in forgaplist:
                            Str = Str + str(numbers) + ','
                        customStopStr.append(Str)
            else:
                customStopStr.append('NONE')
            gapB = False
            counter = counter + 1
            forgaplist.clear()
            mynum = 0
        return customStopStr
    # def takes two lists:
    # 1) list of sl positions
    # 2) list of sl values
    def straightProfitFunc(stopLossPositions, stopLossValues, slPip):
        profitTrade = 0
        LossTrade = 0
        simTrade = 0
        un = 0
        posL = False
        stopLossPosList = []
        forCheckTP = []
        forCheckTP2 = []
        forCheckMom = []
        posTP = False
        tots2 = 0
        mistake = 0
        openV = 0
        mistakestr = ''
        finPrintMis = ''
        count = 0
        halvegap = 0
        stoplossSize = 0
        takeProfitSize = 0
        Rvalue = 0
        totalR = 0
        writeStr = ''
        writeStr2 = ''
        specialStraghtListPL = []

        # at this point i feel i know when reversetrade options open
        # I see where there was chances for stop loss in this block
        # if items != 'NONE' and GapClosedNum[count] == 'NONE':
        myBool = False
        for items in momentumOpenHitPos:
            if reverseOption[count] == 'REVERSE TRADE HERE':
                #
                # R-Value
                #
                openV = openListDF2[count]
                sl = stopLossValues[count]
                stoplossSize = openV - sl
                if stoplossSize < 0:
                    stoplossSize = stoplossSize * -1
                # only have reverse take profit values for instances where price goes to that value
                if reverseTakeProfitValue[count] != 'NONE':
                    takeProfitSize = openV - reverseTakeProfitValue[count]
                if takeProfitSize < 0:
                    takeProfitSize = takeProfitSize * -1
                Rvalue = (takeProfitSize / stoplossSize)
                #
                # Algo
                #
                tots2 = tots2 + 1
                # in this case we check the new Stop Loss position string
                # this list carries NONE values for those instances where price does not go through SL
                halveString = stopLossPositions[count]
                if halveString != 'NONE':
                    forCheckMom = extractor(halveString)
                    for positions in forCheckMom:
                        # So i check if there is cases where price goes through sl value after trade is opened
                        # this means there is a chance for stop loss
                        if positions > items:
                            posL = True
                            stopLossPosList.append(positions)
                            # now i have a list that either contains the positions of going through stop loss or NONE if price
                            # did not go through stop loss
                    #         so if there is a position where price went through sl then we can say there is a chance for SL
                if posL:
                    # here we now know that there is in fact a value for SL
                    # we now check if there is a value for TP
                    if reverseTakeProfitStr[count] != 'NONE':
                        forCheckTP = extractor(reverseTakeProfitStr[count])
                        # first i check if there are values for take profit after trade open position
                        for positions in forCheckTP:
                            if positions > items:
                                posTP = True
                                forCheckTP2.append(positions)
                    else:
                        #
                        #  BLOK1
                        #
                        # We have no value for take profit but plenty values for sl
                        print('-------------')
                        LossTrade = LossTrade + 1
                        specialStraghtListPL.append('LOSS')
                        myBool = True
                        mistakestr = mistakestr + '_BLOK1_'
                        mistake = mistake + 1
                        print('SPECIAL Loss Reverse Trade KKK On ' + str(
                            dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                            halveGapValue[count]) + ' at the position ' + str(
                            halveHitPos[
                                count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                            momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                            reverseTakeProfitValue[
                                count]) + '\nStop loss is set at ' + str(stopLossValues[count]) + '\nTake profit was never reached ' + '\n stop loss was reached at the following position ' + str(
                            stopLossPosList[
                                0]) + '\n----------------------------------------------------------------------------\n')
                        # here i kno that there no value for TP but there is for SL
                    if posTP:
                        # this can only be true if there was a value for str
                        if stopLossPosList[0] < forCheckTP2[0]:
                            #
                            #  BLOK 2
                            #
                            print('-------------')
                            specialStraghtListPL.append('LOSS')
                            LossTrade = LossTrade + 1
                            myBool = True
                            loss = loss + 1

                            print('SPECIAL Loss Reverse Trade On ' + str(
                                dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                                halveGapValue[count]) + ' at the position ' + str(
                                halveHitPos[
                                    count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                                momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                                reverseTakeProfitValue[count]) + '\nTake profit was reached at the following position ' + str(
                                forCheckTP2[0]) + '\n stop loss was reached at the following position ' + str(
                                stopLossPosList[0]) + '\nStop loss is set at ' + str(stopLossValues[count]) + '\n----------------------------------------------------------------------------\n')
                        if stopLossPosList[0] > forCheckTP2[0]:
                            #
                            # BLOK 3
                            #
                            print('-------------')
                            profitTrade = profitTrade + 1
                            AP = ('profit', Rvalue)
                            specialStraghtListPL.append(AP)
                            myBool = True
                            totalR = totalR + Rvalue
                            mistake = mistake + 1
                            mistakestr = mistakestr + "_BLOK3_"
                            #
                            #
                            #
                            print('SPECIAL Profit Reverse with Rvalue ' + (str(Rvalue)) + ' Trade On ' + str(
                                dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                                halveGapValue[count]) + ' at the position ' + str(
                                halveHitPos[
                                    count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                                momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                                reverseTakeProfitValue[count]) + '\nTake profit was reached at the following position ' + str(
                                forCheckTP2[0]) + '\n stop loss was reached at the following position ' + str(
                                stopLossPosList[0]) + '\nStop loss is set at ' + str(stopLossValues[count]) + '\n----------------------------------------------------------------------------\n')
                        if stopLossPosList[0] == forCheckTP2[0]:
                            #
                            # BLOK 4
                            #
                            print('-------------')
                            simTrade = simTrade + 1
                            specialStraghtListPL.append('SIM')
                            print('SPECIAL SIM Reverse Trade On ' + str(
                                dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                                halveGapValue[count]) + ' at the position ' + str(
                                halveHitPos[
                                    count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                                momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                                reverseTakeProfitValue[count]) + '\nTake profit was reached at the following position ' + str(forCheckTP2[0])+ '\nStop loss is set at ' + str(stopLossValues[count]) + '\n----------------------------------------------------------------------------\n')
                    else:
                        # if reverseTakeProfitstr was NONE
                        # here we had two ittereations of what could have happened:
                        # 1) there was a NONE value for reverseTakeProfitStr so our check bolean could not go to true
                        # 2) or there was a value for above but no TP values for before trade opened.
                        # Both of these results in this section being activated
                        if reverseTakeProfitStr[count] != 'NONE':
                            specialStraghtListPL.append('LOSS')
                            LossTrade = LossTrade + 1
                            myBool = True
                            print('SPECIAL Loss Reverse Trade where price reached TP before open and lost after On ' + str(
                                dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                                halveGapValue[count]) + ' at the position ' + str(
                                halveHitPos[
                                    count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                                momentumOpenHitPos[
                                    count])+ '\nStop loss is set at ' + str(stopLossValues[count]) + '\n----------------------------------------------------------------------------\n')
                else:
                    # now we kno there no value for SL but there might be a value for TP
                    # check if there is a value for reverseTakeProfitstr
                    # none value is assigned for instances where price never goes through TP
                    if reverseTakeProfitStr[count] != 'NONE':
                        forCheckTP = extractor(reverseTakeProfitStr[count])
                        # first i check if there are values for take profit after trade open position
                        for positions in forCheckTP:
                            if positions > items:
                                posTP = True
                                forCheckTP2.append(positions)
                        if posTP:
                            # now we know there is no value for sl and a value for tp
                            #
                            # BLOK 6
                            #
                            profitTrade = profitTrade + 1
                            AP = ('profit', Rvalue)
                            totalR = totalR + Rvalue
                            specialStraghtListPL.append(AP)
                            myBool = True
                            mistake = mistake + 1
                            mistakestr = mistakestr + "_BLOK6_"
                            print('SPECIAL Profit Reverse with Rvalue ' + (str(Rvalue)) + ' Trade On ' + str(
                                dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                                halveGapValue[count]) + ' at the position ' + str(
                                halveHitPos[
                                    count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                                momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                                reverseTakeProfitValue[count]) + '\nTake profit was reached at the following position ' + str(
                                forCheckTP2[0]) + '\n stop loss was never reached' + '\nStop loss is set at ' + str(stopLossValues[count]) + '\n----------------------------------------------------------------------------\n')
                        else:
                            # here we say there is no value for SL
                            # and no value for TP
                            un = un + 1
                            #
                            # Blok 7
                            #
                            specialStraghtListPL.append('UNDETERMINED')
                            myBool = True
                            mistake = mistake + 1
                            mistakestr = mistakestr + "_BLOK7_"
                            print('SPECIAL UNDETERMINED Reverse Trade On ' + str(
                                dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                                halveGapValue[count]) + ' at the position ' + str(
                                halveHitPos[
                                    count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                                momentumOpenHitPos[count]) + '\nThe trade never reached SL or TP after being opened' + '\nStop loss is set at ' + str(stopLossValues[count])  + '\n----------------------------------------------------------------------------\n')
                    else:
                        #
                        # Blok 8
                        #
                        # print('-------------')
                        un = un + 1
                        specialStraghtListPL.append('UNDETERMINED')
                        myBool = True
                        mistake = mistake + 1
                        mistakestr = mistakestr + "_BLOK8_"
                        print('SPECIAL UNDETERMINED KKK Reverse Trade On ' + str(
                            dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                            halveGapValue[count]) + ' at the position ' + str(
                            halveHitPos[
                                count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                            momentumOpenHitPos[count]) + '\nThe trade never reached SL or TP after being opened' + '\nStop loss is set at ' + str(stopLossValues[count])  + '\n----------------------------------------------------------------------------\n')
            else:
                specialStraghtListPL.append('NONE')
                myBool = True
            stopLossPosList.clear()
            forCheckTP.clear()
            forCheckTP2.clear()
            forCheckMom.clear()
            myBool = False
            loss = False
            posL = False
            posTP = False
            count = count + 1
            mistake = 0
            mistakestr = ''
        print('<><><><><><><><><><><><><><><><><><><><><><><><><<><><><><><><><><><><><><')
        print('TOTAL SPECIAL STRAIGHT DRIVE ' + str(tots2))
        print('PROFIT SPECIAL STRAIGHT DRIVE ' + str(profitTrade))
        print('LOSS SPECIAL STRAIGHT DRIVE ' + str(LossTrade))
        print('UNDETERMINED SPECIAL STRAIGHT DRIVE ' + str(un))
        print('SIM SPECIAL STRAIGHT DRIVE ' + str(simTrade))
        print('TOTAL R ' + str(totalR))
        print('<><><><><><><><><><><><><><><><><><><><><><><><><<><><><><><><><><><><><><')
        specialStraightDrive = ''
        specialStraightDrive = '<><><><><><><><><><><><><><><><><><><><><><><><><<><><><><><><><><><><><><' + '\nTOTAL SPECIAL STRAIGHT DRIVE ' + str(tots2) + '\nPROFIT SPECIAL STRAIGHT DRIVE ' + str(profitTrade) + '\nLOSS SPECIAL STRAIGHT DRIVE ' + str(LossTrade) + '\nUNDETERMINED SPECIAL STRAIGHT DRIVE ' + str(un) + '\nSIM SPECIAL STRAIGHT DRIVE ' + str(simTrade) + '\nTOTAL R ' + str(totalR) + '\n<><><><><><><><><><><><><><><><><><><><><><><><><<><><><><><><><><><><><><'
        straightTup = ()
        straightTup = (str(slPip), str(pair), 'Straight', tots2, profitTrade, LossTrade, '', simTrade, un, totalR)
        return specialStraghtListPL, specialStraightDrive, straightTup

    def voleyProfFunc(stopLossPositions, stopLossValues, slPip):
        # CHECK VOLEY drive PROFIT
        count = 0
        vLoss = 0
        vTotal = 0
        vSim = 0
        vUn = 0
        vProfit = 0
        forCheckTP = []
        forCheckTP2 = []
        writeStr2 = ''
        voleyDropPL = []
        posTP = False
        closeBoon = False
        forCloseLoop = []
        myBool = False
        openV = 0
        stoplossSize = 0
        Rvalue = 0
        vR = 0

        for items in voleyOpenPos:
            if items != 'NONE':
                # if there is an open position volley trade is true
                openNum = items
                openV = halveGapValue[count]
                sl = stopLossValues[count]
                stoplossSize = openV - sl
                if stoplossSize < 0:
                    stoplossSize = stoplossSize * -1
                # only have reverse take profit values for instances where price goes to that value
                if voleyTakeProfit[count] != 'NONE':
                    takeProfitSize = openV - voleyTakeProfit[count]
                if takeProfitSize < 0:
                    takeProfitSize = takeProfitSize * -1
                Rvalue = (takeProfitSize / stoplossSize)
                closeNum = stopLossPositions[count]
                if closeNum != 'NONE':
                    forCheckMom = extractor(closeNum)
                    for positions in forCheckMom:
                        # if there is value for gapclose after trade is opened we have chance for sl
                        if positions > openNum:
                            # in this case there is a chance for stoploss
                            closeBoon = True
                            forCloseLoop.append(positions)
                if closeBoon:
                    #
                    # here we now know that there is in fact a value for SL
                    # we now check if there is a value for TP
                    #
                    if voleyTakeProfitPosStr[count] != 'NONE':
                        #
                        # Value for SL and TP
                        #
                        # No else block cause the undetermined is caught below
                        forCheckTP = extractor(voleyTakeProfitPosStr[count])
                        # first i check if there are values for take profit after trade open position
                        for positions in forCheckTP:
                            # check if there is positions for tp after trade is open
                            if positions > openNum:
                                posTP = True
                                forCheckTP2.append(positions)
                        if posTP:
                            #
                            #
                            # Values for tp after trade is opened & values for SL
                            #
                            #
                            if forCloseLoop[0] > forCheckTP2[0]:
                                #
                                # Trade went through TP before going through SL
                                #
                                AP = ('profit', Rvalue)
                                voleyDropPL.append(AP)
                                vR = vR + Rvalue
                                myBool = True
                                checkBool = True
                                vProfit = vProfit + 1
                                vTotal = vTotal + 1
                                print('Profit voley with RVALUE ' + str(Rvalue) + 'on ' + str(
                                    dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                                    GapClosedNum[
                                        count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                                    voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                                    voleyTakeProfit[
                                        count]) + '\nTake profit was reached at the following positionS ' + str(
                                    forCheckTP2[0]) + '\nStopLoss for this trade was set at ' + str(stopLossValues[count]) +  '\n----------------------------------------------------------------------------\n')
                                print('-------------')
                                # writeStr2 = writeStr2 + 'Profit voley on ' + str(
                                #     dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                                #     GapClosedNum[
                                #         count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                                #     voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                                #     voleyTakeProfit[
                                #         count]) + '\nTake profit was reached at the following positionS ' + str(
                                #     forCheckTP2[
                                #         0]) + '\n----------------------------------------------------------------------------\n'
                            if forCloseLoop[0] < forCheckTP2[0]:
                                #
                                # SL was was hit before the TP
                                #
                                voleyDropPL.append('LOSS')
                                myBool = True
                                checkBool = True
                                vLoss = vLoss + 1
                                vTotal = vTotal + 1
                                print('SPECIAL Loss voley on ' + str(
                                    dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                                    GapClosedNum[
                                        count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                                    voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                                    voleyTakeProfit[
                                        count]) + '\nStop loss was reached at the following position ' + str(
                                    forCloseLoop[0]) + '\nStopLoss for this trade was set at ' + str(stopLossValues[count]) + '\n----------------------------------------------------------------------------\n')
                                print('-------------')
                                # writeStr2 = writeStr2 + 'Loss voley on ' + str(
                                #     dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                                #     GapClosedNum[
                                #         count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                                #     voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                                #     voleyTakeProfit[
                                #         count]) + '\nStop loss was reached at the following position ' + str(
                                #     forCloseLoop[
                                #         0]) + '\nStopLoss for this trade was set at ' + str(stopLossValues[count]) + '\n----------------------------------------------------------------------------\n'
                            if forCloseLoop[0] == forCheckTP2[0]:
                                voleyDropPL.append('SIM')
                                myBool = True
                                checkBool = True
                                vSim = vSim + 1
                                vTotal = vTotal + 1
                                print('SPECIAL VOLLEY SIM on ' + str(
                                    dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                                    GapClosedNum[
                                        count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                                    voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                                    voleyTakeProfit[
                                        count]) + '\nStop loss was reached at the following position ' + str(
                                    forCloseLoop[
                                        0]) + ' and take profit was reached on ' + str(forCheckTP2[0]) + '\nStopLoss for this trade was set at ' + str(stopLossValues[count]) + '\n----------------------------------------------------------------------------\n')
                                # writeStr2 = writeStr2 + 'SIM on ' + str(
                                #     dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                                #     GapClosedNum[
                                #         count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                                #     voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                                #     voleyTakeProfit[
                                #         count]) + '\nStop loss was reached at the following position ' + str(
                                #     forCloseLoop[
                                #         0]) + ' and take profit was reached on ' + str(forCheckTP2[
                                #                                                            0]) + '\n----------------------------------------------------------------------------\n'
                        else:
                            #
                            # Here there are values for TP and SL but no values for TP AFTER trade open
                            #
                            vLoss = vLoss + 1
                            vTotal = vTotal + 1
                            voleyDropPL.append('LOSS')
                            print('SPECIAL Loss voley with price going to volley take profit before opening the trade on ' + str(
                                dateListdf2[count]) + ' \nThe trade closed the gap at position ' + str(
                                GapClosedNum[
                                    count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                                voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                                voleyTakeProfit[
                                    count]) + '\nStop loss was reached at the following position ' + str(
                                gapClosedNumStr[
                                    count]) + '\nStopLoss for this trade was set at ' + str(stopLossValues[count]) + '\n----------------------------------------------------------------------------\n')
                    else:
                        #
                        #  We have no value for take profit but plenty values for sl. closeBoon is true
                        #
                        # print('-------------')
                        vLoss = vLoss + 1
                        vTotal = vTotal + 1
                        voleyDropPL.append('LOSS')
                        myBool = True
                        checkBool = True
                        print('SPECIAL Loss voley on ' + str(
                            dateListdf2[count]) + ' \nThe trade closed the gap at position ' + str(
                            GapClosedNum[
                                count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                            voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                            voleyTakeProfit[
                                count]) + '\nStop loss was reached at the following position ' + str(
                            gapClosedNumStr[count]) + '\nStopLoss for this trade was set at ' + str(stopLossValues[count]) + '\n----------------------------------------------------------------------------\n')
                        print('-------------')
                else:
                    #
                    # No value for SL. CHECK fo TP
                    # if there is any value for take profit after trade open we are good
                    if voleyTakeProfitPosStr[count] != 'NONE':
                        AP = ('profit', Rvalue)
                        voleyDropPL.append(AP)
                        vR = vR + Rvalue
                        myBool = True
                        checkBool = True
                        vTotal = vTotal + 1
                        vProfit = vProfit + 1
                        # print('-------------')
                        # writeStr2 = writeStr2 + 'Profit voley on ' + str(
                        #     dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                        #     GapClosedNum[
                        #         count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                        #     voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                        #     voleyTakeProfit[
                        #         count]) + '\nTake profit was reached at the following positionS ' + str(
                        #     voleyTakeProfitPosStr[
                        #         count]) + '\n stop loss was never reached' + '\n' + '\n----------------------------------------------------------------------------\n'
                        print('Profit voley with RVALUE ' + str(Rvalue) + 'on ' +  str(
                            dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                            GapClosedNum[count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                            voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                            voleyTakeProfit[
                                count]) + '\nTake profit was reached at the following positionS ' + str(
                            voleyTakeProfitPosStr[count]) + '\n stop loss was never reached'+ '\nStopLoss for this trade was set at ' + str(stopLossValues[count])  + '\n' + '\n----------------------------------------------------------------------------\n')
                    else:
                        #
                        # No value for SL or TP
                        #
                        voleyDropPL.append('UNDETERMINED')
                        myBool = True
                        checkBool = True
                        vUn = vUn + 1
                        vTotal = vTotal + 1
                        # writeStr2 = writeStr2 + 'Undetermined voley trade on ' + str(
                        #     dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                        #     GapClosedNum[
                        #         count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                        #     voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                        #     voleyTakeProfit[
                        #         count]) + '\nTake profit nor Stop Loss was never reached' + '\n----------------------------------------------------------------------------\n'
                        print('SPECIAL Undetermined voley trade on ' + str(
                            dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                            GapClosedNum[
                                count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                            voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                            voleyTakeProfit[
                                count]) + '\nTake profit nor Stop Loss was never reached' + '\nStopLoss for this trade was set at ' + str(stopLossValues[count]) + '\n----------------------------------------------------------------------------\n')
            else:
                voleyDropPL.append('NONE')
            #     myBool = True
            #     checkBool = True
            # if not myBool:
            #     print('SPECIAL voley trade on ' + str(
            #         dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
            #         GapClosedNum[
            #             count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
            #         voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
            #         voleyTakeProfit[
            #             count]) + '\nStopLoss for this trade was set at ' + str(stopLossValues[count]) + '\n----------------------------------------------------------------------------\n')
            count = count + 1
            forCheckTP2.clear()
            forCheckTP.clear()
            forCloseLoop.clear()
            closeBoon = False
            posTP = False
        print('<><><><><><><><><><><><><><><><><><><><><><><><><<><><><><><><><><><><><><')
        print('TOTAL SPECIAL VOLLEY DRIVE ' + str(vTotal))
        print('PROFIT SPECIAL VOLLEY DRIVE ' + str(vProfit))
        print('LOSS SPECIAL VOLLEY DRIVE ' + str(vLoss))
        print('UNDETERMINED VOLLEY STRAIGHT DRIVE ' + str(vUn))
        print('SIM SPECIAL VOLLEY DRIVE ' + str(vSim))
        print('TOTAL R ' + str(vR))
        netVR = vR - vLoss
        print('NET R VALUE' + str(netVR))
        print('<><><><><><><><><><><><><><><><><><><><><><><><><<><><><><><><><><><><><><')
        volleyTup = (str(slPip), str(pair), 'Volley', vTotal, vProfit, vLoss, '', vSim, vUn, vR, netVR)
        print(volleyTup)
        specialVolleyDrop = '\n<><><><><><><><><><><><><><><><><><><><><><><><><<><><><><><><><><><><><><' + '\nTOTAL SPECIAL VOLLEY DRIVE ' + str(vTotal) + '\nPROFIT SPECIAL VOLLEY DRIVE ' + str(vProfit) + '\nLOSS SPECIAL VOLLEY DRIVE ' + str(vLoss) + '\nUNDETERMINED VOLLEY STRAIGHT DRIVE ' + str(vUn) + '\nSIM SPECIAL VOLLEY DRIVE ' + str(vSim) + '\nTOTAL R ' + str(vR) + '\nTOTAL NET ' + str(netVR) + '\n<><><><><><><><><><><><><><><><><><><><><><><><><<><><><><><><><><><><><><'
        return voleyDropPL, specialVolleyDrop, volleyTup

    def extractor(valueList):
        # Recieves string like 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,
        # Converts to list containing numbers
        # len function starts counting from 1
        # I refer to a char in a list starting counting from 0 eg. valueList[0] is item 1 in list
        checkList = []
        if valueList != '':
            commaPositions = []
            valueList = valueList[:-1]
            count = 1
            for chars in valueList:
                if chars == ',':
                    commaPositions.append(count)
                count = count + 1
            # first
            if len(commaPositions) != 0:
                firstEntry = valueList[0:commaPositions[0] - 1]
                checkList.append(int(firstEntry))
            else:
                firstEntry = int(valueList)
                checkList.append(int(firstEntry))
            count = 0
            # I extract the first entry before i start looping
            for positions in commaPositions:
                if len(commaPositions) > count + 1:
                    stopNum = commaPositions[count + 1] - positions
                    stopNum = stopNum - 1
                    stopNum = positions + stopNum
                    if count < len(commaPositions) - 2:
                        addNum = valueList[positions:stopNum]
                        checkList.append(int(addNum))
                if count == len(commaPositions) - 1:
                    addNum = valueList[positions:len(valueList)]
                    checkList.append(int(addNum))
                count = count + 1
        else:
            checkList.append('')
        return checkList


    # reset all values to check for stopouts for gap trade
    stopOutList = []
    openListDF2 = list(df2.loc[:, 'Opening Value'])
    # openListDF2 = floatConverter(openListDF2)

    count = 0
    counter = 0
    gapS = 0
    reverseTakeProfit =[]
    reverseTakeProfitValue = []
    reverseSting = ''
    reverseTakeProfitStr = []
    stopNumber = len(Low)
    stopHighNumber = len(High)
    gapB = False
    forgaplist = []
    reverseTP = 0
    # calculate straight drive take profit positions
    # price goes to 50% then return to TP
    for gaps in gapClassList:
        gapsizeCheck = gapsizelist[counter]
        if gaps == 'GAP':
            if gapsizeCheck > 0:
                reverseTP = openListDF2[counter] + gapsizeCheck
                for i in range(0, rangeHigh):
                    if counter + i < stopList:
                        if High[counter + i] >= reverseTP:
                            forgaplist.append(i)
                            gapB = True
                if not gapB:
                    reverseTakeProfit.append('NONE')
                    reverseTakeProfitStr.append('NONE')
                    reverseTakeProfitValue.append('NONE')
                else:
                    mynum = forgaplist[0]
                    reverseSting = ''
                    for numbers in forgaplist:
                        reverseSting = reverseSting + str(numbers) + ','
                    reverseTakeProfitStr.append(reverseSting)
                    reverseTakeProfit.append(mynum)
                    reverseTakeProfitValue.append(reverseTP)
            if gapsizeCheck < 0:
                reverseTP = float(openListDF2[counter]) + gapsizeCheck
                for i in range(0, rangeHigh):
                    if counter + i < stopList:
                        if Low[counter + i] <= reverseTP:
                            forgaplist.append(i)
                            gapB = True
                if not gapB:
                    reverseTakeProfit.append('NONE')
                    reverseTakeProfitStr.append('NONE')
                    reverseTakeProfitValue.append('NONE')
                else:
                    mynum = forgaplist[0]
                    reverseSting = ''
                    for numbers in forgaplist:
                        reverseSting = reverseSting + str(numbers) + ','
                    reverseTakeProfitStr.append(reverseSting)
                    reverseTakeProfit.append(mynum)
                    reverseTakeProfitValue.append(reverseTP)
        else:
            reverseTakeProfit.append('NONE')
            reverseTakeProfitStr.append('NONE')
            reverseTakeProfitValue.append('NONE')
        gapB = False
        counter = counter + 1
        forgaplist.clear()
        mynum = 0


    counter = 0

    stopLossCount = []
    stopLossValue = []
    counter=0
    forlist2 = []
    priceMoveOpenCount = []
    priceItem = ()
    gapC = False
    gapB = False
    forgaplist = []
    # I have added the list of values thqat we go through open here
    for gaps in gapClassList:
        gapsizeCheck = gapsizelist[counter]
        # for positive gap
        # stoploss is set below
        # So we check min
        # myOpenNumber = (float(openListDF2[counter]) + stoploss)
        # myOpenNumberNegative = (float(openListDF2[counter]) - stoploss)
        myOpenNumber = (float(openListDF2[counter]))
        myOpenNumberNegative = (float(openListDF2[counter]))
        if gaps == 'GAP':
            if gapsizeCheck > 0:
                for i in range(0, rangeHigh):
                    if counter + i < stopList:
                        if High[counter + i] >= myOpenNumber:
                            forgaplist.append(i)
                            gapB = True
                if not gapB:
                    stopOutList.append('NONE')
                    stopLossCount.append('NONE')
                    stopLossValue.append('NONE')
                    priceMoveOpenCount.append('NONE')
                else:
                    mynum = forgaplist[0]
                    runStr = ''
                    for items in forgaplist:
                        runStr = runStr + str(items) + ','
                    priceMoveOpenCount.append(runStr)
                    stopOutList.append('StopLoss')
                    stopLossCount.append(mynum)
                    stopLossValue.append(myOpenNumber)
            if gapsizeCheck < 0:
                for i in range(0, rangeHigh):
                    if counter + i < stopList:
                        if Low[counter + i] <= myOpenNumberNegative:
                            forgaplist.append(i)
                            gapB = True
                if not gapB:
                    stopOutList.append('NONE')
                    stopLossCount.append('NONE')
                    stopLossValue.append('NONE')
                    priceMoveOpenCount.append('NONE')
                else:
                    mynum = forgaplist[0]
                    runStr = ''
                    for items in forgaplist:
                        runStr = runStr + str(items) + ','
                    priceMoveOpenCount.append(runStr)
                    stopOutList.append('StopLoss')
                    stopLossCount.append(mynum)
                    stopLossValue.append(myOpenNumber)
        else:
            stopOutList.append('NONE')
            priceMoveOpenCount.append('NONE')
            stopLossCount.append('NONE')
            stopLossValue.append('NONE')
        gapB = False
        counter = counter + 1
        forgaplist.clear()
        mynum = 0


    df2['GAP_CLOSED'] = tradeList
    df2['GAP_CLOSED_AT'] = GapClosedNum
    df2['STOPLOSS_VAL'] = stopLossValue
    df2['STOP_LOSS'] = stopOutList
    df2['STOP_COUNT'] = stopLossCount
    df2['POSITIONS_PRICE_MOVE_THROUGH_OPEN'] = priceMoveOpenCount



    # Whats happening here
    # i found a wa to effectively determine 50% value of gap
    # halveGapValue is gold standard list for halvegapvalues

    # STOPLOSS MOVE STRAT


    counter = 0
    halveGapSize = 0
    halveGapValue = []
    secondSLnum = 0
    secondSLnumNeg = 0
    secondSL = []
    pip = 0
    halvepip = 0
    openPip = 0
    prevClosePip = 0
    halveValuePip = 0
    negHalveValuePip = 0
    addNum = 0
    # prevClosingValueC
    # I determine the value of 50% gap here
    # prevClosingValueC = floatConverter(prevClosingValueC)
    for gaps in gapClassList:
        infoString = ''
        gapsizeCheck = gapsizelist[counter]
        addNum = (float(openListDF2[counter]) + float(prevClosingValueC[counter])) / 2
        # movementNumber2 = (openListDF2[counter] - halveGapSize)
        # secondSLnum = (movementNumber2 + stoploss)
        # movementNumberNegative2 = (openListDF2[counter] + halveGapSize)
        # secondSLnumNeg = (movementNumberNegative2 + stoploss)
        if gaps == 'GAP':
            halveGapValue.append(addNum)
        else:
            halveGapValue.append('NONE')
        counter = counter + 1


    df2['50%_GAP_VALUE'] = halveGapValue

    # lets set stoploss at 6 pips for voley
    counter = 0
    gapSizeCheck = 0
    voleySixPipSL = []
    stopLossValue = 0
    for items in halveGapValue:
        gapsizeCheck = gapsizelist[counter]
        if items != 'NONE':
            if gapsizeCheck > 0:
                stopLossValue = halveGapValue[counter] + stoploss
                voleySixPipSL.append(stopLossValue)
            if gapsizeCheck < 0:
                stopLossValue = halveGapValue[counter] - stoploss
                voleySixPipSL.append(stopLossValue)
        else:
            voleySixPipSL.append('NONE')
        counter = counter + 1

    forgaplist = []
    sixPipLossStr = []
    size = 0
    counter = 0
    for gaps in gapClassList:
        if gaps == 'GAP':
            size = gapsizelist[counter]
        counter = counter + 1


    counter = 0
    # here i check price moving through sixPip sl
    for gaps in gapClassList:
        if gaps == 'GAP':
            if voleySixPipSL[counter] != 'NONE':
                gapsizeCheck = gapsizelist[counter]
                checkValue = voleySixPipSL[counter]
                if gapsizeCheck > 0:
                    for i in range(0, rangeHigh):
                        if counter + i < stopList:
                            if Low[counter + i] <= checkValue:
                                forgaplist.append(i)
                                gapB = True
                    if not gapB:
                        sixPipLossStr.append('NONE')
                    else:
                        mynum = forgaplist[0]
                        halveStr = ''
                        for numbers in forgaplist:
                            halveStr = halveStr + str(numbers) + ','
                        sixPipLossStr.append(halveStr)
                if gapsizeCheck < 0:
                    for i in range(0, rangeHigh):
                        if counter + i < stopList:
                            if High[counter+i] >= checkValue:
                                forgaplist.append(i)
                                gapB = True
                    if not gapB:
                        sixPipLossStr.append('NONE')
                    else:
                        mynum = forgaplist[0]
                        halveStr = ''
                        for numbers in forgaplist:
                            halveStr = halveStr + str(numbers) + ','
                        sixPipLossStr.append(halveStr)
            else:
                sixPipLossStr.append('NONE')
        else:
            sixPipLossStr.append('NONE')
        gapB = False
        counter = counter + 1
        forgaplist.clear()
        mynum = 0






    #checking how many gaps closed
    myClosedList = list(df2.loc[:, 'GAP_CLOSED'])
    # gapNUM = 0
    # for closes in myClosedList:
    #     if closes != 'NONE':
    #         gapNUM = gapNUM+1

    # counting lost trades
    stopOUT = 0
    myStopsList = list(df2.loc[:, 'STOP_LOSS'])
    # for stops in myStopsList:
    #     if stops != 'NONE':
    #         stopOUT = stopOUT+1


    myStopsNumberListCheck = list(df2.loc[:, 'STOP_COUNT'])
    myGapsNumberListCheck = list(df2.loc[:, 'GAP_CLOSED_AT'])

    dateListdf2 = list(df2.loc[:, 'DATE_OBJECT'])


    fridayCount = 0
    for days in weekdayList:
        if days == 4:
            fridayCount = fridayCount + 1


    fridayCount = round(fridayCount/48)
    # HERE I CALCULATE THE AMOUNT OF WEEKENDS IN MY DATASET
    date1 = actualDateList[0]
    date2 = actualDateList[(len(actualDateList)-1)]
    # getting the result, abs = absolute value
    # (date1-date2).days gives an integer number of dates
    days = abs(date1 - date2).days
    # caculating and printing the weeks, // = floor division operator
    weekCounter = (days // 7)
    forgaplist = []
    halveHit = []
    halveHitPos = []
    halvehitValue = []
    counter = 0
    #Here I check if 50% was hit
    halveGapSizeList = []
    positiveGap = 0
    negativeGap = 0
    # Here i want to check if price went through 50% gap value
    # halveGapValue
    # This is quality checked
    halveHitPosStr = []
    for gaps in gapClassList:
        if gaps == 'GAP':
            gapsizeCheck = gapsizelist[counter]
            halveValue = halveGapValue[counter]
            if gapsizeCheck > 0:
                positiveGap = positiveGap + 1
                for i in range(0, rangeHigh):
                    if counter + i < stopList:
                        if Low[counter + i] <= halveValue:
                            forgaplist.append(i)
                            gapB = True
                if not gapB:
                    halveHit.append('NONE')
                    halveHitPos.append('NONE')
                    halvehitValue.append('NONE')
                    halveHitPosStr.append('NONE')
                else:
                    mynum = forgaplist[0]
                    halveStr = ''
                    for numbers in forgaplist:
                        halveStr = halveStr + str(numbers) + ','
                    halveHitPosStr.append(halveStr)
                    halveHit.append('HIT')
                    halveHitPos.append(mynum)
            if gapsizeCheck < 0:
                negativeGap = negativeGap + 1
                for i in range(0, rangeHigh):
                    if counter + i < stopList:
                        if High[counter+i] >= halveValue:
                            forgaplist.append(i)
                            gapB = True
                if not gapB:
                    halveHit.append('NONE')
                    halveHitPos.append('NONE')
                    halvehitValue.append('NONE')
                    halveHitPosStr.append('NONE')
                else:
                    mynum = forgaplist[0]
                    halveStr = ''
                    for numbers in forgaplist:
                        halveStr = halveStr + str(numbers) + ','
                    halveHitPosStr.append(halveStr)
                    halveHit.append('HIT')
                    halveHitPos.append(mynum)
        else:
            halveHit.append('NONE')
            halveHitPosStr.append('NONE')
            halveHitPos.append('NONE')
        gapB = False
        counter = counter + 1
        forgaplist.clear()
        mynum = 0

    df2['50% POSITIONS'] = halveHitPosStr
    df2['50% EFFORT'] = halveHit
    df2['HIT POSITION'] = halveHitPos
    #
    # I now check reverse 50% value hit to determine if price go back through it after closing the gap
    #
    reverseHalveHitPosStr = []
    voleyOpenPos = []
    reverseHalveHit = []
    lastPos = 0
    firstPos = []
    gapC = False
    counter = 0
    for gaps in gapClassList:
        if gaps == 'GAP':
            # I actually need to check those instance that close the gap
            if GapClosedNum[counter] != 'NONE':
                # if it hits i check the opposite end to see if it goes back through
                gapsizeCheck = gapsizelist[counter]
                halveValue = halveGapValue[counter]
                if gapsizeCheck > 0:
                    for i in range(0, rangeHigh):
                        # I check High instead of low
                        if counter + i < stopList:
                            if High[counter + i] >= halveValue:
                                forgaplist.append(i)
                                gapB = True
                    if not gapB:
                        reverseHalveHit.append('NONE')
                        reverseHalveHitPosStr.append('NONE')
                        voleyOpenPos.append('NONE')
                    else:
                        #
                        # I only want to add the position after the original position crossing 50%
                        #
                        lastPos = GapClosedNum[counter]
                        halveStr = ''
                        for numbers in forgaplist:
                            if numbers > lastPos:
                                halveStr = halveStr + str(numbers) + ','
                                gapC = True
                                firstPos.append(numbers)
                        if halveStr == '':
                            reverseHalveHitPosStr.append('NONE')
                        else:
                            reverseHalveHitPosStr.append(halveStr)
                        if gapC:
                            voleyOpenPos.append(firstPos[0])
                        else:
                            voleyOpenPos.append('NONE')
                        reverseHalveHit.append('HIT')
                if gapsizeCheck < 0:
                    negativeGap = negativeGap + 1
                    for i in range(0, rangeHigh):
                        # I check Low instead of High
                        if counter + i < stopList:
                            if Low[counter+i] <= halveValue:
                                forgaplist.append(i)
                                gapB = True
                    if not gapB:
                        reverseHalveHit.append('NONE')
                        reverseHalveHitPosStr.append('NONE')
                        voleyOpenPos.append('NONE')
                    else:
                        #
                        # I only want to add the position after the original position crossing 50%
                        #
                        lastPos = GapClosedNum[counter]
                        halveStr = ''
                        for numbers in forgaplist:
                            if numbers > lastPos:
                                halveStr = halveStr + str(numbers) + ','
                                gapC = True
                                firstPos.append(numbers)
                        if halveStr == '':
                            reverseHalveHitPosStr.append('NONE')
                        else:
                            reverseHalveHitPosStr.append(halveStr)
                        if gapC:
                            voleyOpenPos.append(firstPos[0])
                        else:
                            voleyOpenPos.append('NONE')
                        reverseHalveHit.append('HIT')
            else:
                reverseHalveHit.append('NONE')
                reverseHalveHitPosStr.append('NONE')
                voleyOpenPos.append('NONE')
        else:
            reverseHalveHit.append('NONE')
            reverseHalveHitPosStr.append('NONE')
            voleyOpenPos.append('NONE')
        gapB = False
        gapC = False
        counter = counter + 1
        forgaplist.clear()
        firstPos.clear()
    # i want to check all the positions that wick go through the open value
    momentumOpenHitPos = []
    hitcount = 0
    # checking if it went back through openvalue for reverse trade
    # This checks after it went through halve gap
    # position is appended into momentumOpenHitPos
    # position is determined as how many itterations from gap opening it goes through the open value again with parameter that it must first have reached 50
    forOpenList = []
    momentumO = []
    counter = 0
    for hits in halveHit:
        if hits == 'HIT':
            hitcount = hitcount + 1
            hhPosition = halveHitPos[counter]
            priceMovestr = priceMoveOpenCount[counter]
            # use extractor to extract values
            forOpenList = extractor(priceMovestr)
            for positions in forOpenList:
                # Important: we only check to open the reverse trade 4 itterations from when the gap opened for market reasons
                # I removed the 4 itteration rule
                if positions > hhPosition:
                    momentumO.append(positions)
            # now i have all the positions where price went back through oppen value after the 50% value was reached
            if len(momentumO) != 0:
                momentumOpenHitPos.append(momentumO[0])
            else:
                momentumOpenHitPos.append('NONE')
        else:
            momentumOpenHitPos.append('NONE')
        forOpenList.clear()
        momentumO.clear()
        counter = counter + 1

    df2['Straight Drive Open Position'] = momentumOpenHitPos

    count = 0

    # Here i check for the straight drive

    count = 0
    mcount = 0
    reverseOption = []

    for items in momentumOpenHitPos:
        if items != 'NONE':
            # if there is a value for momentum open we need to check gap close
            # if gap wasclosed after it is ok to open trade
            # if not then no trade
            # and GapClosedNum[count] == 'NONE':
            if GapClosedNum[count] == 'NONE':
                reverseOption.append('REVERSE TRADE HERE')
                # here i am happy to open the trade
            else:
                if GapClosedNum[count] > items:
                    reverseOption.append('REVERSE TRADE HERE')
                else:
                    reverseOption.append('NONE')
            mcount = mcount + 1
        else:
            reverseOption.append('NONE')
        count = count + 1

    df2['REVERSE TRADE YN'] = reverseOption
    reverseProfitLoss = []

    def stringConstructor(inputString):
        goto = 50
        outPutString = ' |           '
        stringLen = len(inputString)
        for chars in inputString:
            outPutString = outPutString + chars
        net = 0
        net = goto - stringLen
        for i in range(0, net):
            outPutString = outPutString + ' '
        outPutString = outPutString + '|'
        return outPutString

    forCheckMom = []
    addNum = 0
    # reverse take profit calculations
    # lets check the take profit values and levels
    # lets take a step back and find only stoploss positions for reverse trades
    # i must now solve the single digit problem with all my string converters
    # ReturnTPlistPos holds the position where price went through tp
    # so now its simple. if price goes through take profit firs its a winner
    # reverseTakeProfitStr.append(reverseSting)
    #                 reverseTakeProfit.append(mynum)
    #                 reverseTakeProfitValue.append(reverseTP)

    reverseP = 0
    reverseLoss = 0
    reverseSIM = 0
    reverseU = 0
    posL = False
    stopLossPosList = []
    forCheckTP = []
    forCheckTP2 = []
    posTP = False
    tots = 0
    mistake = 0
    mistakestr = ''
    finPrintMis = ''
    count = 0
    totalR = 0
    writeStr = ''
    # at this point i feel i know when straight drivwe options open
    # I see where there was chances for stop loss in this block
    # if items != 'NONE' and GapClosedNum[count] == 'NONE':
    myBool = False
    for items in momentumOpenHitPos:
        if reverseOption[count] == 'REVERSE TRADE HERE':
            #
            # R-value
            #
            openV = openListDF2[count]
            halvegap = halveGapValue[count]
            stoplossSize = openV - halvegap
            if stoplossSize < 0:
                stoplossSize = stoplossSize * -1
            if reverseTakeProfitValue[count] == 'NONE':
                takeProfitSize = stoplossSize + stoplossSize
            else:
                takeProfitSize = openV - reverseTakeProfitValue[count]
            if takeProfitSize < 0:
                takeProfitSize = takeProfitSize * -1
            Rvalue = (takeProfitSize / stoplossSize)
            #
            # Algo
            #
            tots = tots + 1
            halveString = halveHitPosStr[count]
            forCheckMom = extractor(halveString)
            for positions in forCheckMom:
                # So i check if there is cases where price goes through 50% value after trade is opened
                # this means there is a chance for stop loss
                if positions > items:
                    posL = True
                    stopLossPosList.append(positions)
                    # now i have a list that either contains the positions of going through stop loss or NONE if price
                    # did not go through stop loss
            #         so if there is a position where price went through sl then we can say there is a chance for SL
            if posL:
                # here we now know that there is in fact a value for SL
                # we now check if there is a value for TP
                if reverseTakeProfitStr[count] != 'NONE':
                    forCheckTP = extractor(reverseTakeProfitStr[count])
                    # first i check if there are values for take profit after trade open position
                    for positions in forCheckTP:
                        if positions > items:
                            posTP = True
                            forCheckTP2.append(positions)
                else:
                    #
                    #  BLOK1
                    #
                    # We have no value for take profit but plenty values for sl
                    reverseLoss = reverseLoss + 1
                    reverseProfitLoss.append('LOSS')
                    myBool = True
                    mistakestr = mistakestr + '_BLOK1_'
                    mistake = mistake + 1
                    writeStr = writeStr + 'Loss Reverse Trade KKK On ' + str(
                        dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                        halveGapValue[count]) + ' at the position ' + str(
                        halveHitPos[
                            count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                        momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                        reverseTakeProfitValue[
                            count]) + '\nTake profit was never reached ' + '\n stop loss was reached at the following position ' + str(
                        stopLossPosList[0]) + '\n----------------------------------------------------------------------------\n'

                    print('Loss Reverse Trade KKK On ' + str(
                        dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                        halveGapValue[count]) + ' at the position ' + str(
                        halveHitPos[
                            count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                        momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                        reverseTakeProfitValue[
                            count]) + '\nTake profit was never reached ' + '\n stop loss was reached at the following position ' + str(
                        stopLossPosList[0]) +'\nThe gap closed at the following positions ' + str(gapClosedNumStr[count]) + '\nGap open value ' + str(openListDF2[count]) + '\nPrice went through the open value at the following positions ' + priceMoveOpenCount[count])
                    # here i kno that there no value for TP but there is for SL
                if posTP:
                    # this can only be true if there was a value for str
                    if stopLossPosList[0] < forCheckTP2[0]:
                        #
                        #  BLOK 2
                        #
                        reverseProfitLoss.append('LOSS')
                        mistake = mistake + 1
                        mistakestr = mistakestr + "_BLOK2_"
                        reverseLoss = reverseLoss + 1
                        #
                        # writing text file lines
                        #
                        # writeStr = writeStr + stringConstructor('Loss Reverse Trade On ' + str(
                        #     dateListdf2[count])) + '\n'
                        # writeStr = writeStr + stringConstructor('The trade reached 50% gap value off ' + str(
                        #     halveGapValue[count])) + '\n'
                        # writeStr = writeStr + stringConstructor(' at the position ' + str(
                        #     halveHitPos[
                        #         count])) + '\n'
                        # writeStr = writeStr + stringConstructor('Price went back through open value opening the momentum trade at ' + str(
                        #     momentumOpenHitPos[count])) + '\n'
                        # writeStr = writeStr + stringConstructor('Take profit value for this trade is set at: ' + str(
                        #     reverseTakeProfitValue[count])) + '\n'
                        # writeStr = writeStr + stringConstructor('Take profit was reached at the following position ' + str(
                        #     forCheckTP2[0])) + '\n'
                        # writeStr = writeStr + stringConstructor('stop loss was reached at the following position ' + str(
                        #     stopLossPosList[0])) + '\n'
                        # writeStr = writeStr + stringConstructor('\n----------------------------------------------------------------------------\n')
                        #
                        #
                        #
                        writeStr = writeStr + 'Loss Reverse Trade On ' + str(
                            dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                            halveGapValue[count]) + ' at the position ' + str(
                            halveHitPos[
                                count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                            momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                            reverseTakeProfitValue[count]) + '\nTake profit was reached at the following position ' + str(
                            forCheckTP2[0]) + '\n stop loss was reached at the following position ' + str(
                            stopLossPosList[0]) + '\n----------------------------------------------------------------------------\n'

                        # print('Loss Reverse Trade On ' + str(
                        #     dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                        #     halveGapValue[count]) + ' at the position ' + str(
                        #     halveHitPos[
                        #         count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                        #     momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                        #     reverseTakeProfitValue[count]) + '\nTake profit was reached at the following position ' + str(
                        #     forCheckTP2[0]) + '\n stop loss was reached at the following position ' + str(
                        #     stopLossPosList[0]))
                    if stopLossPosList[0] > forCheckTP2[0]:
                        #
                        # BLOK 3
                        #
                        # print('-------------')
                        reverseP = reverseP + 1
                        reverseProfitLoss.append('PROFIT')
                        myBool = True
                        totalR = totalR + Rvalue
                        mistake = mistake + 1
                        mistakestr = mistakestr + "_BLOK3_"
                        #
                        # wrting text lines
                        #
                        # writeStr = writeStr + stringConstructor('Profit Reverse with Rvalue ' + (str(Rvalue)) + ' Trade On ' + str(
                        #     dateListdf2[count])) + '\n'
                        # writeStr = writeStr + stringConstructor('The trade reached 50% gap value off ' + str(
                        #     halveGapValue[count]) + ' at the position ' + str(
                        #     halveHitPos[
                        #         count])) + '\n'
                        # writeStr = writeStr + stringConstructor('Price went back through open value opening the momentum trade at ' + str(
                        #     momentumOpenHitPos[count])) + '\n'
                        # writeStr = writeStr + stringConstructor('Take profit value for this trade is set at: ' + str(
                        #     reverseTakeProfitValue[count])) + '\n'
                        # writeStr = writeStr + stringConstructor('Take profit was reached at the following position ' + str(
                        #     forCheckTP2[0])) + '\n'
                        # writeStr = writeStr + stringConstructor('Stop loss was reached at the following position ' + str(
                        #     stopLossPosList[0])) + '\n'
                        # writeStr = writeStr + stringConstructor('\n----------------------------------------------------------------------------\n')
                        #
                        #
                        #
                        writeStr = writeStr + 'Profit Reverse with Rvalue ' + (str(Rvalue)) + ' Trade On ' + str(
                            dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                            halveGapValue[count]) + ' at the position ' + str(
                            halveHitPos[
                                count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                            momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                            reverseTakeProfitValue[count]) + '\nTake profit was reached at the following position ' + str(
                            forCheckTP2[0]) + '\n stop loss was reached at the following position ' + str(
                            stopLossPosList[0]) + '\n----------------------------------------------------------------------------\n'
                        # print('Profit Reverse with Rvalue ' + (str(Rvalue)) + ' Trade On ' + str(
                        #     dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                        #     halveGapValue[count]) + ' at the position ' + str(
                        #     halveHitPos[
                        #         count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                        #     momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                        #     reverseTakeProfitValue[count]) + '\nTake profit was reached at the following position ' + str(
                        #     forCheckTP2[0]) + '\n stop loss was reached at the following position ' + str(
                        #     stopLossPosList[0]))
                    if stopLossPosList[0] == forCheckTP2[0]:
                        #
                        # BLOK 4
                        #
                        # print('-------------')
                        writeStr = writeStr + 'SIM Reverse Trade On ' + str(
                            dateListdf2[count]) + 'The trade reached 50% gap value off ' + str(
                            halveGapValue[count]) + ' at the position ' + str(
                            halveHitPos[
                                count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                            momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                            reverseTakeProfitValue[count]) + '\nTake profit was reached at the following position ' + str(
                            forCheckTP2[0]) + '\n stop loss was reached at the following position ' + str(
                            stopLossPosList[0]) + '\n' + '\n----------------------------------------------------------------------------\n'
                        reverseSIM = reverseSIM + 1
                        reverseProfitLoss.append('SIM')
                        myBool = True
                        mistake = mistake + 1
                        mistakestr = mistakestr + "_BLOK4_"
                        # print('SIM Reverse Trade On ' + str(
                        #     dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                        #     halveGapValue[count]) + ' at the position ' + str(
                        #     halveHitPos[
                        #         count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                        #     momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                        #     reverseTakeProfitValue[count]) + '\nTake profit was reached at the following position ' + str(
                else:
                    # if reverseTakeProfitstr was NONE
                    # here we had two ittereations of what could have happened:
                    # 1) there was a NONE value for reverseTakeProfitStr so our check bolean could not go to true
                    # 2) or there was a value for above but no TP values for before trade opened.
                    # Both of these results in this section being activated
                    if reverseTakeProfitStr[count] != 'NONE':
                        reverseProfitLoss.append('LOSS')
                        reverseLoss = reverseLoss + 1
                        myBool = True
                        writeStr = writeStr + 'Crazy Loss Reverse Trade where price reached TP before open and lost after On ' + str(
                            dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                            halveGapValue[count]) + ' at the position ' + str(
                            halveHitPos[
                                count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                            momentumOpenHitPos[count]) + '\n----------------------------------------------------------------------------\n'
                        # if str(dateListdf2[count]) == '2015-06-08':
                        #     print(
                        #         '<><><><><><><><<><><><><><><<><><><><<><><><><><<><><><><><<><><><><><><<><><><><<>><><><><><><><><><><><><><><><><><<><><><><><><<><><><><<><><><><><<><><><><><<><><><><><><<><><><><<>><><><><><><><><><>')
                        # if str(dateListdf2[count]) == '2016-08-22':
                        #     print(
                        #         'HEEEEEEEEEEEEEEEEEEEEEERRRRRRRRRRRRRREEEEEEEEEEEEEEEEEEEIIIIIIIIIIIIIIIAAAAAAAAAAAAAAAAAAMMMMMMMMMMM')

            else:

                # now we kno there no value for SL but there might be a value for TP
                # check if there is a value for reverseTakeProfitstr
                # none value is assigned for instances where price never goes through TP
                if reverseTakeProfitStr[count] != 'NONE':
                    forCheckTP = extractor(reverseTakeProfitStr[count])
                    # first i check if there are values for take profit after trade open position
                    for positions in forCheckTP:
                        if positions > items:
                            posTP = True
                            forCheckTP2.append(positions)
                    if posTP:
                        # now we know there is no value for sl and a value for tp
                        #
                        # BLOK 6
                        #
                        # print('-------------')
                        writeStr = writeStr + 'Profit Reverse with Rvalue ' + (str(Rvalue)) + ' Trade On ' + str(
                            dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                            halveGapValue[count]) + ' at the position ' + str(
                            halveHitPos[
                                count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                            momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                            reverseTakeProfitValue[count]) + '\nTake profit was reached at the following position ' + str(
                            forCheckTP2[0]) + '\n stop loss was never reached' + '\n' + '\n----------------------------------------------------------------------------\n'
                        reverseP = reverseP + 1
                        reverseProfitLoss.append('PROFIT')
                        myBool = True
                        mistake = mistake + 1
                        mistakestr = mistakestr + "_BLOK6_"
                        # print('Profit Reverse with Rvalue ' + (str(Rvalue)) + ' Trade On ' + str(
                        #     dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                        #     halveGapValue[count]) + ' at the position ' + str(
                        #     halveHitPos[
                        #         count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                        #     momentumOpenHitPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                        #     reverseTakeProfitValue[count]) + '\nTake profit was reached at the following position ' + str(
                        #     forCheckTP2[0]) + '\n stop loss was never reached')
                    else:
                        # here we say there is no value for SL
                        # and no value for TP
                        # print('-------------')
                        reverseU = reverseU + 1
                        #
                        # Blok 7
                        #
                        reverseProfitLoss.append('UNDETERMINED')
                        myBool = True
                        writeStr = writeStr + 'UNDETERMINED Reverse Trade On ' + str(
                            dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                            halveGapValue[count]) + ' at the position ' + str(
                            halveHitPos[
                                count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                            momentumOpenHitPos[count]) + '\nThe trade never reached SL or TP after being opened\n' + '\n----------------------------------------------------------------------------\n'
                        mistake = mistake + 1
                        mistakestr = mistakestr + "_BLOK7_"
                        # print('UNDETERMINED Reverse Trade On ' + str(
                        #     dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                        #     halveGapValue[count]) + ' at the position ' + str(
                        #     halveHitPos[
                        #         count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                        #     momentumOpenHitPos[count]) + '\nThe trade never reached SL or TP after being opened')
                else:
                    #
                    # Blok 8
                    #
                    # print('-------------')
                    writeStr = writeStr +'UNDETERMINED KKK Reverse Trade On ' + str(
                        dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                        halveGapValue[count]) + ' at the position ' + str(
                        halveHitPos[
                            count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                        momentumOpenHitPos[count]) + '\nThe trade never reached SL or TP after being opened\n'
                    reverseU = reverseU + 1
                    reverseProfitLoss.append('UNDETERMINED')
                    myBool = True
                    mistake = mistake + 1
                    mistakestr = mistakestr + "_BLOK8_"
                    writeStr = writeStr + 'UNDETERMINED KKK Reverse Trade On ' + str(
                        dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                        halveGapValue[count]) + ' at the position ' + str(
                        halveHitPos[
                            count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                        momentumOpenHitPos[count]) + '\nThe trade never reached SL or TP after being opened' + '\n----------------------------------------------------------------------------\n'
                    # print('UNDETERMINED KKK Reverse Trade On ' + str(
                    #     dateListdf2[count]) + ' \nThe trade reached 50% gap value off ' + str(
                    #     halveGapValue[count]) + ' at the position ' + str(
                    #     halveHitPos[
                    #         count]) + ' \nPrice went back through open value opening the momentum trade at ' + str(
                    #     momentumOpenHitPos[count]) + '\nThe trade never reached SL or TP after being opened')
        else:
            reverseProfitLoss.append('NONE')
            myBool = True
        stopLossPosList.clear()
        forCheckTP.clear()
        forCheckTP2.clear()
        forCheckMom.clear()
        myBool = False
        loss = False
        posL = False
        posTP = False
        count = count + 1
        if mistake > 1:
            finPrintMis = finPrintMis + ' ~~ ' + mistakestr
        mistake = 0
        mistakestr = ''

    # ><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # writing date lists
    # row_list = [['PAIR','STRATEGY','TOTAL TRADES','PROFIT TRADES', 'LOSS TRADES', 'SIM TRADES', 'UNDETERMINED'],
    #             [fileExtractname,'REVERSE TRADE', str(tots),str(reverseP),str(reverseLoss),str(reverseSIM),str(reverseU)],
    #             [fileExtractname,'VOLEY TRADE', str(voleyTotal), str(voleyProfit), str(voleyLoss), str(voleySim), str(voleyUn)]]
    # with open('protagonist.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(row_list)










    # ><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>




    count = 0
    forHalveLoop = []
    openPos = 0
    halveBoon = False
    voleyDrop = []
    voleyDropOpen = []
    forCheckMom.clear()

    # reverseHalveHitPosStr = []
    # voleyOpenPos = []
    # reverseHalveHit= []

    # This loop checks for the voley drop
    # check if there is values for reverse 50 AFTER gapclose
    for items in GapClosedNum:
        if items != 'NONE':
            # Now we know the gap closed. now we need to check if it moved down back to 50%
            # if it went to close it went through 50%
            # Here we know there is 50% value
            # it is not nec the case that price went back to 50% after closing the gap
            if reverseHalveHitPosStr[count] != 'NONE':
                halveString = reverseHalveHitPosStr[count]
                forCheckMom = extractor(halveString)
                for positions in forCheckMom:
                    if positions > items:
                        halveBoon = True
                        forHalveLoop.append(positions)
            if halveBoon:
                # Here we know there is a voley drop oppportunity
                voleyDrop.append('TRUE')
                openPos = forHalveLoop[0]
                voleyDropOpen.append(openPos)
            else:
                voleyDrop.append('NONE')
                voleyDropOpen.append('NONE')
        else:
            voleyDrop.append('NONE')
            voleyDropOpen.append('NONE')
        count = count + 1
        forHalveLoop.clear()
        halveBoon = False

    df2['voley drop'] = voleyDrop


    #
    # Take profit value for the volley
    #
    # for gaps in gapClassList:
    #     infoString = ''
    #     gapsizeCheck = gapsizelist[counter]
    #     addNum = (openListDF2[counter] + prevClosingValueC[counter]) / 2
    #     movementNumber2 = (openListDF2[counter] - halveGapSize)
    #     secondSLnum = (movementNumber2 + stoploss)
    #     movementNumberNegative2 = (openListDF2[counter] + halveGapSize)
    #     secondSLnumNeg = (movementNumberNegative2 + stoploss)
    #     if gaps == 'GAP':
    #         halveGapValue.append(addNum)
    #     else:
    #         halveGapValue.append('NONE')
    #     counter = counter + 1

    # voleyOpenPos.append(firstPos[0])
    # determine actual TP value for volley
    voleyTakeProfit = []
    VTP = 0
    count = 0
    reverseTP = 0
    for gaps in gapClassList:
        # find mid value between open and reverseTP
        # I add the volley tp only for those instances where we open volley trade
        # I need to calculate the reverse take profit first and then determine mid point
        # SPECIAL NOTE: Iam not using the list because it carries NONE values for those instances where price never went through reverseTP
        gapsizeCheck = gapsizelist[count]
        # I want values for voleyTP on ALL gaps not only voley trade
        # This way I can have multiple uses for the list
        if gaps == 'GAP':
            # if gap is negative gapsize is negative
            # so in those instances it is again a plus min thing
            reverseTP = openListDF2[count] + gapsizeCheck
            VTP = (openListDF2[count] + reverseTP) / 2
            voleyTakeProfit.append(VTP)
        else:
            voleyTakeProfit.append('NONE')
        count = count + 1

    count = 0
    counter = 0
    gapS = 0
    voleyTakeProfitPos = []
    voleyTakeProfitPosStr = []
    reverseSting = ''
    stopNumber = len(Low)
    stopHighNumber = len(High)
    gapB = False
    forgaplist = []
    reverseTP = 0
    # calculate voley take profit positions

    for gaps in gapClassList:
        gapsizeCheck = gapsizelist[counter]
        if gaps == 'GAP':
            if gapsizeCheck > 0:
                reverseTP = voleyTakeProfit[counter]
                for i in range(0, rangeHigh):
                    if counter + i < stopList:
                        if High[counter + i] >= reverseTP:
                            forgaplist.append(i)
                            gapB = True
                if not gapB:
                    voleyTakeProfitPos.append('NONE')
                    voleyTakeProfitPosStr.append('NONE')
                else:
                    mynum = forgaplist[0]
                    reverseSting = ''
                    for numbers in forgaplist:
                        reverseSting = reverseSting + str(numbers) + ','
                    voleyTakeProfitPosStr.append(reverseSting)
                    voleyTakeProfitPos.append(mynum)
            if gapsizeCheck < 0:
                reverseTP = voleyTakeProfit[counter]
                for i in range(0, rangeHigh):
                    if counter + i < stopList:
                        if Low[counter + i] <= reverseTP:
                            forgaplist.append(i)
                            gapB = True
                if not gapB:
                    voleyTakeProfitPos.append('NONE')
                    voleyTakeProfitPosStr.append('NONE')
                else:
                    mynum = forgaplist[0]
                    reverseSting = ''
                    for numbers in forgaplist:
                        reverseSting = reverseSting + str(numbers) + ','
                    voleyTakeProfitPosStr.append(reverseSting)
                    voleyTakeProfitPos.append(mynum)
        else:
            voleyTakeProfitPos.append('NONE')
            voleyTakeProfitPosStr.append('NONE')
        gapB = False
        counter = counter + 1
        forgaplist.clear()
        mynum = 0



    # CHECK VOLEY DROP PROFIT
    count = 0
    voleyLoss = 0
    voleyProfit = 0
    voleySim = 0
    voleyUn = 0
    forCheckTP = []
    forCheckTP2 = []
    writeStr2 = ''
    voleyDropPL = []
    posTP = False
    openNum = 0
    closeBoon = False
    forCloseLoop = []
    voleyTotal = 0
    checkBool = False
    checkB = 0
    myBool = False

    for items in voleyOpenPos:
        if items != 'NONE':
            # if there is an open position volley trade is true
            openNum = items
            closeNum = gapClosedNumStr[count]
            forCheckMom = extractor(closeNum)
            for positions in forCheckMom:
                # if there is value for gapclose after trade is opened we have chance for sl
                if positions > openNum:
                    # in this case there is a chance for stoploss
                    closeBoon = True
                    forCloseLoop.append(positions)
            if closeBoon:
                #
                # here we now know that there is in fact a value for SL
                # we now check if there is a value for TP
                #
                if voleyTakeProfitPosStr[count] != 'NONE':
                    #
                    # Value for SL and TP
                    #
                    # No else block cause the undetermined is caught below
                    forCheckTP = extractor(voleyTakeProfitPosStr[count])
                    # first i check if there are values for take profit after trade open position
                    for positions in forCheckTP:
                        # check if there is positions for tp after trade is open
                        if positions > openNum:
                            posTP = True
                            forCheckTP2.append(positions)
                    if posTP:

                        #
                        # Values for tp after trade is opened & values for SL
                        #
                        if forCloseLoop[0] > forCheckTP2[0]:
                            #
                            # Trade went through TP before going through SL
                            #
                            voleyDropPL.append('PROFIT')
                            myBool = True
                            checkBool = True
                            voleyProfit = voleyProfit + 1
                            voleyTotal = voleyTotal + 1
                            # print('Profit voley on ' + str(
                            #     dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                            #     GapClosedNum[
                            #         count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                            #     voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                            #     voleyTakeProfit[
                            #         count]) + '\nTake profit was reached at the following positionS ' + str(
                            #     forCheckTP2[0]) +  '\n----------------------------------------------------------------------------\n')
                            # print('-------------')
                            writeStr2 = writeStr2 + 'Profit voley on ' + str(
                                dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                                GapClosedNum[
                                    count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                                voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                                voleyTakeProfit[
                                    count]) + '\nTake profit was reached at the following positionS ' + str(
                                forCheckTP2[0]) +  '\n----------------------------------------------------------------------------\n'
                        if forCloseLoop[0] < forCheckTP2[0]:
                            #
                            # SL was was hit before the TP
                            #
                            voleyDropPL.append('LOSS')
                            myBool = True
                            checkBool = True
                            voleyLoss = voleyLoss + 1
                            voleyTotal = voleyTotal + 1
                            # print('Loss voley on ' + str(
                            #     dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                            #     GapClosedNum[
                            #         count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                            #     voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                            #     voleyTakeProfit[
                            #         count]) + '\nStop loss was reached at the following position ' + str(
                            #     forCloseLoop[0]) + '\n----------------------------------------------------------------------------\n')
                            # print('-------------')
                            writeStr2 = writeStr2 + 'Loss voley on ' + str(
                                dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                                GapClosedNum[
                                    count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                                voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                                voleyTakeProfit[
                                    count]) + '\nStop loss was reached at the following position ' + str(
                                forCloseLoop[0]) + '\n----------------------------------------------------------------------------\n'
                        if forCloseLoop[0] == forCheckTP2[0]:
                            voleyDropPL.append('SIM')
                            myBool = True
                            checkBool = True
                            voleySim = voleySim + 1
                            voleyTotal = voleyTotal + 1
                            # print('SIM on ' + str(
                            #     dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                            #     GapClosedNum[
                            #         count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                            #     voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                            #     voleyTakeProfit[
                            #         count]) + '\nStop loss was reached at the following position ' + str(
                            #     forCloseLoop[
                            #         0]) + ' and take profit was reached on ' + str(forCheckTP2[0]) + '\n----------------------------------------------------------------------------\n')
                            writeStr2 = writeStr2 +'SIM on ' + str(
                                dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                                GapClosedNum[
                                    count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                                voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                                voleyTakeProfit[
                                    count]) + '\nStop loss was reached at the following position ' + str(
                                forCloseLoop[
                                    0]) + ' and take profit was reached on ' + str(forCheckTP2[0]) + '\n----------------------------------------------------------------------------\n'
                    else:
                        #
                        # Here there are values for TP and SL but no values for TP AFTER trade open
                        #
                        voleyLoss = voleyLoss + 1
                        voleyTotal = voleyTotal + 1
                        voleyDropPL.append('LOSS')
                        writeStr2 = writeStr2 + 'CRAZY Loss voley with price going to volley take profit before opening the trade on ' + str(
                            dateListdf2[count]) + ' \nThe trade closed the gap at position ' + str(
                            GapClosedNum[
                                count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                            voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                            voleyTakeProfit[
                                count]) + '\nStop loss was reached at the following position ' + str(
                            gapClosedNumStr[
                                count]) + '\n----------------------------------------------------------------------------\n'
                else:
                    #
                    #  We have no value for take profit but plenty values for sl. closeBoon is true
                    #
                    # print('-------------')
                    voleyLoss = voleyLoss + 1
                    voleyTotal = voleyTotal + 1
                    voleyDropPL.append('LOSS')
                    myBool = True
                    checkBool = True
                    # print('KKK Loss voley on ' + str(
                    #     dateListdf2[count]) + ' \nThe trade closed the gap at position ' + str(
                    #     GapClosedNum[
                    #         count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                    #     voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                    #     voleyTakeProfit[
                    #         count]) + '\nStop loss was reached at the following position ' + str(
                    #     gapClosedNumStr[count]) + '\n----------------------------------------------------------------------------\n')
                    # print('-------------')
                    writeStr2 = writeStr2 + 'KKK Loss voley on ' + str(
                        dateListdf2[count]) + ' \nThe trade closed the gap at position ' + str(
                        GapClosedNum[
                            count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                        voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                        voleyTakeProfit[
                            count]) + '\nStop loss was reached at the following position ' + str(
                        gapClosedNumStr[count]) + '\n----------------------------------------------------------------------------\n'
            else:
                #
                # No value for SL. CHECK fo TP
                # if there is any value for take profit after trade open we are good
                if voleyTakeProfitPosStr[count] != 'NONE':
                    voleyDropPL.append('PROFIT')
                    myBool = True
                    checkBool = True
                    voleyTotal = voleyTotal + 1
                    voleyProfit = voleyProfit + 1
                    # print('-------------')
                    writeStr2 = writeStr2 + 'BLOCK Profit voley on ' +  str(
                        dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                        GapClosedNum[count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                        voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                        voleyTakeProfit[
                            count]) + '\nTake profit was reached at the following positionS ' + str(
                        voleyTakeProfitPosStr[count]) + '\n stop loss was never reached' + '\n' + '\n----------------------------------------------------------------------------\n'
                    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('BLOCK Profit voley on ' +  str(
                        dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                        GapClosedNum[count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                        voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                        voleyTakeProfit[
                            count]) + '\nTake profit was reached at the following positionS ' + str(
                        voleyTakeProfitPosStr[count]) + '\n stop loss was never reached' + '\n')
                    print('Gap close numbers' + str(forCheckMom))
                    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                else:
                    #
                    # No value for SL or TP
                    #
                    voleyDropPL.append('UNDETERMINED')
                    myBool = True
                    checkBool = True
                    voleyUn = voleyUn + 1
                    voleyTotal = voleyTotal + 1
                    writeStr2 = writeStr2 + 'Undetermined voley trade on ' + str(
                        dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                        GapClosedNum[
                            count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                        voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                        voleyTakeProfit[
                            count]) + '\nTake profit nor Stop Loss was never reached' + '\n----------------------------------------------------------------------------\n'
                    # print('Undetermined voley trade on ' + str(
                    #     dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
                    #     GapClosedNum[
                    #         count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
                    #     voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
                    #     voleyTakeProfit[
                    #         count]) + '\nTake profit nor Stop Loss was never reached' + '\n----------------------------------------------------------------------------\n')
        else:
            voleyDropPL.append('NONE')
            myBool = True
        #     checkBool = True
        # if not myBool:
        #     print('voley trade on ' + str(
        #                 dateListdf2[count]) + ' \nThe trade closed the gap at position' + str(
        #                 GapClosedNum[
        #                     count]) + ' \nPrice went back through 50% value opening the voley trade at ' + str(
        #                 voleyOpenPos[count]) + '\nTake profit value for this trade is set at: ' + str(
        #                 voleyTakeProfit[
        #                     count]) + '\n----------------------------------------------------------------------------\n')
        count = count + 1
        forCheckTP2.clear()
        forCheckTP.clear()
        forCloseLoop.clear()
        closeBoon = False
        checkBool = False
        myBool = False
        posTP = False

    print('%%%%%%%%%%%%%%%%%%%%%%%')
    print('Voley profit trades : ' + str(voleyProfit))
    print('Voley Loss trades  : ' + str(voleyLoss))
    print('Voley SIM trades ' + str(voleySim))
    print('Voley undetermined trades ' + str(voleyUn))
    print('TOTAL Voley value ' + str(voleyTotal))
    print('%%%%%%%%%%%%%%%%%%%%%%%')

    testval = pair[3:]
    if testval == 'JPY':
        stoploss1 = 0.01
        stoploss10 = 0.10
        stoploss15 = 0.15
        stoploss20 = 0.20
        stoploss25 = 0.25
        stoploss35 = 0.35
        stoploss50 = 0.50
    else:
        stoploss1 = 0.0001
        stoploss10 = 0.0010
        stoploss15 = 0.0015
        stoploss20 = 0.0020
        stoploss25 = 0.0025
        stoploss35 = 0.0035
        stoploss50 = 0.0050
    if pair == 'DE3030' or pair == 'US3030':
        stoploss1 = 1
        stoploss10 = 10
        stoploss15 = 15
        stoploss20 = 20
        stoploss25 = 25
        stoploss35 = 35
        stoploss50 = 50

    def gapSizeAnal(gapClassList, reverseProfitLoss, voleyDropPL):
        count = 0
        gapsizex = 0
        smallGapProfit = 0
        smallGapLosses = 0
        smallGapSim = 0
        smallGapUn = 0
        smallGapProfitV = 0
        smallGapLossesV = 0
        smallGapSimV = 0
        smallGapUnV = 0
        mediumGapProfit = 0
        mediumGapLosses = 0
        mediumGapSim = 0
        mediumGapUn = 0
        mediumGapProfitV = 0
        mediumGapLossesV = 0
        mediumGapSimV = 0
        mediumGapUnV = 0
        mediumGapProfit2 = 0
        mediumGapLosses2 = 0
        mediumGapSim2 = 0
        mediumGapUn2 = 0
        mediumGapProfitV2 = 0
        mediumGapLossesV2 = 0
        mediumGapSimV2 = 0
        mediumGapUnV2 = 0
        mediumGapProfit3 = 0
        mediumGapLosses3 = 0
        mediumGapSim3 = 0
        mediumGapUn3 = 0
        mediumGapProfitV3 = 0
        mediumGapLossesV3 = 0
        mediumGapSimV3 = 0
        mediumGapUnV3 = 0
        mediumGapProfit4 = 0
        mediumGapLosses4 = 0
        mediumGapSim4 = 0
        mediumGapUn4 = 0
        mediumGapProfitV4 = 0
        mediumGapLossesV4 = 0
        mediumGapSimV4 = 0
        mediumGapUnV4 = 0
        for items in gapClassList:
            if items == 'GAP':
                gapsizex = gapList[count]
                if gapsizex < 0:
                    gapsizex = gapsizex * -1
                if gapsizex < stoploss25:
                    if reverseProfitLoss[count] == 'PROFIT':
                        smallGapProfit = smallGapProfit + 1
                    if reverseProfitLoss[count] == 'LOSS':
                        smallGapLosses = smallGapLosses + 1
                    if reverseProfitLoss[count] == 'SIM':
                        smallGapSim = smallGapSim + 1
                    if voleyDropPL[count] == 'UNDETERMINED':
                        smallGapUn = smallGapUn + 1
                    if reverseProfitLoss[count] == 'PROFIT':
                        smallGapProfitV = smallGapProfitV + 1
                    if voleyDropPL[count] == 'LOSS':
                        smallGapLossesV = smallGapLossesV + 1
                    if voleyDropPL[count] == 'SIM':
                        smallGapSimV = smallGapSimV + 1
                    if voleyDropPL[count] == 'UNDETERMINED':
                        smallGapUnV = smallGapUnV + 1
                if gapsizex > stoploss25 and gapsizex < stoploss35:
                    if reverseProfitLoss[count] == 'PROFIT':
                        mediumGapProfit = mediumGapProfit + 1
                    if reverseProfitLoss[count] == 'LOSS':
                        mediumGapLosses = mediumGapLosses + 1
                    if reverseProfitLoss[count] == 'SIM':
                        mediumGapSim = mediumGapSim + 1
                    if reverseProfitLoss[count] == 'UNDETERMINED':
                        mediumGapUn = mediumGapUn + 1
                    if voleyDropPL[count] == 'PROFIT':
                        mediumGapProfitV = mediumGapProfitV + 1
                    if voleyDropPL[count] == 'LOSS':
                        mediumGapLossesV = mediumGapLossesV + 1
                    if voleyDropPL[count] == 'SIM':
                        mediumGapSimV = mediumGapSimV + 1
                    if voleyDropPL[count] == 'UNDETERMINED':
                        mediumGapUnV = mediumGapUnV + 1
                if gapsizex > stoploss35 and gapsizex < stoploss50:
                    if reverseProfitLoss[count] == 'PROFIT':
                        mediumGapProfit3 = mediumGapProfit3 + 1
                    if reverseProfitLoss[count] == 'LOSS':
                        mediumGapLosses3 = mediumGapLosses3 + 1
                    if reverseProfitLoss[count] == 'SIM':
                        mediumGapSim3 = mediumGapSim3 + 1
                    if reverseProfitLoss[count] == 'UNDETERMINED':
                        mediumGapUn3 = mediumGapUn3 + 1
                    if voleyDropPL[count] == 'PROFIT':
                        mediumGapProfitV3 = mediumGapProfitV3 + 1
                    if voleyDropPL[count] == 'LOSS':
                        mediumGapLossesV3 = mediumGapLossesV3 + 1
                    if voleyDropPL[count] == 'SIM':
                        mediumGapSimV3 = mediumGapSimV3 + 1
                    if voleyDropPL[count] == 'UNDETERMINED':
                        mediumGapUnV3 = mediumGapUnV3 + 1
                if gapsizex > stoploss50:
                    if reverseProfitLoss[count] == 'PROFIT':
                         mediumGapProfit4 = mediumGapProfit4 + 1
                    if reverseProfitLoss[count] == 'LOSS':
                        mediumGapLosses4 = mediumGapLosses4 + 1
                    if reverseProfitLoss[count] == 'SIM':
                        mediumGapSim4 = mediumGapSim4 + 1
                    if reverseProfitLoss[count] == 'UNDETERMINED':
                        mediumGapUn4 = mediumGapUn4 + 1
                    if voleyDropPL[count] == 'PROFIT':
                        mediumGapProfitV4 = mediumGapProfitV4 + 1
                    if voleyDropPL[count] == 'LOSS':
                        mediumGapLossesV4 = mediumGapLossesV4 + 1
                    if voleyDropPL[count] == 'SIM':
                        mediumGapSimV4 = mediumGapSimV4 + 1
                    if voleyDropPL[count] == 'UNDETERMINED':
                        mediumGapUnV4 = mediumGapUnV4 + 1
            count = count + 1

        #
        # STRAIGHT DRIVE
        #
        calcWinrate = 0
        totalCalc = 0
        interumTot = 0
        lineItems = []
        headerLine = (pair, pair, pair, pair, pair, pair, pair)
        lineItems.append(headerLine)
        headerLine = ('STRATEGY', 'TOTAL', 'PROFIT', 'LOSS', 'SIM', 'UN', 'WINRATE')
        lineItems.append(headerLine)
        headerLine = ('GAP UNDER 25 PIPS' , 'GAP UNDER 25 PIPS' , 'GAP UNDER 25 PIPS' , 'GAP UNDER 25 PIPS' , 'GAP UNDER 25 PIPS' , 'GAP UNDER 25 PIPS', 'GAP UNDER 25 PIPS')
        lineItems.append(headerLine)
        totalCalc = smallGapProfit + smallGapLosses + smallGapSim + smallGapUn
        interumTot = smallGapProfit + smallGapLosses
        if interumTot != 0:
            calcWinrate = (smallGapProfit/interumTot) * 100
        else:
            calcWinrate = 0
        subHeader = ('Straight Drive', totalCalc, smallGapProfit, smallGapLosses, smallGapSim, smallGapUn, calcWinrate)
        lineItems.append(subHeader)
        #
        # VOLEY DRIVE
        #

        totalCalc = smallGapProfitV + smallGapLossesV + smallGapSimV + smallGapUnV
        interumTot = smallGapProfitV + smallGapLossesV
        if interumTot != 0:
            calcWinrate = (smallGapProfitV/interumTot) * 100
        else:
            calcWinrate = 0

        subHeader = ('Volley Drive', totalCalc, smallGapProfitV, smallGapLossesV, smallGapSimV, smallGapUnV, calcWinrate)
        lineItems.append(subHeader)
        headerLine = (
        'GAP BETWEEN 25 and 35 PIPS', 'GAP BETWEEN 25 and 35 PIPS', 'GAP BETWEEN 25 and 35 PIPS', 'GAP BETWEEN 25 and 35 PIPS', 'GAP BETWEEN 25 and 35 PIPS',
        'GAP BETWEEN 25 and 35 PIPS', 'GAP BETWEEN 25 and 35 PIPS')
        lineItems.append(headerLine)

        #
        # STRAIGHT DRIVE
        #

        totalCalc = mediumGapProfit + mediumGapLosses + mediumGapSim + mediumGapUn
        interumTot = mediumGapProfit + mediumGapLosses
        if interumTot != 0 :
            calcWinrate = (mediumGapProfit/interumTot) * 100
        else:
            calcWinrate = 0
        subHeader = ('Straight Drive', totalCalc, mediumGapProfit, mediumGapLosses, mediumGapSim, mediumGapUn, calcWinrate)
        lineItems.append(subHeader)

        #
        # VOLLEY DRIVE
        #
        totalCalc = mediumGapProfitV + mediumGapLossesV + mediumGapSimV + mediumGapUnV
        interumTot = mediumGapProfitV + mediumGapLossesV
        if interumTot != 0:
            calcWinrate = (mediumGapProfitV/interumTot) * 100
        else:
            calcWinrate = 0
        gapSizeAnalSt = ''
        gapSizeAnalSt = gapSizeAnalSt + '\nWINRATE ' + str(calcWinrate)
        subHeader = (
        'Volley Drive', totalCalc, mediumGapProfitV, mediumGapLossesV, mediumGapSimV, mediumGapUnV, calcWinrate)
        lineItems.append(subHeader)
        #
        # MEDIUM 3
        #
        headerLine = (
            'GAP BETWEEN 35 and 50 PIPS', 'GAP BETWEEN 35 and 50 PIPS', 'GAP BETWEEN 35 and 50 PIPS',
            'GAP BETWEEN 35 and 50 PIPS', 'GAP BETWEEN 35 and 50 PIPS',
            'GAP BETWEEN 35 and 50 PIPS', 'GAP BETWEEN 35 and 50 PIPS')
        lineItems.append(headerLine)
        interumTot = mediumGapProfit3 + mediumGapLosses3
        if interumTot != 0:
            calcWinrate = (mediumGapProfit3/interumTot) * 100
        else:
            calcWinrate = 0
        subHeader = (
        'Straight Drive', totalCalc, mediumGapProfit3, mediumGapLosses3, mediumGapSim3, mediumGapUn3, calcWinrate)
        lineItems.append(subHeader)
        #
        # VOLLEY
        #
        totalCalc = mediumGapProfitV3 + mediumGapLossesV3 + mediumGapSimV3 + mediumGapUnV3
        interumTot = mediumGapProfitV3 + mediumGapLossesV3
        if interumTot != 0:
            calcWinrate = (mediumGapProfitV3 / interumTot) * 100
        else:
            calcWinrate = 0
        subHeader = (
            'Volley Drive', totalCalc, mediumGapProfitV3, mediumGapLossesV3, mediumGapSimV3, mediumGapUnV3, calcWinrate)
        lineItems.append(subHeader)
        headerLine = (
            'GAPS BIGGER THAN 50 PIPS', 'GAPS BIGGER THAN 50 PIPS', 'GAPS BIGGER THAN 50 PIPS',
            'GAPS BIGGER THAN 50 PIPS', 'GAPS BIGGER THAN 50 PIPS',
            'GAPS BIGGER THAN 50 PIPS', 'GAPS BIGGER THAN 50 PIPS')
        lineItems.append(headerLine)
        #
        # STRAIGH DRIVE
        #
        totalCalc = mediumGapProfit4 + mediumGapLosses4 + mediumGapSim4 + mediumGapUn4
        interumTot = mediumGapProfit4 + mediumGapLosses4
        if interumTot != 0:
            calcWinrate = (mediumGapProfit4/interumTot) * 100
        else:
            calcWinrate = 0
        subHeader = (
            'Straight Drive', totalCalc, mediumGapProfit4, mediumGapLosses4, mediumGapSim4, mediumGapUn4, calcWinrate)
        lineItems.append(subHeader)
        #
        # VOLLEY
        #
        interumTot = mediumGapProfitV4 + mediumGapLossesV4
        if interumTot != 0:
            calcWinrate = (mediumGapProfitV4/interumTot) * 100
        else:
            calcWinrate = 0
        gapSizeAnalSt = gapSizeAnalSt + '\nWINRATE ' + str(calcWinrate)
        subHeader = (
            'Volley Drive', totalCalc, mediumGapProfitV4, mediumGapLossesV4, mediumGapSimV4, mediumGapUnV4, calcWinrate)
        lineItems.append(subHeader)
        return gapSizeAnalSt, lineItems






    # df2['VoleyDrop'] = voleyDrop
    # df2['Voley PL'] = voleyDropPL
    #         VolleyOpen = halveGapValue[counter]
    #         straightOpen = openListDF2[counter]





    volleyStopLossValues = []
    volleyStopLossPos = []
    volleyStopLossValues = stopLossValues(halveGapValue, stoploss15)
    volleyStopLossPos = checkStopLossPositions(volleyStopLossValues)

    straightStopLossValues = []
    straightStopLossPos = []
    straightStopLossValues = stopLossValues(openListDF2, stoploss15)
    straightStopLossPos = checkStopLossPositions(straightStopLossValues)
    count = 0

    specialStraightPL = []
    specialVoleyPL = []
    #
    # RUNNING AT 15pip STOP
    #
    specialStraightPL, specialStraigString, specialTup15 = straightProfitFunc(straightStopLossPos, straightStopLossValues, 15)
    specialVoleyPL, specialVolleyString, volleyTup15 = voleyProfFunc(volleyStopLossPos,volleyStopLossValues, 15)

    #
    # Running 1 pip
    #

    # volleyStopLossValues = stopLossValues(halveGapValue, stoploss1)
    # volleyStopLossPos = checkStopLossPositions(volleyStopLossValues)
    #
    # straightStopLossValues = stopLossValues(openListDF2, stoploss1)
    # straightStopLossPos = checkStopLossPositions(straightStopLossValues)
    #
    # specialStraightPLonePip, specialStraigStringonePip, specialTup1 = straightProfitFunc(straightStopLossPos,
    #                                                                           straightStopLossValues, 1)
    # specialVoleyPLonePip, specialVolleyStringonePip, volleyTup1 = voleyProfFunc(volleyStopLossPos, volleyStopLossValues, 1)






    gapSizeCompStr = ''
    specialGapSizeCompStr = ''

    gapSizeCompStr, gapStandardAnal = gapSizeAnal(gapClassList, reverseProfitLoss, voleyDropPL)
    specialGapSizeCompStr, gapSpecialAnal = gapSizeAnal(gapClassList, specialStraightPL, specialVoleyPL)

    fileAnal = ''
    fileAnal = pair + 'GapAnal.csv'
    with open(fileAnal, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(gapStandardAnal)
        writer.writerows(gapSpecialAnal)







    count = 0
    headRowT = ('DATE','REVERSE', 'VOLLEY')
    headRow = []
    headRow.append(headRowT)
    date = ''
    reCheck = 0
    pl = ''
    op = ''
    inLineRow = []
    for items in dateListdf2:
        date = str(items)
        countTwo = count - 1
        if dateListdf2[count] != dateListdf2[countTwo]:
            if reverseProfitLoss[count] != 'NONE':
                pl = reverseProfitLoss[count]
                reCheck = reCheck + 1
            else:
                pl = ''
            if voleyDropPL[count] != 'NONE':
                op = voleyDropPL[count]
            else:
                op = ''
            dateLineTup = (pair, date, pl, op)
        count = count + 1


    count = 0
    headRowT = ('DATE','RESULT','OPEN')
    headRow = []
    reCheck = 0
    headRow.append(headRowT)
    date = ''
    pl = ''
    op = ''
    inLineRow = []
    with open('VoleyDateList.csv', 'w', newline='') as file:
        for items in dateListdf2:
            date = str(items)
            countTwo = count - 1
            if dateListdf2[count] != dateListdf2[countTwo]:
                if voleyDropPL[count] != 'NONE':
                    pl = voleyDropPL[count]
                    op = voleyOpenPos[count]
                    reCheck = reCheck + 1
                else:
                    pl = ''
                inlineTup = (date, pl, op)
                headRow.append(inlineTup)
            count = count + 1
        writer = csv.writer(file)
        writer.writerows(headRow)








    # reverseP = 0
    # reverseLoss = 0
    # reverseSIM = 0
    # reverseU = 0

    #
    # Calculate net R
    #

    netR = 0
    totalR = reverseP * 2
    netR = totalR - reverseLoss


    summaryTxt = ''
    summaryTxt = summaryTxt + '\n        ------------------------------------------\n'
    summaryTxt = summaryTxt + stringConstructor('Reverse profit trades : ' + str(reverseP)) + '\n'
    summaryTxt = summaryTxt + stringConstructor('Reverse Loss trades  : ' + str(reverseLoss)) + '\n'
    summaryTxt = summaryTxt + stringConstructor('Reverse SIM trades ' + str(reverseSIM)) + '\n'
    summaryTxt = summaryTxt + stringConstructor('Reverse undetermined trades ' + str(reverseU)) + '\n'
    summaryTxt = summaryTxt + stringConstructor('Total Reverse trades ' + str(tots)) + '\n'
    summaryTxt = summaryTxt + stringConstructor('Total R for 5 years ' + str(netR)) + '\n'
    summaryTxt = summaryTxt + '\n        ------------------------------------------\n'

    print('%%%%%%%%%%%%%%%%%%%%%%%')
    print('Reverse profit trades : ' + str(reverseP))
    print('Reverse Loss trades  : ' + str(reverseLoss))
    print('Reverse SIM trades ' + str(reverseSIM))
    print('Reverse undetermined trades ' + str(reverseU))
    print('tots value ' + str(tots))
    print('%%%%%%%%%%%%%%%%%%%%%%%')
    straightDriveTup = ()
    # volleyTup = (str(slPip), str(pair), 'Volley', vTotal, vProfit, vLoss, '', vSim, vUn, vR, netVR)

    straightDriveTup = ('', pair, 'STRAIGHT DRIVE ORIGINAL', tots, reverseP, reverseLoss, '', reverseSIM, reverseU)

    print('%%%%%%%%%%%%%%%%%%%%%%%')
    print('Voley profit trades : ' + str(voleyProfit))
    print('Voley Loss trades  : ' + str(voleyLoss))
    print('Voley SIM trades ' + str(voleySim))
    print('Voley undetermined trades ' + str(voleyUn))
    print('TOTAL Voley value ' + str(voleyTotal))
    print('%%%%%%%%%%%%%%%%%%%%%%%')
    voleyDriveTup = ()
    voleyDriveTup = ('', pair,'VOLLEY DRIVE ORIGINAL', voleyTotal, voleyProfit, voleyLoss, '', voleySim, voleyUn )

    voleyNet = (voleyProfit * 2) - voleyLoss

    summaryTxt2 = ''
    summaryTxt2 = summaryTxt2 + '\n        ------------------------------------------\n'
    summaryTxt2 = summaryTxt2 + stringConstructor('Volley profit trades : ' + str(voleyProfit)) + '\n'
    summaryTxt2 = summaryTxt2 + stringConstructor('Volley Loss trades  : ' + str(voleyLoss)) + '\n'
    summaryTxt2 = summaryTxt2 + stringConstructor('Volley SIM trades ' + str(voleySim)) + '\n'
    summaryTxt2 = summaryTxt2 + stringConstructor('Volley undetermined trades ' + str(voleyUn)) + '\n'
    summaryTxt2 = summaryTxt2 + stringConstructor('Total Volley trades ' + str(voleyTotal)) + '\n'
    summaryTxt2 = summaryTxt2 + stringConstructor('Total R for 5 years ' + str(voleyNet)) + '\n'
    summaryTxt2 = summaryTxt2 + '\n        ------------------------------------------\n'

    row_list = [['PAIR','STRATEGY','TOTAL TRADES','PROFIT TRADES', 'LOSS TRADES', 'SIM TRADES', 'UNDETERMINED'],
                [fileExtractname,'REVERSE TRADE', str(tots),str(reverseP),str(reverseLoss),str(reverseSIM),str(reverseU)],
                [fileExtractname,'VOLEY TRADE', str(voleyTotal), str(voleyProfit), str(voleyLoss), str(voleySim), str(voleyUn)]]

    with open('protagonist.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)









    filename = currencyPairing + " REVERSE TRADE_REPORT.txt"
    directory = './'+ pair + '/'
    file_path = os.path.join(directory, filename)
    if not os.path.isdir(directory):
        os.mkdir(directory)

    f = open( file_path, "w")
    f.write("--------------------------------------------TRADE REPORT--------------------------------------------------\n")
    f.write("-----------------------------------" + fileExtractname + "------------------------------------------------\n")
    f.write('\n\n')
    f.write('##############################################################################################################\n')
    f.write('#                                       ##################                                                   # \n')
    f.write('#                                    #######################                                                 #   \n')
    f.write('#                                 #############################                                              #      \n')
    f.write('#                               #######     #########     #######                                            #        \n')
    f.write('#                               ######       #######       ######                                            #        \n')
    f.write('#                               #######     #########     ######                                             #\n')
    f.write('#                                 ############     ###########                                               #\n')
    f.write('#                                    #########    #########                                                  #\n')
    f.write('#                                        ###############                                                     #\n')
    f.write('#                                         #############                                                      #\n')
    f.write('#                                            #######                                                         #\n')
    f.write('##############################################################################################################\n')
    f.write('       _____________________    _____  ________  _____________________ ___________________ \n')
    f.write('       \__    ___/\______   \  /  _  \ \______ \ \_   _____/\______   \\_____  \__    ___/ \n')
    f.write('         |    |    |       _/ /  /_\  \ |    |  \ |    __)_  |    |  _/ /   |   \|    |   \n')
    f.write('         |    |    |       _/ /  /_\  \ |    |  \ |    __)_  |    |  _/ /   |   \|    |   \n')
    f.write('         |    |    |    |   \/    |    \|    `   \|        \ |    |   \/    |    \    |  \n')
    f.write('         |____|    |____|_  /\____|__  /_______  /_______  / |______  /\_______  /____|   \n')
    f.write('                          \/         \/        \/        \/         \/         \/         \n')
    f.write('##############################################################################################################\n')
    f.write('-----------------------------------------SPECIAL STRAIGHT STRING-----------------------------------------------\n')
    f.write(specialStraigString)
    f.write(
        '\n-----------------------------------------SPECIAL VOLLEY STRING-----------------------------------------------\n')
    f.write(specialVolleyString)
    f.write('\n______________________________________STRAIGHT DRIVE / 50% THEN RETURN TO OPEN_______________________________________\n')
    f.write(summaryTxt)
    f.write(writeStr)
    f.write('______________________________________VOLEYDRIVE / CLOSE GAP, RETURN TO 50%_______________________________________\n')
    f.write(summaryTxt2)
    f.write(writeStr2)
    f.write('----------------------------------------------------------END OF FILE-------------------------------------------------------------- \n')


    countTwo = 0
    dateTupList = []
    headRow = []
    headRow = ('PAIR','DATE', 'STRAIGH FIXED SL', 'STRAIGHT R-VALUE','VOLLEY FIXED SL', 'VOLLEY R-Value' ,'STRAIGHT STANDARD', 'VOLLEY STANDARD')
    dateTupList.append(headRow)
    count = 0
    sPL = ''
    vPL = ''
    svPL = ''
    ssPL = ''
    sPLR = ''
    for items in dateListdf2:
        date = str(items)
        countTwo = count - 1
        if dateListdf2[count] != dateListdf2[countTwo]:
            if specialStraightPL[count] != 'NONE':
                sPLBase = specialStraightPL[count]
                sPL = sPLBase[0]
                if sPL == 'profit':
                    sPLR = float(sPLBase[1])
                else:
                    sPLR = ''
                if sPL == 'L':
                    sPL = 'LOSS'
                if sPL == 'U':
                    sPL = 'UNDETERMINED'
                if sPL == 'S':
                    sPL = 'SIM'
            else:
                sPL = ''
                sPLR = ''
            if specialVoleyPL[count] != 'NONE':
                vPLBASE = specialVoleyPL[count]
                vPL = vPLBASE[0]
                if vPL == 'profit':
                    vplR = float(vPLBASE[1])
                else:
                    vplR = ''
                if vPL == 'L':
                    vPL = 'LOSS'
                if vPL == 'U':
                    vPL = 'UNDETERMINED'
                if vPL == 'S':
                    vPL = 'SIM'
            else:
                vPL = ''
                vplR = ''
            if voleyDropPL[count] != 'NONE':
                svPL = voleyDropPL[count]
            else:
                svPL = ''
            if reverseProfitLoss[count] != 'NONE':
                ssPL = reverseProfitLoss[count]
            else:
                ssPL = ''
            dateLineTup = (pair, date, sPL, sPLR, vPL, vplR ,ssPL, svPL)
            dateTupList.append(dateLineTup)
        count = count + 1
    filename = 'dateList' + pair + '.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(dateTupList)



    return specialTup15, volleyTup15, straightDriveTup, voleyDriveTup, dateTupList

# with open('test.csv', 'w', newline='') as file:
#     writer = csv.writer(file)
#     myTup = ('1', 'EURNZD', 'Straight', '62', '6', '55', '', '1', '0', 234.50000000002555)
#     writer.writerows(myTup)


stv = []
dateLine = []
with open('consolodatedGap.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup = operator('EURNZD')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup = operator('US3030')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup  =operator('AUDUSD')
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup  =operator('AUDJPY')
    stv.append(straightDriveTup)
    stv.append(specialTupple15)
    stv.append(voleyDriveTup)
    stv.append(volleyTupple15)
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup  =operator('AUDUSD')
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup  =operator('CADCHF')
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)

    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup  =operator('CADJPY')
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #EURAUD
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup  =  operator('EURAUD')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup  =operator('EURCAD')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #EURGBP
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup  =operator('EURGBP')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup  =operator('EURUSD')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup  =operator('GBPAUD')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #GBPJPY
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup  =operator('GBPJPY')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    #
    # GPBNZD
    #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup  =operator('GBPNZD')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    #
    # GBPUSD
    #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup  =operator('GBPUSD')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    #
    #
    #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup  =operator('NZDCAD')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup =operator('NZDJPY')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup =operator('NZDUSD')
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    #
    # AUDCAD
    #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup =operator('AUDCAD')
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup =operator('AUDCHF')
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup =operator('AUDNZD')
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup =operator('CHFJPY')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup =operator('DE3030')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup =operator('EURCHF')
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup =operator('EURJPY')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #gbpcad
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup =operator('GBPCAD')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup =operator('GBPCHF')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup =operator('USDCHF')
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup =operator('USDJPY')
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup = operator('USDCAD')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # #
    # #
    # #
    # specialTupple15, volleyTupple15, straightDriveTup, voleyDriveTup, dateLineTup = operator('NZDCHF')
    # dateLine.append(dateLineTup)
    # stv.append(straightDriveTup)
    # stv.append(specialTupple15)
    # stv.append(voleyDriveTup)
    # stv.append(volleyTupple15)
    # writer.writerows(stv)















