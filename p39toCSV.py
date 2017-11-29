import sys
import os
from collections import OrderedDict

import lxml
from lxml import etree

schemaFile = os.path.join('schema_files','UtilDataProp39Report.xsd')

def getTextValues(node, valueConf, ns, defaultValue='' ):
    out = []
    for (xmlName, exportName) in valueConf:
        #print xmlName, exportName
        if node is None:
            out.append( (exportName, defaultValue) )
        else:
            targetNode = node.find('.%s' % (xmlName), ns)
            if targetNode is not None:
                out.append( (exportName, targetNode.text) )
            else:
                #print 'No target node found: %s' % (xmlName)
                out.append( (exportName, defaultValue) )
    return out

def getUsage(observation, ns=None):
    '''Return a tuple of energy recieved by the customer and energy produced by the customer
If there is no solar, there is just EnergyUsage;
If there is solar, EnergyDelivered is from the grid and EnergyRecieved is from the customer
'''
    try:
        usage = observation[1].find('./uti:IntervalReading_EnergyUsage', ns)
        if usage is not None: return (usage.text, '0.0')
        else:
            delivered = observation[1].find('./uti:IntervalReading_EnergyDelivered', ns)
            received  = observation[1].find('./uti:IntervalReading_EnergyReceived', ns)
            return ( delivered.text,
                     received.text   )
    except AttributeError as ae:
        print observation[1].getchildren()
        raise ae

def getSchoolMeta(node, ns):
    schoolMetaConf = [('//uti:UtilitySender', 'utility'),
                      ('//uti:Customer_CustomerName', 'customer_name'),
                      ('//uti:Customer_City', 'customer_city'),
                      ('//uti:Customer_ZipPlus4', 'customer_zip'),
                      ('//uti:Customer_AccountNumber', 'customer_account'),
                      ('//uti:LEA_CustomerName', 'lea_customer'),
                      ('//uti:SchoolSite_CDSCode', 'cds_code'),
                      ('//uti:SchoolSite_SchoolSiteName', 'school_site_name'),
                      ('//uti:SchoolSite_City', 'school_city'),
                      ('//uti:SchoolSite_ZipPlus4', 'school_site_zip'), ]
    schoolMeta = getTextValues(node, schoolMetaConf, ns)
    return schoolMeta

def loadDoc(dataFile):
    #print 'Loading %s' % dataFile
    with open(schemaFile) as f:
        schema = etree.XMLSchema(etree.parse(f))
        #print "Schema OK; loading document"
    with open(dataFile) as f:
        dataDoc = etree.parse(f)
    #print "Validating document ..."
    try:
        schema.assertValid(dataDoc)
    except lxml.etree.DocumentInvalid as validationError:
        print 'WARNING: XML document did not pass schema validation: %s' % (str(validationError))
    #print "Document OK"
    return dataDoc

def getNSMap(dataDoc):
    # see http://stackoverflow.com/questions/14853243/parsing-xml-with-namespace-in-python-via-elementtree
    # ns = {'uti' : 'http://www.lmonte.com/prop39/UtilDataProp39Report'}
    ns = dataDoc.getroot().nsmap
    # None and '' are not valid namespace names, but they are sometimes returned anyway!
    try: del ns[None]
    except: pass
    try: del ns['']
    except: pass
    ns['uti'] = 'http://www.lmonte.com/prop39/UtilDataProp39Report'  # hack because this is sometimes missing
    return ns

