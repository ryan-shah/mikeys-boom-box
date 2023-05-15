from discord.ext import commands
from GoogleCalendar import GCalendar, load_calendars
from exceptions import AuthenticationException


class Calendar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_calendars()
        self.calendars = {}

    async def get_calendar(self, guild_id, ctx=None):
        """Retrieves the calendar for the guild, or generates a new one"""
        try:
            calendar = self.calendars[guild_id]
        except KeyError:
            try:
                calendar = GCalendar(guild_id)
                self.calendars[guild_id] = calendar
            except AuthenticationException as e:
                if ctx:
                    await ctx.send(str(e))
                return

        return calendar

    @commands.Cog.listener()
    async def on_scheduled_event_create(self, event):
        calendar = await self.get_calendar(event.guild.id)
        calendar.publish_event(event)

    @commands.Cog.listener()
    async def on_scheduled_event_update(self, before, after):
        calendar = await self.get_calendar(before.guild.id)
        calendar.modify_event(before, after)

    @commands.Cog.listener()
    async def on_scheduled_event_delete(self, event):
        calendar = await self.get_calendar(event.guild.id)
        calendar.delete_event(event)

    @commands.command(name="register", aliases=["reg", "r"])
    async def cal_(self, ctx, *, url):
        """Register a new calendar.
        Parameters
        ------------
        calendarId: string [Required]
            The ID of the calendar you wish to use.
        """
        calendar = await self.get_calendar(ctx.guild.id, ctx)
        calendar.register_calendar(url)
        print(calendar.get_calendars())

    @commands.command(name="list", aliases=["ls", "l"])
    async def list_(self, ctx):
        """List Registered Calendars
        Parameters
        ------------
        none
        """
        calendar = await self.get_calendar(ctx.guild.id, ctx)
        msg = "**Synced Calnedars**\n"
        for c in calendar.list_calendars():
            msg += f"{c['name']}: <{c['url']}>\n"
        await ctx.send(msg)

    @commands.command(name="create", aliases=["c"])
    async def create_(self, ctx):
        """Creates a new calendar for the server
        Parameters
        ------------
        none
        """
        calendar = await self.get_calendar(ctx.guild.id, ctx)
        calendar.create_calendar(ctx.guild.name)
        await ctx.send("Calendar Created")
        await ctx.invoke(self.list_)

    @commands.command(name="remove", aliases=["rm"])
    async def remove_(self, ctx, *, name):
        """Removes a calendar for the server
        Parameters
        ------------
        none
        """
        calendar = await self.get_calendar(ctx.guild.id, ctx)
        c = calendar.remove_calendar(name)
        if c:
            await ctx.send(f"Calendar Removed: {c['name']}")
        else:
            await ctx.send("Unable to find calendar in server")
        await ctx.invoke(self.list_)
