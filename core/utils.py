import discord

__all__ = (
    "add_members",
    "add_to_thread_directory",
    "get_permissions",
    "get_tag",
    "get_tutorial_embed",
    "get_valid_thread",
    "is_valid_thread",
    "remove_from_thread_directory",
)


# functions
async def add_feedback_thread_to_feedback_thread_directory(thread: discord.Thread, thread_dir_msg: discord.Message,
                                                           thread_ids: list[int]) -> bool:
    """Adds the feedback thread to the feedback thread directory.

    Parameters
    ------------
    thread: discord.Thread
        The feedback thread to add to the feedback thread directory.
    thread_dir_msg: discord.Message
        The message containing the feedback thread directory.
    thread_ids: list[int]
        The list of thread ids in the feedback thread directory.

    Returns
    -----------
    bool
        Whether the feedback thread was added to the feedback thread directory successfully."""
    if thread.id in thread_ids:
        thread_ids.remove(thread.id)
    thread_ids.append(thread.id)
    thread_directory_embed: discord.Embed = await get_feedback_thread_directory_embed(thread_ids, thread.guild)
    await thread_dir_msg.edit(embed=thread_directory_embed, content=None)
    return True


async def add_members(thread: discord.Thread) -> None:
    """Adds members to the thread specified.

    Parameters
    ------------
    thread: discord.Thread
        The thread to add members to."""
    await thread.join()
    await thread.edit(auto_archive_duration=10080)

    ping_role = get_ping_role(thread.guild)

    member_mentions = [member.mention for member in thread.guild.members if ping_role in member.roles]

    if not member_mentions:
        return
    ping_msg: discord.Message = await thread.send(embed=discord.Embed(
        title="Adding Members",
        description="Adding members to the thread...",
        color=discord.Color.blurple(),
        timestamp=discord.utils.utcnow()
    ))
    msg_content = ""
    counter = 0
    for member_mention in member_mentions:
        if len(msg_content + member_mention) > 2000 or counter == 10:
            await ping_msg.edit(content=msg_content)
            msg_content = f"{member_mention} "
            counter = 1
        else:
            msg_content += f"{member_mention} "
            counter += 1
    if len(msg_content) != 0:
        await ping_msg.edit(content=msg_content)
    embed_description = "Successfully added people to the thread and set auto-archive duration to the max!"
    message = ""
    if thread.guild.id == 933075515881951292:
        embed_description += "\n\nPlease use the template above for your feedback. Simply right-click on this" \
                             "message and then click Copy Text to copy the template to your clipboard."
        message = """## <:Overworld:1132644632489103371>  Overworld
-
## <:Nether:1132644630576517190>  Going to Bastion
-
## <:Bastion:1138327109929025536>  Bastion Split
-
## <:Nether:1132644630576517190>  Going to Fortress
-
## <:Fortress:1138327332688511027>  Fortress Split
-
## <:Triangulation:1138327300736290906>  Finding/Going to Stronghold
-
## <:Stronghold:1138327270625378324>  Stronghold Split
-
## <:End:1132644627506278451>  End Split
-"""
    await ping_msg.edit(embed=discord.Embed(
        title="Members Added",
        description=embed_description,
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    ), content=message)


async def add_to_thread_directory(thread: discord.Thread) -> bool:
    """Adds the thread to the thread directory.

    Parameters
    ------------
    thread: discord.Thread
        The thread to add to the thread directory.

    Returns
    -----------
    bool
        Whether the thread was added to the thread directory successfully."""
    thread_dir_msg: discord.Message | None = await get_thread_dir_msg(thread.guild)
    if thread_dir_msg is None:
        return False
    initial_embed: discord.Embed = thread_dir_msg.embeds[0]
    thread_ids: list[int] = [int(line[4:-1]) for field in initial_embed.fields for line in field.value.splitlines()]
    if thread.guild.id == 933075515881951292:
        return await add_feedback_thread_to_feedback_thread_directory(thread, thread_dir_msg, thread_ids)
    if thread.id in thread_ids:
        return True
    thread_ids.append(thread.id)
    parent_ids: list[int] = await get_parent_ids(thread_ids, thread)
    thread_directory_embed: discord.Embed = await get_thread_directory_embed(parent_ids, thread_ids, thread.guild)
    await thread_dir_msg.edit(embed=thread_directory_embed, content=None)
    return True