def billsToCSV(dataDoc, csvFile):
    root = dataDoc.getroot()
    ns = getNSMap(dataDoc)
    print 'Writing data to %s' % csvFile
    tmpFile = csvFile + '.tmp'
    billDataConf = [('/uti:ElectricityMonthly_RateScheduleID', 'rate_schedule_id'),
                    ('/uti:ElectricityMonthly_BillingPeriodNumberOfDays', 'n_days'),
                    ('/uti:ElectricityMonthly_EnergyGenerationOnSite', 'generation'),
                    ('/uti:ElectricityMonthly_StartTime', 'start_time'),
                    ('/uti:ElectricityMonthly_BillLastPeriod', 'last_period'),
                    ('/uti:ElectricityMonthly_ConsumptionBillingPeriodTotal', 'consumption_total'),
                    ('//uti:ElectricityMonthly_ConsumptionOnPeak', 'on_peak'),
                    ('//uti:ElectricityMonthly_ConsumptionSemiPeak', 'semi_peak'),
                    ('//uti:ElectricityMonthly_ConsumptionOffPeak', 'off_peak'),
                    ('//uti:ElectricityMonthly_DemandMaximumOnPeak', 'on_peak_demand'),
                    ('//uti:ElectricityMonthly_DemandMaximumSemiPeak', 'semi_peak_demand'),
                    ('//uti:ElectricityMonthly_DemandMaximumOffPeak', 'off_peak_demand'), ]
    with open(tmpFile, 'wb') as csvOut:
        # write header line
        schoolMeta = getSchoolMeta(root, ns)
        header = [x[0] for x in schoolMeta]
        header.extend( ['agreement','units','demandUnits'] )
        header.extend( [x[1] for x in billDataConf] )
        csvOut.write( ','.join( header ) + '\n' )
        for account in root.findall('.//uti:ElectricityMonthlyBillDataPerAgreement', ns):
            #print account
            bills = account.findall('.//uti:ElectricityMonthlyBillData', ns)
            if len(bills) > 0:
                agreement = account.find('./uti:ElectricityMonthly_AgreementIdentifier', ns).text
                units = account.find('./uti:ElectricityMonthly_ConsumptionUnitOfMeasure', ns).text
                demandUnits = account.find('./uti:ElectricityMonthly_MaximumDemandUnitOfMeasure', ns).text
                meta = [agreement, units, demandUnits]
                for bill in bills:
                    textValues = getTextValues(bill, billDataConf, ns)
                    row = [x[1] for x in schoolMeta]
                    row.extend(meta)
                    row.extend( [x[1] for x in textValues] ) # add bill readings
                    csvOut.write(','.join([str(x) for x in row]) + '\n' )
                    #print textValues.values()
    try:
        if os.path.exists(csvFile): os.remove(csvFile)
        os.rename(tmpFile, csvFile)
    except:
        print 'Error renaming file %s we will continue to others.' % csvFile

def intervalsToCSV(dataDoc, csvFile):
    root = dataDoc.getroot()
    ns = getNSMap(dataDoc)
    print 'Writing data to %s' % csvFile
    tmpFile = csvFile + '.tmp'
    with open(tmpFile, 'wb') as csvOut:

        csvOut.write('%s,%s,%s,%s\n' % ('agreement',
                                        'start',
                                        ','.join(['d' + str(i+1) for i in range(100)]),
                                        ','.join(['r' + str(i+1) for i in range(100)])))

        for account in root.findall('.//uti:ElectricityIntervalData', ns):
            days = account.findall('.//uti:IntervalBlockDay', ns)
            if len(days) > 0:
                agreements = account.findall('./uti:ElectricityInterval_AgreementIdentifier', ns)
                if len(agreements) > 0:
                    agreement = account.find('./uti:ElectricityInterval_AgreementIdentifier', ns).text
                    print 'Agreement: %s; CDS code: %s' % (agreement, cds_code)
                    print '%s days of data' % len(days)
                    for day in days:
                        nobs = day.find('./uti:IntervalReadingLength_IntervalLength', ns).text
                        start = day.find('./uti:IntervalBlockDay_StartTime', ns).text
                        obs = day.findall('.//uti:IntervalReadings', ns)
    
                        readings = [getUsage(ob, ns) for ob in obs]
                        if len(readings) == 96:
                            readings.extend([('', '')] * 4)
                        if len(readings) == 92:
                            readings.extend([('', '')] * 8)
                        if len(readings) == 24:
                            readings.extend([('', '')])
                        if len(readings) == 93:
                            readings.extend([('', '')] * 2)
                        csvOut.write('%s,%s,%s,%s\n' % (agreement,
                                                        start,
                                                        ','.join([x[0] for x in readings]),
                                                        ','.join([x[1] for x in readings])))
                        #print '%s,%s,%s,%s' % (agreement,
                        #                       start,
                        #                       ','.join([x[0] for x in readings]),
                        #                       ','.join([x[1] for x in readings]))
    try:
        if os.path.exists(csvFile): os.remove(csvFile)
        os.rename(tmpFile,csvFile)
    except:
        print 'Error renaming file %s we will continue to others.' % csvFile


