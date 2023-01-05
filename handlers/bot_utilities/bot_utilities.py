from discord_helpers import DiscordHelpers
from handlers.handler import Handler, HandleInfo
import discord


class BotUtilities(Handler):
    def __init__(self, bot: discord.Client, bot_channel_id, original_handler: Handler, help_file_path: str) -> None:
        super().__init__(__file__)
        self.bot = bot
        self.bot_channel_id = bot_channel_id
        self.original_handler = original_handler if original_handler else self
        self.help_file_path = help_file_path

    async def __handle_commands__(self, message: discord.Message, args: str, admin: bool) -> HandleInfo:
        if args[0] == "help" and admin:
            await message.author.send(content="Help message", file=discord.File(self.help_file_path))
            return HandleInfo.Handled(self)
        if args[0] == "logout" and admin:
            await self.original_handler.handle_logout(self.bot)
            await self.bot.close()
            return HandleInfo.Handled(self)
        if args[0] == "log_roles" and admin:
            if DiscordHelpers.is_private_message(message) or len(args) < 2:
                return HandleInfo.RecognizedAndNotHandled(self)
            members_of_role = DiscordHelpers.get_members_of_role(message.guild, args[1:-1])
            text = f"Found {len(members_of_role)} accounts with at least one of the roles!\n"
            for member in members_of_role:
                text += member.name + ", "
            await message.channel.send(text)
            return HandleInfo.Handled(self)
        if args[0] == "separator":
            await message.channel.send(self.data["separator"] * self.data["separator_length"])
            await message.delete()
            return HandleInfo.Handled(self)
        if args[0] == "neutral_face":
            await message.channel.send(":neutral_face:")
            await message.delete()
            return HandleInfo.Handled(self)

        return HandleInfo.NotHandled(self)

    async def __handle_logout__(self, bot: discord.Client):
        await bot.get_channel(self.bot_channel_id).send("Logging out!")
