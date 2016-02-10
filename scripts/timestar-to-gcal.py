#!/usr/bin/python
#
# Script used to one-way sync Sage Time and Attendance (Insperity TimeStar) time-off events to Google Calendar
# Requirements:
#   - Python 2.7 (2.7.9 Release Date: 2014-12-10 32-bit, https://www.python.org/ftp/python/2.7.9/python-2.7.9.msi)
#   - Python ODBC library (pyodbc 3.0.7 32-bit, https://pyodbc.googlecode.com/files/pyodbc-3.0.7.win32-py2.7.exe)
#   - update pip: C:\Python27\Scripts\easy_install.exe -U pip
#   - Google APIs Client Library for Python, https://github.com/google/google-api-python-client (C:\Python27\Scripts\pip2.7.exe install --upgrade google-api-python-client)
#   - Create Google Project and populate the client_secrets.json file with your Google Project API Credentials (https://console.developers.google.com/project)
#   - SQL User with db_datareader role membership to TimeStar Database

import pyodbc
import time
import sys

from oauth2client import client
from googleapiclient import sample_tools

VACATION_CALENDAR = 'YOUR-CAL@group.calendar.google.com'
SQLSERVERIP='YOURSQLIP'
SQLDSN='YOURtimestar'
SQLDATABASE='YOURTimeStarDB'
SQLUID='YOURTimeStarToGoogleUSER'
SQLPWD='YOURsupersecretpasssword'

def get_google_usernames_for_day(service,time_max,time_min):
    names = [];
    ids = [];
    try:
        page_token = None
        while True:
            events = service.events().list(calendarId=VACATION_CALENDAR, pageToken=page_token,timeMax=time_max,timeMin=time_min).execute()
            for event in events['items']:
                names.append(event['summary'])
                ids.append(event['id'])
            page_token = events.get('nextPageToken')
            if not page_token:
                break

    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run the application to re-authorize.')
 
    return names, ids

def add_events(service,names,the_date):
    for name in names:
        try:
            event = {
                'summary': name,
                'start': {
                    'date': the_date
                },
                'end': {
                    'date': the_date
                }
            }

            created_event = service.events().insert(calendarId=VACATION_CALENDAR, body=event).execute()

        except client.AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run the application to re-authorize.')

def remove_google_event(service,gid):
    try:
        service.events().delete(calendarId=VACATION_CALENDAR, eventId=gid).execute()

    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run the application to re-authorize.')

if __name__ == '__main__':

    # Make database connection
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=SQLSERVERIP;DSN=SQLDSN;DATABASE=SQLDATABASE;UID=SQLUID;PWD=SQLPWD')
    cursor = cnxn.cursor()
    
    # Authenticate and construct service.
    google_cal_service, flags = sample_tools.init(
        sys.argv, 'calendar', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/calendar')

    # Get Timestamp
    ticks = time.time()

    # Calculate approximately 4 months out.  
    fourmonths = ticks + 60 * 60 * 24 * 30 * 4
  
    # Get all time-off events for next 4 months from today out of TimeStar
    while ticks <= fourmonths:
  
        # Convert ticks to SQL Date, 2014-12-31 00:00:00
        sql_time = time.strftime('%Y-%m-%d 00:00:00', time.localtime(ticks))

        # Convert ticks to Google Event Date
        google_timeMax = time.strftime('%Y-%m-%dT11:59:59+00:00', time.localtime(ticks))
        google_timeMin = time.strftime('%Y-%m-%dT00:00:00+00:00', time.localtime(ticks))

        # Convert ticks to Google Event short Date, 2014-12-31
        google_date = time.strftime('%Y-%m-%d', time.localtime(ticks))

        sage_names = []

        # Get names from Sage for this day
        cursor.execute("select first_name, last_name from employee where employee_id in (select employee_id from time_other_hours where actual_date = '" + sql_time +"')")
        while 1:
            row = cursor.fetchone()
            if not row:
                break
            sage_names.append(row.first_name.rstrip() + ' ' + row.last_name.rstrip())

        # Get names and ID from Google for this day 
        google_names, google_ids = get_google_usernames_for_day(google_cal_service,google_timeMax,google_timeMin)

        for name in google_names:
            if name in sage_names:
                sage_names.remove(name)
            else:
                # Remove event from Google, no longer in Sage
                i = google_names.index(name)
                remove_google_event(google_cal_service,google_ids[i])

        # Add Sage names
        if len(sage_names) > 0:
            add_events(google_cal_service,sage_names,google_date)

        # Increase ticks by one day
        ticks = ticks + 60 * 60 * 24
