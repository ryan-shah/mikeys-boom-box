from constants import calendarFile
from exceptions import AuthenticationException
from datetime import datetime, timedelta
import base64
import csv
import os.path
import inspect
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

"""
{
    guildId: [{
        id: calendarId,
        name: name
    }]
}
"""
CALENDARS = {}


def load_calendars():
    if not os.path.exists(calendarFile):
        return
    with open(calendarFile, "r+") as f:
        reader = csv.reader(f)
        for row in reader:
            guild = row[0]
            calendar = row[1]
            name = row[2]
            c = {"id": calendar, "name": name}
            if guild in CALENDARS.keys():
                CALENDARS[guild].append(c)
            else:
                CALENDARS[guild] = [c]


def save_calendars():
    with open(calendarFile, "w+") as f:
        writer = csv.writer(f)
        for key in CALENDARS.keys():
            for calendar in CALENDARS[key]:
                writer.writerow([key, calendar["id"], calendar["name"]])


class GCalendar:
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

    def get_calendar_details(self, url):
        service = build("calendar", "v3", credentials=self.creds)
        try:
            c = service.calendars().get(calendarId=url).execute()
            return c
        except HttpError as error:
            print("An error occurred: %s" % error)

    def register_calendar(self, url):
        calendar = {"id": url, "name": self.get_calendar_details(url)["summary"]}
        self.calendars.append(calendar)
        CALENDARS[self._guild] = self.calendars

        save_calendars()
        self.fetch_calendars()

    def remove_calendar(self, name):
        cal = None
        for i in range(len(self.calendars)):
            calendar = self.calendars[i]
            if calendar["name"] == name:
                cal = self.calendars.pop(i)
                break

        save_calendars()
        self.fetch_calendars
        return cal

    def get_calendars(self):
        return self.calendars

    def get_new_creds(self):
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        try:
            return flow.run_local_server(port=0, open_browser=False, timeout_seconds=30)
        except Exception as e:
            raise AuthenticationException("Google", e, inspect.stack()[0][3])

    def get_creds(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = self.get_new_creds()
            else:
                creds = self.get_new_creds()
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    def parse_event(self, event):
        x = {
            "summary": event.name,
            "location": f"{event.guild.name}: {event.location or event.channel}",
            "description": f"{event.description}\n\neventId: {event.id}",
            "start": {
                "dateTime": event.start_time.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": (event.start_time + timedelta(hours=3)).isoformat(),
                "timeZone": "UTC",
            },
            "reminders": {
                "useDefault": True,
            },
        }
        return x

    def publish_event(self, event):
        data = self.parse_event(event)
        service = build("calendar", "v3", credentials=self.creds)
        for calendar in self.calendars:
            try:
                event = (
                    service.events()
                    .insert(calendarId=calendar["id"], body=data)
                    .execute()
                )
                print(f"Event Created: {event.get('htmlLink')}")
            except HttpError as error:
                print("An error occurred: %s" % error)

    def get_matching_event(self, calendar, event_id):
        service = build("calendar", "v3", credentials=self.creds)
        try:
            events = (
                service.events()
                .list(
                    calendarId=calendar,
                    timeMin=datetime.utcnow().isoformat() + "Z",
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events.get("items", [])
            for event in events:
                if str(event_id) in event["description"]:
                    return str(event["id"])
        except HttpError as error:
            print("An error occurred: %s" % error)
        return None

    def modify_event(self, old, new):
        event_id = old.id
        for calendar in self.calendars:
            gCalId = self.get_matching_event(calendar["id"], event_id)
            if gCalId is not None:
                service = build("calendar", "v3", credentials=self.creds)
                try:
                    event = (
                        service.events()
                        .patch(
                            calendarId=calendar["id"],
                            eventId=gCalId,
                            body=self.parse_event(new),
                        )
                        .execute()
                    )
                    print(f"Event Updated: {event.get('htmlLink')}")
                except HttpError as error:
                    print("An error occurred: %s" % error)

    def delete_event(self, event):
        event_id = event.id
        for calendar in self.calendars:
            gCalId = self.get_matching_event(calendar["id"], event_id)
            if gCalId is not None:
                service = build("calendar", "v3", credentials=self.creds)
                try:
                    service.events().delete(
                        calendarId=calendar["id"], eventId=gCalId
                    ).execute()
                    print("Event Deleted.")
                except HttpError as error:
                    print("An error occurred: %s" % error)

    def list_calendars(self):
        results = []
        for c in self.calendars:
            details = {"name": c["name"], "url": self.get_shareable_url(c["id"])}
            results.append(details)
        return results

    def create_calendar(self, name):
        service = build("calendar", "v3", credentials=self.creds)
        cal = None
        try:
            cal = (
                service.calendars()
                .insert(body={"summary": name, "timeZone": "America/New_York"})
                .execute()
            )
            print("Calendar Created.")
        except HttpError as error:
            print("An error occurred: %s" % error)

        if cal:
            print(cal)
            self.register_calendar(cal["id"])

    def get_shareable_url(self, url):
        cid = base64.b64encode(url.encode("utf-8")).decode().rstrip("=")
        return f"https://calendar.google.com/calendar?cid={cid}"