async def get_feedback_thread_directory_embed(thread_ids: list[int], guild: discord.Guild) -> discord.Embed:
    """Gets the feedback thread directory embed.

    Parameters
    ------------
    thread_ids: list[int]
        The thread ids to get the message parts for.
    guild: discord.Guild
        The guild to get the thread directory embed for.

    Returns
    -----------
    discord.Embed
        The feedback thread directory embed."""
    thread_directory_embed = discord.Embed(
        title="Feedback Thread Directory",
        description="A list of all feedback threads of this server, sorted by the time they have been waiting for "
                    "feedback. The threads at the top have been waiting the longest.",
        color=guild.me.color,
        timestamp=discord.utils.utcnow()
    )
    field_value = "\n".join(
        [f"- <#{thread_id}>" for thread_id in thread_ids]
    )
    thread_directory_embed.add_field(
        name=f"Feedback Threads",
        value=field_value,
        inline=False
    )
    return thread_directory_embed


async def get_thread_directory_embed(parent_ids: list[int], thread_ids: list[int],
                                     guild: discord.Guild) -> discord.Embed:
    """Gets the thread directory embed.

    Parameters
    ------------
    parent_ids: list[int]
        The parent ids for the thread ids specified.
    thread_ids: list[int]
        The thread ids to get the message parts for.
    guild: discord.Guild
        The guild to get the thread directory embed for.

    Returns
    -----------
    discord.Embed
        The thread directory embed."""
    thread_directory_embed = discord.Embed(
        title="Thread Directory",
        description="A list of all threads of this server, sorted by the parent channels of the threads.",
        color=guild.me.color,
        timestamp=discord.utils.utcnow()
    )
    for parent_id in parent_ids:
        field_value = "\n".join(
            [f"- <#{thread_id}>" for thread_id in thread_ids
             if (await guild.fetch_channel(thread_id)).parent.id == parent_id]
        )
        thread_directory_embed.add_field(
            name=f"<#{parent_id}>",
            value=field_value,
            inline=False
        )
    return thread_directory_embed


def get_tutorial_embed(ctx: discord.ApplicationContext) -> discord.Embed:
    """Returns the tutorial embed.

    Parameters
    ------------
    ctx: discord.ApplicationContext
        The context used for command invocation.

    Returns
    -----------
    discord.Embed
        The tutorial embed."""
    tutorial_embed = discord.Embed(
        title="Title",
        description="Description",
        color=ctx.guild.me.color,
        timestamp=discord.utils.utcnow()
    )
    tutorial_embed.add_field(name="Inline Field 1", value="← Color sets color of the bar on the left!")
    tutorial_embed.add_field(name="Inline Field 2", value="Value 2")
    tutorial_embed.add_field(name="Inline Field 3", value="Inline fields will be next to each other!")
    tutorial_embed.add_field(name="Non-inline Field", value="Value", inline=False)
    tutorial_embed.set_author(name="Author", icon_url=ctx.guild.me.avatar.url)
    tutorial_embed.set_footer(text="Footer", icon_url="https://cdn.discordapp.com/attachments/751512715872436416"
                                                      "/1125701630273261629/13YRA70M.png")
    tutorial_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/751512715872436416"
                                     "/1125132998967304412/t6HnzvR8.png")
    tutorial_embed.set_image(url="https://cdn.discordapp.com/attachments/751512715872436416/1125132939160731799"
                                 "/kJ9NYtR1.png")
    return tutorial_embed


async def get_parent_ids(thread_ids: list[int], thread: discord.Thread) -> list[int]:
    """Gets the parent ids of the thread ids specified.

    Parameters
    ------------
    thread_ids: list[int]
        The thread ids to get the parent ids of.
    thread: discord.Thread
        The thread to get the parent ids for.

    Returns
    -----------
    list[int]
        The parent ids of the thread ids specified."""
    parent_ids = []
    for thread_id in thread_ids:
        thread = await thread.guild.fetch_channel(thread_id)
        if thread.parent_id not in parent_ids:
            parent_ids.append(thread.parent.id)
    return parent_ids


def get_permissions(user: discord.Member, include: int = 0) -> str:
    """Gets the permissions for the user specified.

    Parameters
    ------------
    user: discord.Member
        The user to get the permissions for.
    include: int
        The permissions to include.

    Returns
    -----------
    str
        The permissions for the user specified."""
    permissions = user.guild_permissions
    if permissions.administrator:
        return "- Administrator"
    return (
            "\n".join(
                f"- {k.replace('_', ' ').title()}"
                for k, v in user.guild_permissions
                if v and (not include or getattr(discord.Permissions(include), k))
            )
            or "_No permissions_"
    )


