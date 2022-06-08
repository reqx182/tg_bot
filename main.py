import logging
import pytube
import os
import requests

#os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"
from moviepy.editor import AudioFileClip
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters, \
    ConversationHandler
from telegram.constants import MESSAGEENTITY_URL as URL
from telegram.constants import MESSAGEENTITY_TEXT_LINK as TEXT_LINK
import telegram.ext.filters as filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

KEYBOARD, BUTTONS, LINK = range(3)


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Введите ссылку ')
    return KEYBOARD


def keyboard(update: Update, context: CallbackContext):
    url = update.message.text
    """Выводит клавиатуру Загрузить видео | Загрузить аудио"""
    keyboard = [[
        InlineKeyboardButton("video", callback_data='video'),
        InlineKeyboardButton("audio", callback_data='audio')],
        [
            InlineKeyboardButton("cancel", callback_data='cancel')
        ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(url, reply_markup=reply_markup)
    return BUTTONS


def link_check(link) -> bool:
    try:
        pytube.YouTube(link)
        return True
    except:
        print("Неправильная ссылка")
        return False


def delet_syms(title: str) -> str:
    """Удаляет лишние символы из названия файла во избежании ошибки при сохранении"""
    wrong_syms = '|\\/_-!"№;%:?*+='
    title = title.split()
    for index in range(len(title)):
        if title[index] in wrong_syms:
            title[index] = ''
    title = "".join(title)
    return title


def video(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    link = update.callback_query['message']['text']
    if not link_check(link):
        update.callback_query.bot.send_message(chat_id, 'Неправильная ссылка. Введите ссылку ещё раз.')
        return KEYBOARD

    update.callback_query.bot.send_message(chat_id, 'Подождите, видео скачивается.')
    yt = pytube.YouTube(link)
    stream = yt.streams.get_highest_resolution()
    title = yt.title
    title = delet_syms(title)
    filename = f'{title}.mp4'
    stream.download(filename=filename)
    file = open(filename, 'rb')
    update.callback_query.bot.send_video(chat_id, file, timeout = 100)
    print(os.getcwd())
    #os.remove(f'{os.getcwd()}/{filename}')
    print('video')

    return KEYBOARD


def audio(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    link = update.callback_query['message']['text']
    if not link_check(link):
        update.callback_query.bot.send_message(chat_id, 'Неправильная ссылка. Введите ссылку ещё раз.')
        return KEYBOARD

    update.callback_query.bot.send_message(chat_id, 'Подождите, аудио скачивается.')
    yt = pytube.YouTube(link)
    stream = yt.streams.get_highest_resolution()
    title = yt.title
    title = delet_syms(title)
    filename = f'{title}'
    stream.download(filename=filename)
    file = open(filename, 'rb')
    update.callback_query.bot.send_audio(chat_id, file, timeout = 100)
    convert_to_mp3(filename + '.mp4', filename + '.mp3')
    os.remove(f'{os.getcwd()}/{filename}')
    print('audio')

    return KEYBOARD


def convert_to_mp3(input_mp4_file, output_name_file='без названия.mp3', delete_input_file=True):
    in_audio = AudioFileClip(input_mp4_file)
    in_audio.write_audiofile(filename=output_name_file)
    in_audio.close()
    print('конвертация выполнена')
    if delete_input_file:
        os.remove(input_mp4_file)


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Введите новую ссылку')
    return KEYBOARD


def exit(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.'
    )
    return ConversationHandler.END


def send_audio(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    url = open('AFRAID.mp4', 'rb')
    update.message.bot.send_audio(chat_id, url)


def main():
    TOKEN = '5386827464:AAGLD9D-ypRRQJmc-LTB82EUW7VDVRmTKt0'
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            KEYBOARD: [
                MessageHandler(Filters.text, keyboard)
            ],
            BUTTONS: [
                CallbackQueryHandler(video, pattern='video'),
                CallbackQueryHandler(audio, pattern='audio'),
                CallbackQueryHandler(cancel, pattern='cancel')
            ]
        },
        fallbacks=[CommandHandler('exit', exit)])

    # filters.TEXT & (filters.Entity(URL) | filters.Entity(TEXT_LINK)) ?????
    # filters.TEXT & (~ filters.FORWARDED)
    # Filters.regex('^(Boy|Girl|Other)$')

    dispatcher.add_handler(CommandHandler('send', send_audio))
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

