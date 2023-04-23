from discord.ext import commands

from .bot import AimBot
from .context import Context
from .utils import humanize_time, LogAction, LogActions, Lowercase, s

__all__ = (
    "AimBot",
    "Cog",
    "Context",
    "humanize_time",
    "LogAction",
    "LogActions",
    "Lowercase",
    "s",
)


class Cog(commands.Cog):
    """Base class for all cogs"""

    def __init__(self, bot: AimBot) -> None:
        self.bot = bot