def get_ping_role(guild: discord.Guild) -> discord.Role | None:
    """Gets the ping role for the guild specified.

    Parameters
    ------------
    guild: discord.Guild
        The guild to get the ping role for.

    Returns
    ------------
    discord.Role
        The ping role for the guild specified."""
    ping_role_ids = {
        933075515881951292: 939633923305132182,  # RIP
        959162264081014814: 939633923305132182,  # SEA
        849650258786779196: None,  # EAR
        915333299981934692: 941942976429559808  # TEST
    }
    ping_role_id = ping_role_ids.get(guild.id)
    if ping_role_id is None:
        return None
    return guild.get_role(ping_role_id)


def get_tag() -> dict[str, str]:
    """Gets a tag for the bot.

    Returns
    ------------
    dict[str, str]"""
    tags: dict[str, str] = {
        "Bastion Route Spreadsheet": "https://docs.google.com/spreadsheets/d/1qLgp5uhMOKuerNZaec1dpoECpJI0"
                                     "-6YhztMqa_wZ8W0/edit?usp=sharing",
        "Blaze Fight": "https://youtu.be/dUMclLehKXE",
        "Bridge": "https://youtu.be/uvvhKX_KnT8",
        "Cobble Skip": "https://youtu.be/HLrsRaij1x8",
        "Dynamic RD": "https://youtu.be/qfwyFWTY3ds",
        "Housing": "https://youtu.be/B2SLviws-3c",
        "Kuee Housing": "https://www.twitch.tv/pncakespoon/clip/CovertShyTruffleHumbleLife-GbXo9QqoNykzFNLI",
        "Language Guide": "https://docs.google.com/document/d/1jSeciLoEgSwWWCdNk0dKignzxJskxJ5_zeCQmcdGmTg/edit?usp"
                          "=sharing",
        "Lauf Crafting": "https://youtu.be/OHleXZuhYng",
        "Lava Placement": "https://cdn.discordapp.com/attachments/751512715872436416/1005946160386687108"
                          "/LavaPlacememt.png",
        "Manhunt Housing": "https://youtu.be/A2tiwLB3DlY",
        "Mapless": "https://youtu.be/ujZJw95h0nk",
        "Ninjabrain Bot": "Bot: https://github.com/Ninjabrain1/Ninjabrain-Bot/releases/\r\n"
                          "Tutorial: https://youtu.be/Rx8i7e5lu7g",
        "Pig Punch": "When you break a chest/gold block, piglins who are on tier 1 **don't** upgrade to tier 2. "
                     "However, when you punch a piglin, piglins **do** upgrade to tier 2, even if they're on tier 1. "
                     "The significance of this is, that piglins on tier 1 lose interest in you as soon as they lose "
                     "LOS, so you want them on tier 2 aggro. Use cases for this are: Manhunt, where you're aggroing "
                     "piglins without armour, bridge manhunt, stables manhunt, treasure bridge, etc. Punching a pig "
                     "is not beneficial in crookst boomer or when you are wearing gold armour.",
        "Preemptive Navigation": "Video: https://youtu.be/2dWq2wXy43M\r\n"
                                 "Document: https://docs.google.com/document/d/1NEJ_BaQOqyDlt"
                                 "-h2GiUg4zXlqBHv8YfMVdGpQhDLD8U/edit?usp=sharing",
        "Rawalle": "https://github.com/joe-ldp/Rawalle/releases/",
        "Reset Tracker": "https://github.com/Specnr/ResetTracker",
        "Right Shoulder Auto Funnel": "https://cdn.discordapp.com/attachments/751512715872436416/1006313251874820257"
                                      "/rightShoulderAutoFunnel.png",
        "Stables": "<:PauseMan:1005005749191184385>",
        "Sub Pixel": "Left wide: -0.01\r\n"
                     "Middle wide: +0.01\r\n"
                     "Right wide: Do nothing\r\n"
                     "https://cdn.discordapp.com/attachments/751512715872436416/1077348478654611486/image.png",
        "Treasure": "https://youtu.be/HGcDSFKHOtw",
        "Vietnamese": "Guide: https://docs.google.com/document/d/1el7XoX9-wv1boIQ8haIO6XYSoAkEQoh0X1Rd8_PcN70/edit\r\n"
                      "Keyboard Doc: https://docs.google.com/document/d/1V2Uk4wDZknr6U9KbYJEc0JRYO7OWmhtmNIK0swTzXxs"
                      "/edit\r\n "
                      "Resource Pack: https://drive.google.com/file/d/1NXiqmJ40-Oi3LcLQgc8LNlgGhr0TrRG4/view",
        "Wall": "Rawalle: https://github.com/joe-ldp/Rawalle/releases/\r\n"
                "Specnr's wall: https://github.com/Specnr/MultiResetWall/releases/",
        "Wood Light": "https://youtu.be/QFNvgd32TYY",
        "Zero Cycle": "Video: https://youtu.be/YTVctKuUWbI\r\n"
                      "Document: https://docs.google.com/document/d/1Umtj4jo69FnHz68cgp9TCrfDS-14Ummhi6ZDEXg4XGY/view"
    }
    return tags


