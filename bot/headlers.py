from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from loguru import logger

import utils
from .settings import bot, dp
from model.app import main


class Form(StatesGroup):
    image_style = State()
    image_source = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
    logger.info(f'User {message.from_user.id} {message.from_user.username} started')
    await message.answer(utils.main_text)


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message) -> None:
    logger.info(f'User {message.from_user.id} {message.from_user.username} requested help')
    help_text = "This bot allows you to send two photos and receive a photo with the style transferred.\n\n" \
                "Available commands:\n" \
                "/start - Start interacting with the bot\n" \
                "/set_style - Select the style for the photo\n" \
                "/modified_photo - Select the photo for style transfer\n" \
                "/generate - Generate a new photo with the transferred style\n" \
                "/help - Display this help message"
    await message.answer(help_text)


@dp.message_handler(state='*', commands=['set_style'])
async def set_style_photo(message: types.Message):
    logger.info(f'Started loading photo style for {message.from_user.id}')
    await Form.image_style.set()
    await message.reply(utils.photo_style_text)


@dp.message_handler(state=Form.image_style, content_types=['photo'])
async def set_style_photo_received(message: types.Message, state: FSMContext):
    try:
        file_id = message.photo[-1].file_id
        logger.info(f'{message.from_user.id} loading {file_id}.jpg')

        async with state.proxy() as data:
            data['image_style'] = file_id

        await message.photo[-1].download(destination_file=f'Photos/style_photos/{file_id}.jpg')

        await message.answer("Style photo has been successfully set.")

    except Exception as e:
        logger.exception(f'Error occurred while setting the style photo: {str(e)}')
        await message.answer(f"An error occurred while setting the style photo: {str(e)}")


@dp.message_handler(state='*', commands=['modified_photo'])
async def set_source_photo(message: types.Message) -> None:
    logger.info(f'Started loading photo source for {message.from_user.id}')
    await Form.image_source.set()
    await message.reply(utils.photo_source_text)


@dp.message_handler(state=Form.image_source, content_types=['photo'])
async def set_source_photo_received(message: types.Message, state: FSMContext):
    try:
        file_id = message.photo[-1].file_id
        logger.info(f'{message.from_user.id} loading {file_id}.jpg')

        async with state.proxy() as data:
            data['image_source'] = file_id
            data['size'] = [message.photo[-1].width, message.photo[-1].height]

        await message.photo[-1].download(destination_file=f'Photos/style_photos/{file_id}.jpg')

        await message.answer("Source photo has been successfully set.")

    except Exception as e:
        logger.exception(f'Error occurred while setting the source photo: {str(e)}')
        await message.answer(f"An error occurred while setting the source photo: {str(e)}")


@dp.message_handler(state='*', commands=['generate'])
async def generate_photo(message: types.Message, state: FSMContext):
    try:
        logger.info(f'{message.from_user.id} generating photo')

        async with state.proxy() as data:
            if len(data) != 3:
                await message.answer(utils.error_generate)
                return

            logger.info('{} | source file: {} | image_file: {}'.format(message.from_user.id, data['image_source'],
                                                                       data['image_style']))
            output_file = main(data['image_source'], data['image_style'], data['size'],
                               epochs=50)

            with open(f'Photos/modified_photos/{output_file}', 'rb') as photo_out:
                await bot.send_photo(chat_id=message.chat.id, photo=photo_out)

    except Exception as e:
        logger.exception(f'Error occurred while generating the photo: {str(e)}')
        await message.answer(f"An error occurred while generating the photo: {str(e)}")
