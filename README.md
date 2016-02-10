# timestar-to-gcal
Unidirectional sync from Sage Time and Attendance (Insperity TimeStar) time-off events to Google Calendar
http://www.insperity.com/products/time-and-attendance<br>
http://www.sage.com/us/sage-hrms/time-and-attendance-management

\# Requirements:
   - Python 2.7 (2.7.9 Release Date: 2014-12-10 32-bit, https://www.python.org/ftp/python/2.7.9/python-2.7.9.msi)
   - Python ODBC library (pyodbc 3.0.7 32-bit, https://pyodbc.googlecode.com/files/pyodbc-3.0.7.win32-py2.7.exe)
   - update pip: C:\Python27\Scripts\easy_install.exe -U pip
   - Google APIs Client Library for Python, https://github.com/google/google-api-python-client (C:\Python27\Scripts\pip2.7.exe install --upgrade google-api-python-client)
   - Create Google Project and populate the client_secrets.json file with your Google Project API Credentials (https://console.developers.google.com/project)
   - SQL User with db_datareader role membership to TimeStar Database

\# Be sure to change the following values in the following files

\# client_secrets.json<br>
"client_id": "YOUR-CLIENT-ID.apps.googleusercontent.com"<br>
"client_secret": "YOUR-CLIENT-SECRET"<br>
"client_email": "YOUR-CLIENT-EMAIL@developer.gserviceaccount.com"<br>

\# timestar-to-gcal.py<br>
VACATION_CALENDAR = 'YOUR-CAL@group.calendar.google.com'<br>
SQLSERVERIP='YOURSQLIP'<br>
SQLDSN='YOURtimestar'<br>
SQLDATABASE='YOURTimeStarDB'<br>
SQLUID='YOURTimeStarToGoogleUSER'<br>
SQLPWD='YOURsupersecretpasssword'<br>
