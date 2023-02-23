from constants import calendarFile
from datetime import datetime, timedelta
import csv
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

CALENDARS = {}
def load_calendars():
    with open(calendarFile, "r+") as f:
        reader = csv.reader(f)
        for row in reader:
            guild = row[0]
            calendar = row[1]
            if guild in CALENDARS.keys():
                CALENDARS[guild].append(calendar)
            else:
                CALENDARS[guild] = [calendar]

def save_calendars():
    with open(calendarFile, "w+") as f:
        writer = csv.writer(f)
        for key in CALENDARS.keys():
            for calendar in CALENDARS[key]:
                writer.writerow([key, calendar])

class Calendar():
    """
    A class representing the calendar for each guild.
    """

    def __init__(self, guild_id):
        self._guild = str(guild_id)
        self.fetch_calendars()
        self.creds = self.get_creds()
        
    def fetch_calendars(self):
        if self._guild in CALENDARS.keys():
            self.calendars = CALENDARS[self._guild]
        else:
            self.calendars = []

    def register_calendar(self, calendar):
        self.calendars.append(calendar)
        if self._guild in CALENDARS.keys():
            CALENDARS[self._guild] = list(set(CALENDARS[self._guild] + self.calendars))
        else:
            CALENDARS[self._guild] = [calendar]

        save_calendars()
        self.fetch_calendars()

    def get_calendars(self):
        return self.calendars

    def get_creds(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds
        
    def parse_event(self, event):
        x = {
            'summary': event.name,
            'location': f"{event.guild.name}: {event.location or event.channel}",
            'description': f"{event.description}\n\neventId: {event.id}",
            'start': {
                'dateTime': event.start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (event.start_time + timedelta(hours=3)).isoformat(),
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': True,
            },
        }
        return x
    
    def publish_event(self, event): 
            data = self.parse_event(event)
            service = build('calendar', 'v3', credentials=self.creds)
            for calendar in self.calendars:
                try:
                    event = service.events().insert(calendarId=calendar, body=data).execute()
                    print(f"Event Created: {event.get('htmlLink')}")
                except HttpError as error:
                    print('An error occurred: %s' % error)

    def get_matching_event(self, calendar, event_id):
        service = build('calendar', 'v3', credentials=self.creds)
        try:
            events = service.events().list(
                calendarId=calendar,
                timeMin=datetime.utcnow().isoformat() + 'Z',
                maxResults=10,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            events = events.get('items', [])
            for event in events:
                if str(event_id) in event['description']:
                    return str(event['id'])
        except HttpError as error:
            print('An error occurred: %s' % error)
        return None

    def modify_event(self, old, new):
        event_id = old.id
        for calendar in self.calendars:
            gCalId = self.get_matching_event(calendar, event_id)
            if gCalId is not None:
                service = build('calendar', 'v3', credentials=self.creds)
                try:
                    event = service.events().patch(
                        calendarId=calendar,
                        eventId=gCalId,
                        body=self.parse_event(new)
                    ).execute()
                    print(f"Event Updated: {event.get('htmlLink')}")
                except HttpError as error:
                    print('An error occurred: %s' % error)

    def delete_event(self, event):
        event_id = event.id
        for calendar in self.calendars:
            gCalId = self.get_matching_event(calendar, event_id)
            if gCalId is not None:
                service = build('calendar', 'v3', credentials=self.creds)
                try:
                    service.events().delete(
                        calendarId=calendar,
                        eventId=gCalId
                    ).execute()
                    print(f"Event Deleted.")
                except HttpError as error:
                    print('An error occurred: %s' % error)