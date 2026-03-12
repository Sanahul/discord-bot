import discord
from discord.ext import commands
from datetime import datetime, timezone


def format_timedelta(dt: datetime) -> str:
    """Return a human-readable age string from a datetime to now (approximate)."""
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # Approximate using calendar arithmetic
    years = now.year - dt.year
    months = now.month - dt.month
    days = now.day - dt.day
    if days < 0:
        months -= 1
        # Days in the previous month
        prev_month = now.month - 1 or 12
        prev_year = now.year if now.month > 1 else now.year - 1
        import calendar
        days += calendar.monthrange(prev_year, prev_month)[1]
    if months < 0:
        years -= 1
        months += 12
    parts = []
    if years:
        parts.append(f"{years}y")
    if months:
        parts.append(f"{months}mo")
    if days or not parts:
        parts.append(f"{days}d")
    return " ".join(parts)


KEY_PERMISSIONS = [
    ("administrator", "Administrator"),
    ("manage_guild", "Manage Server"),
    ("manage_channels", "Manage Channels"),
    ("manage_roles", "Manage Roles"),
    ("manage_messages", "Manage Messages"),
    ("kick_members", "Kick Members"),
    ("ban_members", "Ban Members"),
    ("mention_everyone", "Mention Everyone"),
    ("manage_nicknames", "Manage Nicknames"),
    ("mute_members", "Mute Members"),
    ("deafen_members", "Deafen Members"),
    ("move_members", "Move Members"),
]

STATUS_LABELS = {
    discord.Status.online: "🟢 Online",
    discord.Status.idle: "🌙 Idle",
    discord.Status.dnd: "⛔ Do Not Disturb",
    discord.Status.offline: "⚫ Offline",
}


class General(commands.Cog):
    """General utility commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="w")
    @commands.guild_only()
    async def whoami(self, ctx, member: discord.Member = None):
        """Display detailed user information including permissions and roles."""
        member = member or ctx.author

        # ── Embed colour: highest role colour, fallback to blurple ──────────
        colour = member.colour if member.colour != discord.Colour.default() else discord.Colour.blurple()

        embed = discord.Embed(colour=colour, timestamp=datetime.now(timezone.utc))
        embed.set_thumbnail(url=member.display_avatar.url)

        # ── Title ────────────────────────────────────────────────────────────
        bot_badge = " 🤖" if member.bot else ""
        embed.set_author(
            name=f"{member}{bot_badge}",
            icon_url=member.display_avatar.url,
        )

        # ── 1. Basic User Info ───────────────────────────────────────────────
        created_at = member.created_at
        embed.add_field(
            name="👤 User",
            value=(
                f"**Username:** {member.name}\n"
                f"**Display Name:** {member.display_name}\n"
                f"**ID:** `{member.id}`"
            ),
            inline=True,
        )
        embed.add_field(
            name="📅 Account Created",
            value=(
                f"{discord.utils.format_dt(created_at, style='D')}\n"
                f"({format_timedelta(created_at)} ago)"
            ),
            inline=True,
        )

        # ── 2. Server Info ───────────────────────────────────────────────────
        joined_at = member.joined_at
        joined_str = (
            f"{discord.utils.format_dt(joined_at, style='D')}\n"
            f"({format_timedelta(joined_at)} ago)"
            if joined_at
            else "Unknown"
        )
        embed.add_field(name="📥 Joined Server", value=joined_str, inline=True)

        # Roles (exclude @everyone, list highest first)
        roles = [r for r in reversed(member.roles) if r.id != ctx.guild.id]
        highest_role = roles[0] if roles else None

        if roles:
            # Build mention list, keeping only complete mentions within the limit
            mentions = [r.mention for r in roles]
            role_mentions = " ".join(mentions)
            if len(role_mentions) > 1024:
                # Trim whole mentions until it fits, then note the count omitted
                kept = []
                total = 0
                for m in mentions:
                    needed = len(m) + (1 if kept else 0)
                    if total + needed > 1020:
                        break
                    kept.append(m)
                    total += needed
                omitted = len(mentions) - len(kept)
                role_mentions = " ".join(kept) + f" (+{omitted} more)"
        else:
            role_mentions = "None"

        embed.add_field(
            name=f"🏷️ Roles ({len(roles)})",
            value=role_mentions,
            inline=False,
        )
        embed.add_field(
            name="⭐ Highest Role",
            value=highest_role.mention if highest_role else "None",
            inline=True,
        )

        # ── 3. Permissions ───────────────────────────────────────────────────
        perms = member.guild_permissions
        perm_lines = []
        for attr, label in KEY_PERMISSIONS:
            has = getattr(perms, attr, False)
            perm_lines.append(f"{'✅' if has else '❌'} {label}")

        embed.add_field(
            name="🔐 Key Permissions",
            value="\n".join(perm_lines),
            inline=True,
        )

        # ── 4. Activity / Status ─────────────────────────────────────────────
        status_text = STATUS_LABELS.get(member.status, "⚫ Offline")
        if member.is_on_mobile():
            status_text += " 📱"

        activity_text = "None"
        if member.activity:
            act = member.activity
            if isinstance(act, discord.Streaming):
                activity_text = f"🎥 Streaming **{act.name}**"
            elif isinstance(act, discord.Spotify):
                activity_text = f"🎵 Listening to **{act.title}** by {act.artist}"
            elif isinstance(act, discord.Game):
                activity_text = f"🎮 Playing **{act.name}**"
            elif isinstance(act, discord.CustomActivity):
                activity_text = str(act) or "None"
            else:
                activity_text = str(act.name) if act.name else "None"

        voice_text = "Not in voice"
        if member.voice and member.voice.channel:
            voice_text = member.voice.channel.mention

        embed.add_field(
            name="📡 Activity",
            value=(
                f"**Status:** {status_text}\n"
                f"**Activity:** {activity_text}\n"
                f"**Voice:** {voice_text}"
            ),
            inline=True,
        )

        # ── 5. Account Details ───────────────────────────────────────────────
        flags = member.public_flags
        badge_map = {
            "staff": "👨‍💼 Discord Staff",
            "partner": "🤝 Partner",
            "hypesquad": "🏠 HypeSquad Events",
            "bug_hunter": "🐛 Bug Hunter",
            "bug_hunter_level_2": "🐛 Bug Hunter (Gold)",
            "hypesquad_bravery": "🏅 HypeSquad Bravery",
            "hypesquad_brilliance": "🏅 HypeSquad Brilliance",
            "hypesquad_balance": "🏅 HypeSquad Balance",
            "early_supporter": "💜 Early Supporter",
            "verified_bot_developer": "🤖 Verified Bot Developer",
            "active_developer": "👨‍💻 Active Developer",
        }
        badges = [label for attr, label in badge_map.items() if getattr(flags, attr, False)]
        badges_text = "\n".join(badges) if badges else "None"

        accent = f"#{member.accent_colour.value:06X}" if member.accent_colour else "None"
        embed.add_field(
            name="🏆 Badges",
            value=badges_text,
            inline=True,
        )
        embed.add_field(
            name="🎨 Accent Colour",
            value=accent,
            inline=True,
        )

        if member.banner:
            embed.set_image(url=member.banner.url)

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    @whoami.error
    async def whoami_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Member not found. Please mention a valid user or provide a valid username.")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ This command can only be used in a server.")
        else:
            raise error


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
