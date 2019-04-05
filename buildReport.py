#Script to generate an ad copy report by Patrick O'Doherty (1-3-19)
import os, csv, xlsxwriter, datetime
from functions import *
from googleads import adwords
from datetime import date

#pylint: disable=no-value-for-parameter
#pylint: disable=no-member

#adList is a dictonary of lists
#a dictonary is an array that is indexed with unique indices, in this implementation the
#ad groups are the different indexes in the dictonary, the lists that are in these spots or 'indexes'
#will be the actual list data.
#so adList['Branded'] will contain a list of branded ads
adList = {}
keywordList = {}
customers = {}

# Initalize AdWords client
yaml_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'googleads.yaml')

adwords_client = adwords.AdWordsClient.LoadFromStorage(yaml_file_path)

adwords_client.SetClientCustomerId('904-054-7932')

customers = getCustomerIDs(adwords_client)

for customer in customers:
    adList.clear()
    keywordList.clear()

    adwords_client.SetClientCustomerId(customer)


    adCopyQuery = (adwords.ReportQueryBuilder()
                    .Select('AccountDescriptiveName', 'CampaignName', 'AdGroupName', 'HeadlinePart1',
                            'HeadlinePart2', 'ExpandedTextAdHeadlinePart3', 'Description', 'ExpandedTextAdDescription2',
                            'CreativeFinalUrls')
                    .From('AD_PERFORMANCE_REPORT')
                    .Where('Status').In('ENABLED')
                    .Where('AdGroupStatus').In('ENABLED')
                    .Where('CampaignStatus').In('ENABLED')
                    .During('LAST_MONTH')
                    .Build())

    adKeywordQuery = (adwords.ReportQueryBuilder()
                        .Select('AccountDescriptiveName', 'CampaignName', 'AdGroupName', 'Criteria')
                        .From('KEYWORDS_PERFORMANCE_REPORT')
                        .Where('Status').In('ENABLED')
                        .Where('AdGroupStatus').In('ENABLED')
                        .Where('CampaignStatus').In('ENABLED')
                        .During('LAST_MONTH')
                        .Build())

    accountNameQuery = (adwords.ReportQueryBuilder()
                        .Select('AccountDescriptiveName', 'CampaignName', 'AdGroupName', 'Criteria')
                        .From('KEYWORDS_PERFORMANCE_REPORT')
                        .Where('Status').In('ENABLED')
                        .During('LAST_MONTH')
                        .Build())

    communityName = dataumQuery(adwords_client, accountNameQuery)
    
    reportQuery(adwords_client, adCopyQuery, 'files/adCopy.csv')
    reportQuery(adwords_client, adKeywordQuery, 'files/adKeywords.csv')

    ###Read in data
    #
    #Initalize the dictonary with an empty list
    initDictonary('files/adCopy.csv', adList)
    initDictonary('files/adKeywords.csv', keywordList)

    #Remove empty lists from dictonaries
    adList.pop('')
    keywordList.pop('')
    adList.pop(' --')
    keywordList.pop(' --')
    adList.pop('Ad group')
    keywordList.pop('Ad group')

    # print(keywordList['Assisted Living Local'])

    ###Generate output workbook
    #
    #Build output
    workbook = xlsxwriter.Workbook("files/" + communityName + "_adCopy.xlsx")
    worksheetCover = workbook.add_worksheet("Cover")
    worksheet = workbook.add_worksheet("Ad Copy & Keywords")

    #Set font type of workbook
    workbook.formats[0].set_font_name("Avenir Book")
    workbook.formats[0].set_font_size(9)

    #Create cell formats
    title_format = workbook.add_format({'bold' : True, 'font_name' : 'Avenir Book'})
    adgroup_title_format = workbook.add_format({'bold' : True, 'bg_color' : '#088BA3', 'font_color' : 'white', 'font_name' : 'Avenir Book' })
    adgroup_headings = workbook.add_format({'bold' : True, 'bg_color' : '#D9D9D9', 'font_size' : 8, 'font_name' : 'Avenir Book', 'align' : 'center', 'valign' : 'vcenter'})
    cover_title_format = workbook.add_format({'bold' : True, 'font_name' : 'Avenir Book','align': 'center', 'valign': 'vcenter'})

    #Cover Page
    today = date.today().strftime('%m/%d/%Y')

    worksheetCover.insert_image('A1', 'src/orchardLogo.png',{'x_scale': .25, 'y_scale': .25,'x_offset': 225})
    worksheetCover.merge_range('B14:J15', 'Paid Search Ad Copy & Keywords', cover_title_format)
    worksheetCover.merge_range('B14:J15', communityName, cover_title_format)
    worksheetCover.merge_range('B16:J17', 'Paid Search Keyword Report: ' + str(today), cover_title_format)


    #Make title
    worksheet.insert_image('A1', 'src/orchardLogo.png', {'x_scale': 0.08, 'y_scale': 0.08})
    #Format column sizes sizes
    worksheet.set_column('A:A', 45)
    worksheet.set_column('B:B', 5)
    worksheet.set_column('C:C', 25)
    worksheet.set_column('D:D', 25)
    worksheet.set_column('E:E', 25)
    worksheet.set_column('F:F', 5)
    worksheet.set_column('G:G', 25)
    worksheet.set_column('H:H', 25)
    worksheet.set_column('I:I', 25)
    worksheet.set_column('J:J', 5)

    worksheet.merge_range('A4:C4', 'Paid Search Ad Copy & Keywords', title_format)

    #Generate ad group sections
    currentPos = 6 #keeps track of the row we're working with in the worksheet
    newPos = currentPos + 2 #sets the row position to start from when generating next ad group
    adGroupLen = 0
    printPos = 0 #keeps track of if we're printing the ad info on the left or right. 0 is left, 1 is right

    for adGroup in adList:
        newPos = currentPos + 2
        worksheet.merge_range('A' + str(currentPos) + ':J' + str(currentPos), adGroup + ' Ad Group', adgroup_title_format)
        worksheet.write('A' + str(currentPos + 1), 'KEYWORDS', adgroup_headings)

        #Stream in keywords
        try:
            for keyword in range(len(keywordList[adGroup])):
                worksheet.write('A' + str(newPos), keywordList[adGroup][keyword][3])
                newPos +=  1

            worksheet.write('B' + str(currentPos + 1), '', adgroup_headings)

            #Stream in ad information
            for ad in range(len(adList[adGroup])):
                if printPos == 0:
                    worksheet.merge_range('C' + str(currentPos + 1) + ':E' + str(currentPos + 1), "AD " + str(ad + 1), adgroup_headings)
                    #write headlines
                    worksheet.write('C' + str(currentPos + 2), adList[adGroup][ad][3])
                    worksheet.write('D' + str(currentPos + 2), adList[adGroup][ad][4])
                    worksheet.write('E' + str(currentPos + 2), adList[adGroup][ad][5])
                    #write sizes of the headlines below
                    worksheet.write('C' + str(currentPos + 3), len(adList[adGroup][ad][3]))
                    worksheet.write('D' + str(currentPos + 3), len(adList[adGroup][ad][4]))
                    worksheet.write('E' + str(currentPos + 3), len(adList[adGroup][ad][5]))
                    
                    #write descriptions
                    worksheet.merge_range('C' + str(currentPos + 4) + ':E' + str(currentPos + 4), adList[adGroup][ad][6])
                    worksheet.merge_range('C' + str(currentPos + 5) + ':E' + str(currentPos + 5), adList[adGroup][ad][7])
                    #write sizes of descriptions
                    worksheet.write('F' + str(currentPos + 4), len(adList[adGroup][ad][6]))
                    worksheet.write('F' + str(currentPos + 5), len(adList[adGroup][ad][7]))
                    #write final url
                    worksheet.merge_range('C' + str(currentPos + 6) + ':E' + str(currentPos + 6), adList[adGroup][ad][8])
                    worksheet.write('F' + str(currentPos + 1), '', adgroup_headings)
                    printPos = 1
                else:
                    worksheet.merge_range('G' + str(currentPos + 1) + ':I' + str(currentPos + 1), "AD " + str(ad + 1), adgroup_headings)
                    #write headlines
                    worksheet.write('G' + str(currentPos + 2), adList[adGroup][ad][3])
                    worksheet.write('H' + str(currentPos + 2), adList[adGroup][ad][4])
                    worksheet.write('I' + str(currentPos + 2), adList[adGroup][ad][5])
                    #write sizes of the headlines below
                    worksheet.write('G' + str(currentPos + 3), len(adList[adGroup][ad][3]))
                    worksheet.write('H' + str(currentPos + 3), len(adList[adGroup][ad][4]))
                    worksheet.write('I' + str(currentPos + 3), len(adList[adGroup][ad][5]))
                    
                    #write descriptions
                    worksheet.merge_range('G' + str(currentPos + 4) + ':I' + str(currentPos + 4), adList[adGroup][ad][6])
                    worksheet.merge_range('G' + str(currentPos + 5) + ':I' + str(currentPos + 5), adList[adGroup][ad][7])
                    #write sizes of descriptions
                    worksheet.write('J' + str(currentPos + 4), len(adList[adGroup][ad][6]))
                    worksheet.write('J' + str(currentPos + 5), len(adList[adGroup][ad][7]))
                    #write final url
                    worksheet.merge_range('G' + str(currentPos + 6) + ':I' + str(currentPos + 6), adList[adGroup][ad][8])
                    worksheet.write('J' + str(currentPos + 1), '', adgroup_headings)
                    printPos = 0
                    currentPos += 7
            
            #this if statement moves the current position if we last printed on the left
            if printPos == 1:
                currentPos += 7
                printPos = 0
            if newPos > currentPos:
                currentPos = newPos
        except KeyError:
            #handle
            pass


    worksheet.merge_range('A' + str(currentPos) + ':J' + str(currentPos), '', adgroup_title_format)
    workbook.close()