async def get_thread_dir_msg(guild: discord.Guild) -> discord.Message | None:
    """Gets the thread directory message for a guild.

    Parameters
    ----------
    guild: discord.Guild
        The guild to get the thread directory message for.

    Returns
    -------
    discord.Message | None
        The thread directory message for the guild, or None if it doesn't exist."""
    thread_dirs = {
        933075515881951292: [1152697393825976440, 1152718564944511037],  # RIP
        959162264081014814: [959198464900747304, 1126961535605014609],  # SEA
        849650258786779196: [1041033326846296164, 1126961177990287441],  # EAR
        915333299981934692: [922938837049683968, 1121089178122330276]  # TEST
    }
    channel_id, message_id = thread_dirs.get(guild.id)
    if channel_id is None or message_id is None:
        return None
    channel = guild.get_channel(channel_id)
    return await channel.fetch_message(message_id)


async def get_valid_thread(*, ctx: discord.ApplicationContext, thread: discord.Thread) -> discord.Thread | None:
    """Gets a valid thread or None if the thread is invalid.

    Parameters
    ----------
    ctx: discord.ApplicationContext
        The context of the interaction.
    thread: discord.Thread
        The thread to validate.

    Returns
    -------
    discord.Thread | None
        The valid thread, or None if the thread is invalid."""
    if thread is None:
        thread = ctx.channel
    if not isinstance(thread, discord.Thread):
        await ctx.respond(embed=discord.Embed(
            title="Error",
            description="This command can only be used in threads!",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        ), ephemeral=True)
        return None
    return thread


def is_valid_thread(thread: discord.Thread | discord.abc.GuildChannel) -> bool:
    """Checks members should be added to a thread.

    Parameters
    ----------
    thread: discord.Thread | discord.abc.GuildChannel
        The thread to check."""
    if not isinstance(thread, discord.Thread):
        return False
    blocked_parent_ids = [959525754297778216, 1023877748818706452, 850422836585299989, 1057420004380921856]
    if thread.parent_id in blocked_parent_ids:
        return False
    return True


async def remove_feedback_thread_from_feedback_thread_directory(thread: discord.Thread, thread_dir_msg: discord.Message,
                                                                thread_ids: list[int]) -> bool:
    """Removes a feedback thread from the feedback thread directory.

    Parameters
    ----------
    thread: discord.Thread
        The thread to remove.
    thread_dir_msg: discord.Message
        The thread directory message.
    thread_ids: list[int]
        The thread ids.

    Returns
    -------
    bool
        Whether the thread was removed successfully."""
    thread_directory_embed = await get_feedback_thread_directory_embed(thread_ids, thread.guild)
    await thread_dir_msg.edit(embed=thread_directory_embed)
    return True


async def remove_from_thread_directory(thread: discord.Thread) -> bool:
    """Removes a thread from the thread directory.

    Parameters
    ----------
    thread: discord.Thread
        The thread to remove.

    Returns
    -------
    bool
        Whether the thread was removed successfully."""
    thread_dir_msg: discord.Message | None = await get_thread_dir_msg(thread.guild)
    if thread_dir_msg is None:
        return False
    initial_embed: discord.Embed = thread_dir_msg.embeds[0]
    thread_ids: list[int] = [int(line[4:-1]) for field in initial_embed.fields for line in field.value.splitlines()]
    if thread.id not in thread_ids:
        return False
    thread_ids.remove(thread.id)
    if thread.guild.id == 933075515881951292:
        return await remove_feedback_thread_from_feedback_thread_directory(thread, thread_dir_msg, thread_ids)
    parent_ids: list[int] = await get_parent_ids(thread_ids, thread)
    thread_directory_embed: discord.Embed = await get_thread_directory_embed(parent_ids, thread_ids, thread.guild)
    await thread_dir_msg.edit(embed=thread_directory_embed, content=None)
    return True
