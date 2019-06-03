import xml.etree.ElementTree as ET
#from lxml.builder import ElementMaker  # lxml only !
import lxml.builder as builder
from lxml import etree
from datetime import datetime
import xmltodict, json
from jsonParser import loadActivities


global_seq = 0

total_amount = 0
activity_count = 0
aa_count = 0
attachment_count = 0


def seqNum(num):
    global global_seq
    global_seq += 1
    return {'SeqNum': str(num)}


def currentDate():
    date = str(datetime.today())[:10]
    date = date.replace('-', '')
    return date


# Generates SAR E-File Batch Meta Data
def batchAttributes(ta, pc, ac, aac, atc):
    result = {}
    result['TotalAmount'] = str(ta)
    result['PartyCount'] = str(pc)
    result['ActivityCount'] = str(ac)
    result['ActivityAttachmentCount'] = str(aac)
    result['AttachmentCount'] = str(atc)
    result['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = 'www.fincen.gov/base SARXBatchSchema.xsd'
    return result

def defineNamespace():
    return builder.ElementMaker(namespace="www.fincen.gov/base",
                 nsmap={'fc2': "www.fincen.gov/base", 'xsi': "http://www.w3.org/2001/XMLSchema-instance", 'xsd': "http://www.w3.org/2001/XMLSchema",
                        'vc': "http://www.w3.org/2007/XMLSchema-versioning"})
# Defines All namespaces and default namespace
E = defineNamespace()


# Defines Elements of the Batch File
BATCH = E.EFilingBatchXML
FORMTYPECODE = E.FormTypeCode
ACTIVITY = E.Activity
PARTY = E.Party
TITLE = E.Title
APTC = E.ActivityPartyTypeCode
FILEDATE = E.FilingDateText
AA = E.ActivityAssociation
SA = E.SuspiciousActivity
SADATE = E.SuspiciousActivityFromDateText
SACLASS = E.SuspiciousActivityClassification
SASUBTYPE = E.SuspiciousActivitySubtypeID
SATYPE = E.SuspiciousActivityTypeID
SATSA = E.TotalSuspiciousAmountText
ANI = E.ActivityNarrativeInformation
ANISEQNUM = E.ActivityNarrativeSequenceNumber
ANITEXT = E.ActivityNarrativeText
PRTC = E.PrimaryRegulatorTypeCode
PNTC = E.PartyNameTypeCode
PN = E.PartyName
RPFN = E.RawPartyFullName

#Phone Number Elements
PHONENUM = E.PhoneNumber
PNTEXT = E.PhoneNumberText

#Address Elements 
ADDR = E.Address
RCT = E.RawCityText
RCCT = E.RawCountryCodeText
RSCT = E.RawStateCodeText
RSAT = E.RawStreetAddress1Text
RZIP = E.RawZIPCode

#Party Identification
PI = E.PartyIdentification
PINT = E.PartyIdentificationNumberText
PITC = E.PartyIdentificationTypeCode
PRTC = E.PrimaryRegulatorTypeCode #1- Federal Reserve, 2 - FTIC, 3 - NCUA, 7 - IRS

OCTS = E.OrganizationClassificationTypeSubtype
OSID = E.OrganizationSubtypeID #5999 = Other for Casino?
OTID = E.OrganizationTypeID  #999 = Other, 1 = Casino, 2 = Depository, 3 = Insurance Company
OOSS = E.OtherOrganizationSubTypeText
OOTT = E.OtherOrganizationTypeText
# Party Functions
def transmitter():
    result = PARTY(APTC("35"),
            PN(seqNum(global_seq), PNTC("L"), RPFN("LedgerSafe")),
            ADDR(RCT("SD"), RCCT("US"), RSCT("CA"), RSAT("1 Nice Lane"), RZIP("92111"),seqNum(global_seq)),
            PHONENUM(PNTEXT("7777777777"), seqNum(global_seq)),
            PI(PINT("TCC Code"), PITC("28"), seqNum(global_seq)),
            PI(PINT("TIN Number"), PITC("4"), seqNum(global_seq)),
            seqNum(global_seq)
        )
    return result

def transmitterContact():
    result = PARTY(APTC("37"),
                PN(seqNum(global_seq), PNTC("L"), RPFN("LedgerSafe CSO")),
                seqNum(global_seq)
            )
    return result

def filingInstituion():
    result = PARTY(APTC("30"),
                PRTC("1"),
                PN(seqNum(global_seq), PNTC("L"), RPFN("LS FI Partner")),
                ADDR(RCT("SD"), RCCT("US"), RSCT("CA"), RSAT("2 Bank Lane"), RZIP("90210"), seqNum(global_seq)),
                PI(PINT("TCC Code"), PITC("28"), seqNum(global_seq)),
                OCTS(OSID("5999"), OTID("999"),OOSS("TBD"),OOTT("MRB"), seqNum(global_seq)),
                seqNum(global_seq)
            )
    return result

def contactOffice():
    result = PARTY(APTC("8"),
                PN(seqNum(global_seq), PNTC("L"), RPFN("Contact Office Name")),
                PHONENUM(PNTEXT("12312312345"), seqNum(global_seq)),
                seqNum(global_seq)
            )
    return result

def subject(name):
    result = PARTY(APTC("33"),
                PN(seqNum(global_seq), PNTC("DBA"),
                RPFN(name)),
                seqNum(global_seq)
            )
    return result
    
def activityOccured():
    result = PARTY(APTC("34"),
                PRTC("1"),
                PN(seqNum(global_seq), PNTC("L")),
                seqNum(global_seq)
            )
    return result

#Suspicious Activity Function
def suspiciousActivity(date, amount):
    result = SA(SADATE(date),
                SATSA(str(amount)),
                SACLASS(
                    SASUBTYPE("106"), SATYPE("1"), seqNum(global_seq)
                ),
                seqNum(global_seq)
            )
    return result

#ActivityNarrative
def activityNarrative(narrative):
    result = ANI(ANISEQNUM("1"), ANITEXT(narrative), seqNum(global_seq))
    return result

# Adds Activity to a SAR Batch
def newActivity(name, id, date, amount, narrative):
    global total_amount
    global activity_count
    total_amount += amount
    activity_count += 1
    result =  ACTIVITY(seqNum(global_seq),
                    FILEDATE(currentDate()),
                    AA(seqNum(global_seq)),
                    #Transmitter
                    transmitter(),
                    #Transmitter Contact
                    transmitterContact(),
                    #Filing Institution
                    filingInstituion(),
                    #Filing Institution Contact Office (Designated Contact Office)
                    contactOffice,
                    #-------------- Non Consistent Information gets Added ------------# 
                    activityOccured(),
                    subject(name),
                    suspiciousActivity(date,amount),
                    activityNarrative(narrative)
                )
    return result

# Creates Batch XML 
def createBatch(): 
    iname = input("Enter Input File: ")
    data = loadActivities(iname)
    activities = []
    for activity in data:
        activities.append(newActivity(activity["SubjectName"], activity["PartyIdentification"], activity["Date"], activity["Amount"], activity["Narrative"]))

    activities = tuple(activities)
    result = BATCH(
        batchAttributes(total_amount, 1, 1, 2, 2),
        FORMTYPECODE("SARX"),
        *activities
    )
    return result


def output(sar):
    fname = input("Enter the Filename to write to: ")
    # Writes Generated XML Object to an XML File
    with open('./generatedSARs/' + fname + '.xml', 'wb+') as f:
        print("Writing to XML File ...")
        f.write(etree.tostring(sar, pretty_print=True,
                            xml_declaration=True, encoding='UTF-8'))
        print("Wrote EFileBatchSAR to %s" % (fname + '.xml'))


bsasar = createBatch()
output(bsasar)
