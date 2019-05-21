import xml.etree.ElementTree as ET
#from lxml.builder import ElementMaker  # lxml only !
import lxml.builder as builder
from lxml import etree
from datetime import datetime
import xmltodict, json


global_seq = 0


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


# Defines All namespaces and default namespace
E = builder.ElementMaker(namespace="www.fincen.gov/base",
                 nsmap={'fc2': "www.fincen.gov/base", 'xsi': "http://www.w3.org/2001/XMLSchema-instance", 'xsd': "http://www.w3.org/2001/XMLSchema",
                        'vc': "http://www.w3.org/2007/XMLSchema-versioning"})


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
ANI = E.ActivityNarrativeInformation
ANISEQNUM = E.ActivityNarrativeSequenceNumber
ANITEXT = E.ActivityNarrativeText

# Adds Activity to a SAR Batch


def addActivity():
    return ACTIVITY(seqNum(global_seq),
                    FILEDATE(currentDate()),
                    AA(seqNum(global_seq)),
                    PARTY(APTC("35"), seqNum(global_seq)),
                    PARTY(APTC("37"), seqNum(global_seq)),
                    PARTY(APTC("33"), seqNum(global_seq)),
                    PARTY(APTC("34"), seqNum(global_seq)),
                    PARTY(APTC("30"), seqNum(global_seq)),
                    PARTY(APTC("8"), seqNum(global_seq)),
                    SA(SADATE(currentDate()),
                       SACLASS(
                        SASUBTYPE("106"), SATYPE("1"),
                        seqNum(global_seq)),
                       seqNum(global_seq)
                       ),
                    ANI(ANISEQNUM("1"), ANITEXT("Bud Sale"), seqNum(global_seq))
                    )


# Creates the XML Batch File
sarBatch = BATCH(
    batchAttributes(1000, 1, 1, 2, 2),
    FORMTYPECODE("SARX"),
    addActivity(),
    addActivity()
)


# batchAttributes(sarBatch)

fname = input("Enter the Filename to write to:")
# Writes Generated XML Object to an XML File
with open('./generatedSARs/' + fname + '.xml', 'wb+') as f:
    print("Writing to XML File ...")
    f.write(etree.tostring(sarBatch, pretty_print=True,
                           xml_declaration=True, encoding='UTF-8'))
    print("Wrote EFileBatchSAR to %s" % (fname + '.xml'))
