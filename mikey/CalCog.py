from discord.ext import commands
from GoogleCalendar import Calendar, load_calendars

class Cal(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        load_calendars()
        self.calendars = {}

    def get_calendar(self, guild_id):
        """Retrieves the calendar for the guild, or generates a new one"""
        try:
            calendar = self.calendars[guild_id]
        except KeyError:
            calendar = Calendar(guild_id)
            self.calendars[guild_id] = calendar
        
        return calendar

    @commands.Cog.listener()
    async def on_scheduled_event_create(self, event):
        print("create 1")
        calendar = self.get_calendar(event.guild.id)
        print("create 2")
        calendar.publish_event(event)
        print("create 3")
        

    @commands.Cog.listener()
    async def on_scheduled_event_update(self, before, after):
        calendar = self.get_calendar(before.guild.id)
        calendar.modify_event(before, after)

    @commands.Cog.listener()
    async def on_scheduled_event_delete(self, event):
        calendar = self.get_calendar(event.guild.id)
        calendar.delete_event(event)

    @commands.command(name="calender_register", aliases=["cal_reg", "cr"])
    async def cal_(self, ctx, *, url: str):
        print("1")
        calendar = self.get_calendar(ctx.guild.id)
        print(f"2 {url}")
        calendar.register_calendar(url)
        print("3")
        print(calendar.get_calendars())
        