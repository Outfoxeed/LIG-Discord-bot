from __future__ import annotations
import discord
import os
import json

class HandleInfo:
    def __init__(self, handler: Handler, need_next_handle: bool = True, command_recognized: bool = False, took_action: bool = False) -> None:
        self.handler = handler
        self.need_next_handle = need_next_handle
        self.command_recognized = command_recognized
        self.took_action = took_action

    def __str__(self):
        return f"{self.handler.__class__.__name__}; command_recognized:{self.command_recognized}; took_action:{self.took_action}; need_next_handle:{self.need_next_handle}"

    @staticmethod
    def NotHandled(handler: Handler) -> HandleInfo:
        return HandleInfo(handler, need_next_handle=True, command_recognized=False, took_action=False)
    @staticmethod
    def RecognizedAndNotHandled(handler: Handler) -> HandleInfo:
        return HandleInfo(handler, need_next_handle=False, command_recognized=True, took_action=False)
    @staticmethod
    def Handled(handler: Handler) -> HandleInfo:
        return HandleInfo(handler, need_next_handle=False, command_recognized=True, took_action=True)


class Handler:

    next_handler: Handler = None

    def __init__(self, file):
        file_path = os.path.dirname(file)
        config_file_path = os.path.join(file_path, "config.json")
        if os.path.isfile(config_file_path):
            with open(config_file_path, "r", encoding="utf-8") as config_file:
                self.data = json.loads(config_file.read())

        help_text_path = os.path.join(file_path, "help.txt")
        if os.path.isfile(help_text_path):
            with open(help_text_path, "r", encoding="utf-8") as help_file:
                self.help_text = help_file.read()
        else:
            self.help_text = ""

    def set_next_handler(self, handler: Handler) -> Handler:
        if self.next_handler is not None:
            return self.next_handler.set_next_handler(handler)
        else:
            self.next_handler = handler
            return self.next_handler

    def get_help_text(self) -> str:
        if self.next_handler:
            return self.help_text + "\n\n" + self.next_handler.get_help_text()
        else:
            return self.help_text

    async def handle_commands(self, message: discord.Message, args, admin: bool) -> HandleInfo:
        if len(args) > 0:
            handle_info: HandleInfo = await self.__handle_commands__(message, args, admin)
            if handle_info.command_recognized or not self.next_handler:
                return handle_info

            if self.next_handler:
                return await self.next_handler.handle_commands(message, args, admin)

    async def handle_message(self, message: discord.Message) -> HandleInfo:
        handle_info: HandleInfo = await self.__handle_message__(message)
        if handle_info.command_recognized or not self.next_handler:
            return handle_info

        if self.next_handler:
            return await self.next_handler.handle_message(message)

    async def handle_reaction(self, member: discord.Member, message: discord.Message, emoji: discord.PartialEmoji, added: bool) -> HandleInfo:
        handle_info: HandleInfo = await self.__handle_reaction__(member, message, emoji, added)
        if handle_info.command_recognized or not self.next_handler:
            return handle_info
        if self.next_handler:
            return await self.next_handler.handle_reaction(member, message, emoji, added)

    async def handle_vc_update(self, member: discord.Member, before: discord.VoiceChannel, after: discord.VoiceChannel):
        await self.__handle_vc_update__(member, before, after)
        if self.next_handler:
            await self.next_handler.handle_vc_update(member, before, after)

    async def handle_start(self, bot: discord.Client):
        await self.__handle_start__(bot)
        if self.next_handler:
            await self.next_handler.handle_start(bot)

    async def handle_logout(self, bot: discord.Client):
        try:
            await self.__handle_logout__(bot)
        except:
            print(f"Something went wrong during __handle_logout__ of {type(self)}")
        finally:
            if self.next_handler:
                await self.next_handler.handle_logout(bot)

    # Handle arguments of a command
    # Returns infos about the action
    # by self and/or next_handler
    async def __handle_commands__(self, message: discord.Message, args:str, admin: bool) -> HandleInfo:
        return HandleInfo.NotHandled(self)

    # Handle message content
    # Returns infos about the action
    # and shouldn't be handled by next_handler
    async def __handle_message__(self, message: discord.Message) -> HandleInfo:
        return HandleInfo.NotHandled(self)

    # Handle reaction event
    # Returns infos about the action
    # and shouldn't be handled by next_handler
    async def __handle_reaction__(self, member: discord.Member, message: discord.Message, emoji: discord.PartialEmoji, added: bool) -> HandleInfo:
        return HandleInfo.NotHandled(self)

    # Handle vc update
    async def __handle_vc_update__(self, member: discord.Member, before: discord.VoiceChannel, after: discord.VoiceChannel):
        pass

    # Handle start event
    async def __handle_start__(self, bot: discord.Client):
        pass

    # Handle logout event
    async def __handle_logout__(self, bot: discord.Client):
        pass