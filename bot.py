import sys

from aiogram.utils import executor
from aiogram.types import BotCommand

from bot.headlers import *
from bot.utils import dp
from string_consts import *


async def set_commands(dp):
    commands = [
        BotCommand(command="/start", description=string_consts.start_command_description),
        BotCommand(command="/help", description=string_consts.help_command_description),
        BotCommand(command="/set_style", description=string_consts.set_style_command_description),
        BotCommand(command="/modified_photo", description=string_consts.modified_photo_command_description),
        BotCommand(command="/generate", description=string_consts.generate_command_description)
    ]

    await dp.bot.set_my_commands(commands)


if __name__ == '__main__':
    logger.remove()
    logger.add(
        'logs/debug.log',
        format='[{time:YYYY-MM-DD HH:mm:ss}] {level} | {message}',
        level='TRACE'
    )
    logger.add(
        sys.__stdout__,
        format='[{time:YYYY-MM-DD HH:mm:ss}] {level} | {message}',
        level='TRACE',
        colorize=True
    )

    executor.start_polling(dp, skip_updates=True, on_startup=set_commands)
