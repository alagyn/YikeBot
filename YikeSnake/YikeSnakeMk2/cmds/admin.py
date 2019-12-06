# admin.py

from discord.ext import commands
import discord
from sys import exit


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(name='logout', hidden=True, aliases=['lo'])
    @commands.is_owner()
    async def logoutCmd(self, ctx):
        await self.bot.writeYikeLog()
        self.bot.addAdminLog('YikeLog Updated, Logging out')
        await ctx.message.delete()
        await self.bot.change_presence(status=discord.Status.offline)
        await discord.Client.close(self.bot)
        exit(0)

    @commands.command(name='reset', hidden=True)
    @commands.is_owner()
    async def reset(self, ctx: commands.Context):
        await ctx.message.delete()
        try:
            ext = []
            for x in self.bot.extensions:
                ext.append(x)
            for x in ext:
                if x != 'cmds.admin':
                    self.bot.reload_extension(x)

        except (commands.ExtensionNotFound, commands.ExtensionNotLoaded,
                commands.NoEntryPointError, commands.ExtensionFailed) as e:
            await ctx.send(f"Error resetting: {e.message}")
        await ctx.send("Done", delete_after=5)


def setup(bot):
    bot.add_cog(Admin(bot))
