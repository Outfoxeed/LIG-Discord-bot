from discord_helpers import DiscordHelpers
from handlers.handler import Handler, HandleInfo
import discord


class PurgeHandler(Handler):
    def __init__(self) -> None:
        super().__init__(__file__)

    async def __handle_commands__(self, message: discord.Message, args: str, admin: bool) -> HandleInfo:
        if not admin or DiscordHelpers.is_private_message(message):
            return HandleInfo.NotHandled(self)

        args_length = len(args)
        if "purge" in args[0] and args_length > 1:
            await DiscordHelpers.try_purge(message.channel, int(args[1]), "silent" in args[0])
            return HandleInfo.Handled(self)
        if args[0] == "delete":
            if args_length == 1:
                await DiscordHelpers.try_purge(message.channel, 1, silent=True)
            elif args_length == 2:
                msg = await DiscordHelpers.get_message(message.channel, int(args[1]))
                if msg:
                    await msg.delete()
                    await message.delete()
                    print(f"A message has been deleted by command")
            return HandleInfo.Handled(self)
        return HandleInfo.NotHandled(self)
