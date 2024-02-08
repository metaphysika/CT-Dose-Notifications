import os
import sys
import django
import pandas
import datetime
import openpyxl
import py
from emailsender import *
import atexit
from time import time, strftime, localtime
from datetime import timedelta


# This will help display run time for script
def secondsToStr(elapsed=None):
    if elapsed is None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))

def log(s, elapsed=None):
    line = "="*40
    print(line)
    print(secondsToStr(), '-', s)
    if elapsed:
        print("Elapsed time:", elapsed)
    print(line)
    print()

def endlog():
    end = time()
    elapsed = end-start
    log("End Program", secondsToStr(elapsed))

# calls run time functions for script
start = time()
atexit.register(endlog)
log("Start Program")


# set to True to send emails.  False to not send emails.
is_email = True

#setup django/OpenREM
projectpath = os.path.abspath(r'C:\Users\clahn\AppData\Local\Continuum\anaconda3\envs\openrem090\Lib\site-packages\openrem')
if projectpath not in sys.path:
    sys.path.insert(1, projectpath)
os.environ["DJANGO_SETTINGS_MODULE"] = 'openremproject.settings'
django.setup()


# from remapp.tools.hash_id import hash_id
# from openrem.remapp.extractors.rdsr import rdsr
# from itertools import chain
# from remapp.models import UniqueEquipmentNames
from remapp.models import CtIrradiationEventData
# from remapp.models import CtRadiationDose
# GeneralStudyModuleAttr # has study_date and accession_number


enddate = datetime.datetime.now() - datetime.timedelta(days=90)
# https://stackoverflow.com/questions/2425603/how-do-i-select-from-multiple-tables-in-one-query-with-django

# Create query to get data from models.  The double __ will allow you to access data by foreign key on different models.
data = CtIrradiationEventData.objects.values('acquisition_protocol', 'mean_ctdivol', 'irradiation_event_uid',
                                                'ct_radiation_dose__start_of_xray_irradiation', 
                                                'ctdosecheckdetails__ctdivol_notification_value',
                                                'ct_radiation_dose__general_study_module_attributes__accession_number',
                                                'ct_radiation_dose__general_study_module_attributes__generalequipmentmoduleattr__institution_name',
                                                'ct_radiation_dose__general_study_module_attributes__generalequipmentmoduleattr__station_name').filter( 
                                                    ct_radiation_dose__start_of_xray_irradiation__gt=enddate
                                                    )


# Generate a data series 
df = pandas.DataFrame(data)

# rename columns
df.rename(columns = {'acquisition_protocol': 'protocol', 'mean_ctdivol': 'ctdi', 'irradiation_event_uid': 'uid', 
                    'ct_radiation_dose__start_of_xray_irradiation': 'studydate', 
                    'ctdosecheckdetails__ctdivol_notification_value': 'scanalert',
                    'ct_radiation_dose__general_study_module_attributes__accession_number': 'acc',
                    'ct_radiation_dose__general_study_module_attributes__generalequipmentmoduleattr__institution_name': 'site',
                    'ct_radiation_dose__general_study_module_attributes__generalequipmentmoduleattr__station_name': 'stationname'}, inplace=True)


df = df.drop_duplicates()
# Drop nan values in protocol column
df= df.dropna(subset=['protocol'])



def dose_limit(exam, limit):
    # could filter dataframe to exclude 'CTA'.  Do we want to do this for all CTA exams?  Or, just CTA head?
    # Then, create a separate function to deal with CTA exams?
    # Copy of original dataframe to apply current exam filter to checking for alerts.
    df2 = df  # [~df['protocol'].str.contains('CTA', case=False)]
    # create mask of just the protocols we are passing into funciton. ex. 'head'
    for s in exam:
        df2 = df2[df2['protocol'].str.lower().str.contains(s, case=False)]
    # print (df2.head(10))
    # iterate through filtered dataframe and check if ctdi is over limit for that exam type.
    for idx, row in df2.iterrows():         
            if row.at['ctdi'] > limit:
                # list for adding data to spreadsheet for tracking notifications.
                nt = []
                # TODO: change to physics@sanfordhealth.org
                emailname = "christopher.lahn@sanfordhealth.org" #; physics@sanfordhealth.org
                protocol = str(row.at["protocol"])
                nt.append(protocol)
                uid = str(row.at['uid'])
                nt.append(uid)
                ctdi = str(row.at['ctdi'])
                nt.append(ctdi)
                alert_limit = str(limit)
                nt.append(alert_limit)
                scanalert = str(row.at['scanalert'])
                nt.append(scanalert)
                # calls function that matches up uid with accession # in database.
                acc = str(row.at['acc'])
                nt.append(acc)
                # calls function that matches up uid with beginning of radiation event (study date) in database.
                studydate = str(row.at['studydate'])
                nt.append(studydate)
                # calls function that matches up uid with Site name in database.
                site = str(row.at['site'])
                nt.append(site)
                # calls function that matches up uid with station name in database.
                stationname = str(row.at['stationname'])
                nt.append(stationname)

                # write the notifications to a file.
                # TODO move file to a permanent place
                wb = openpyxl.load_workbook(r'W:\SHARE8 Physics\Software\python\scripts\clahn\Dose Notification OpenRem\sql dose limit notifications.xlsx')
                sheet = wb['Sheet1']
                # check if UID is already in file.  If so, pass.  If not, append and send notification.
                oldUid = []
                for col in sheet['B']:
                    oldUid.append(col.value)
                if uid in oldUid:
                    pass
                else:
                    sheet.append(nt)
                    wb.save(r'W:\SHARE8 Physics\Software\python\scripts\clahn\Dose Notification OpenRem\sql dose limit notifications.xlsx')
                    wb.close()
                    # calls the module that sends the email with these variables data.
                    # if is_email is true, the email will get sent.  If false, it will not send email.
                    if is_email:
                        EmailSender().send_email(emailname, "CT Dose Notification Trigger",
                                                "Hello, \r\n \r\nThis is an automated message.  No reply is necessary."
                                                "  \r\n \r\nAn exam was performed that exceeded our dose Notification limits.  \r\n \r\nExam: "
                                                + protocol + "\r\n \r\nAccession #: " + acc + "\r\n \r\nCTDI: " + ctdi +
                                                "\r\n \r\nAlert Limit: " + alert_limit + "\r\n \r\nStudy Date: " +
                                                studydate + "\r\n \r\nSite: " + site + "\r\n \r\nStation name: " + stationname)
                    else:
                        pass
                    continue
    # wb.close()


dose_limit(['head'], 80)
dose_limit(['brain'], 80)
dose_limit(['abd'], 50)
dose_limit(['stone'], 50)
dose_limit(['peds', 'abd'], 25)
dose_limit(['ped', 'head', '0-'], 50)
dose_limit(['ped', 'head'], 60)