if __name__ == '__main__':
    skipExisting = True
    path = 'sample_data'  # relative path to data directory
    output_path = 'csv'   # relative path to output directory
    if len(sys.argv) > 1: # allow for command line override of path
        path = sys.argv[1]
    if len(sys.argv) > 2: # allow for command line override of output path
        output_path = sys.argv[2]

    print 'Converting all sample data from %s' % path

    for root, dirs, files in os.walk(path):
    
        # replicate directory structure under output_path directory
        for d in dirs:
            out_d = os.path.join(output_path, os.path.relpath(root, path), d)
            if not os.path.exists(out_d):
                os.makedirs(out_d)

        potentialFiles = [os.path.join(root, f) for f in os.listdir(root)]
        # data files are considered all xml files.
        dataFiles = [f for f in potentialFiles if os.path.isfile(f) and f.lower().endswith(".xml")]
        n = len(dataFiles)
        for (i,dataFile) in enumerate(dataFiles):
            print '%s (%d/%d)' % (dataFile,i+1,n)
            outputFile = os.path.join(output_path, os.path.relpath(dataFile, path)) 
            csvIntervalFile = outputFile + '_INTERVAL.csv'
            csvBillFile = outputFile + '_BILL.csv'
            dataDoc = None
            # dump metadata
    
            # dump billing data
            if os.path.exists(csvBillFile) and skipExisting:
                print '%s already exists. Skipping conversion.' % csvBillFile
            else:
                if dataDoc is None: dataDoc = loadDoc(dataFile)
                billsToCSV(dataDoc, csvBillFile)
    
            # dump intervals
            if os.path.exists(csvIntervalFile) and skipExisting:
                print '%s already exists. Skipping conversion.' % csvIntervalFile
            else:
                dataDoc = loadDoc(dataFile)
                intervalsToCSV(dataDoc, csvIntervalFile)
    
        #dataFile = '45700116097703_20142015_PacificGasElectric_ELECTRIC_20151223.xml'




# obs = root \
#    .getchildren()[3] \     #-> [0] UtilitySender 'PacificGasElectric'
#                            #-> [1] ReportingPeriod '2014-07-01Through2015-06-30'
#                            #-> [2] Prop39SchemaVersion 'P39 XML 1.004'
#                            #-> [3] DocumentData
#    .getchildren()[0] \     #-> [0] utilDataProp39Report
#    .getchildren()[3] \     #-> [0] LEA_Customer_CDSCode
#                            #-> [1] LEA_CustomerData
#                            #-> [2] SchoolSiteData
#                            #-> [3] UsageData
#    .getchildren()[0] \     #-> [0] ElectricityUsageData
#    .getchildren()[5] \     #-> [0] ElectricityMonthlyBillDataPerAgreement
#                            #-> [1] ElectricityMonthlyBillDataPerAgreement
#                            #-> [2] ElectricityMonthlyBillDataPerAgreement
#                            #-> [3] ElectricityMonthlyBillDataPerAgreement
#                            #-> [4] ElectricityIntervalData
#                            #-> [5] ElectricityIntervalData
#                            #-> [6] ElectricityIntervalData
#                            #-> [7] ElectricityIntervalData
#    .getchildren()[2] \     #-> [0] ElectricityInterval_AgreementIdentifier '0428871646'
#                            #-> [1] ElectricityInterval_ConsumptionUnitOfMeasure 'kWh'
#                            #-> [2] ElectricityIntervalDataForAgreement
#    .getchildren()[0] \     #-> [0:364] IntervalBlockDay
#    .getchildren()[3]       #-> [0] IntervalReadingLength_IntervalLength (900) i.e. 15 minute
#                            #-> [1] IntervalBlockDay_DurationInSeconds (86400) i.e. 24 hour
#                            #-> [2] IntervalBlockDay_StartTime
#                            #-> [3:98] IntervalReadings
#    .getchildren()[0]       #-> [0] IntervalReading_StartTime
#                            #-> [1] IntervalReadingEnergy
#    .text                   #-> 'kWh' for 0 and '0.231' for [1].find('./uti:IntervalReading_EnergyReceived').text


#obs.getchildren()[0].text # IntervalReading_StartTime
#obs.getchildren()[1].text # IntervalReadingEnergy