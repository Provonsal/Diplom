# coding=utf-8

import telebot
import multiprocessing
import os
import time
from pathlib import Path
import shutil
import sql

bot = telebot.TeleBot('token')

b = 0


def load_img(message):
    
    user_id = str(message.from_user.id)
    file_info = bot.get_file(message.photo[-1].file_id)
    file_path = file_info.file_path
    
    sql.addData(user_id, file_path, 0, 1)
    
            
    
def download_images(message, user_id):
        
        lis = sql.select(user_id)
        print(lis)
        lis_i = []
        user_id = str(user_id) + '/'

        for i in lis:
            
            if i[1]:
                lis_i.append(i[0])

        for i in lis_i:
            
            downloaded_file = bot.download_file(i)
            print(user_id)

            if not os.path.isdir('bot-images/' + user_id):
                os.mkdir('bot-images/' + user_id) 
            file_name = i.replace('photos/', '')
        
            src = 'bot-images/'+ user_id + file_name
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)

        text = f'{len(lis_i)} images have loaded'
        bot.send_message(message.chat.id, text)

def load_vid(message):
    
    user_id = str(message.from_user.id)
    file_info = bot.get_file(message.video.file_id)
    file_path = file_info.file_path
    
    sql.addData(user_id, file_path, 1, 0)

def download_videos(message, user_id):
     
    lis = sql.select(user_id)
    print(lis)
    lis_v = []

    for i in lis:

        if i[2]:
            
            lis_v.append(i[0])

    print(lis_v)

    for i in lis_v:
        
        downloaded_file = bot.download_file(i)
        user_id = user_id + '/'
        if not os.path.isdir('bot-images/' + user_id):
            os.mkdir('bot-images/' + user_id) 
        file_name = i.replace('videos/', '') #message.video.file_id + '.mp4' if message.video == None else message.video.file_name
    
        src = 'bot-images/'+ user_id + file_name
        
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        
    text = f'{len(lis_v)} videos have loaded'
    bot.send_message(message.chat.id, text)
        
    
        
def NeurN(message, user_id): 
    
    from detect import run as NN
    chat = message.chat.id
    path = f'C:/Users/Provonsal/source/repos/yolov5/bot-images/{user_id}/'
    NN(**{'source':path, 'project':path})

    def sending_back(chat):
        path = f'C:/Users/Provonsal/source/repos/yolov5/bot-images/{user_id}/exp/'
        arti = os.listdir(path) # list of directory
        medias = [] # help list
        photos = [] # list for photo
        videos = [] # list for videos

        def otpravka_photo(medias, photos, chat):
            
            photos = photos
            photos_copy = photos.copy()
            
            for i in photos:
                print('first')
                print('len of medias: ',len(medias))
                print('len of photos: ',len(photos))
                if len(photos) < 10:
                    break

                elif len(photos) == 10:
                    
                    for i in photos:
                        medias.append(telebot.types.InputMediaPhoto(open(f'{path}{i}', 'rb')))
                    
                    bot.send_media_group(chat, medias)   
                    medias = []

                    break

                elif len(medias) == 10:
                    
                    
                    bot.send_media_group(chat, medias)  
                    medias = []
                    if len(photos_copy) < 10:
                        
                        break

                medias.append(telebot.types.InputMediaPhoto(open(f'{path}{i}', 'rb')))
                print('len of photos_copy: ',len(photos_copy))
                photos_copy.remove(i)
                    
            if len(photos) != 10:

                for i in photos_copy:

                    print('second')
                    print('len of photos_copy: ', len(photos_copy))

                    with open(f'{path}{i}', 'rb') as photo:
                        bot.send_photo(chat,photo)
                        medias = []
            
        
        def otpravka_vid(videos, chat):

            for i in videos:

                print('second')
                print('len of videos: ', len(videos))

                with open(f'{path}{i}', 'rb') as video:
                    print(i)
                    bot.send_video(chat,video)
            
        for i in arti:

            format = Path(f'{path}{i}').suffix

            if format == '.png' or format == '.jpg' or format == '.jpeg':

                print('raz')
                photos.append(i)

            elif format == '.mp4':

                print('dva')
                print(i)
                videos.append(i)

        otpravka_photo(medias, photos, chat)
        otpravka_vid(videos, chat)
        
        markup = telebot.types.InlineKeyboardMarkup(row_width = 1)
        button_1 = telebot.types.InlineKeyboardButton(text='Load files again', callback_data='Load files')
        markup.add(button_1)

        bot.send_message(chat, 'All processed files have sent. Now you can press "Load files again" and try again', reply_markup = markup)
        
    sending_back(chat)

def process_creater(file, func, args):
    
    if file == True:

        print('создаю процесс 1')
        proc1 = multiprocessing.Process(target = func, args=args)
        proc1.start()

    elif file == False:

        print('создаю процесс 2')
        proc2 = multiprocessing.Process(target = func, args=args)
        proc2.start()
    


def loader(message):
    
    content = message.content_type

    if content == 'photo':

        time.sleep(1)
        print('Создаю процесс добавления фото в бд') 
        process_creater(1, load_img, (message,))

    elif content == 'video':

        print('Создаю процесс добавления видео в бд')
        time.sleep(1)
        process_creater(0, load_vid, (message,))

@bot.message_handler(commands=['start']) # 111111111111111111111111111111111111
def main1(message):
    
    global a

    markup = telebot.types.InlineKeyboardMarkup(row_width = 1)
    button_1 = telebot.types.InlineKeyboardButton(text='Next step: file loading', callback_data='Load files')
        
    text = """Hello, stranger. 

I'm a bot, my name is 1pd8 and I can recognize images on your screenshot(s) or video(s).
        
Please press the button below ⬇ to continue. 
"""
    markup.add(button_1)

    bot.send_message(message.chat.id, text, reply_markup = markup)

def processing(message, real_user_id):
    
    global a
    
    text = """Well let's start.
This process will take a while, please wait.
Results will be automaticaly send here.
"""
       
    markup = telebot.types.InlineKeyboardMarkup(row_width = 1)
    button_1 = telebot.types.InlineKeyboardButton(text='Load files again', callback_data='Load files')
        
    markup.add(button_1)
        
    bot.send_message(message.chat.id, text)  
    NeurN(message, real_user_id)



def end_loading(message, real_user_id):
        global b
        
        markup1 = telebot.types.ReplyKeyboardRemove()
        markup2 = telebot.types.InlineKeyboardMarkup(row_width = 1)
        button_1 = telebot.types.InlineKeyboardButton(text='Load files again', callback_data='Load files')
        
        text1 = """Understood. Downloading files. """
        text2 = """ Files are downloaded. Starting processing... """
        path = f'C:/Users/Provonsal/source/repos/yolov5/bot-images/{real_user_id}'
        markup2.add(button_1)
        #process_creater(1, download_images, (message, ))
        #content = message.content_type
        bot.send_message(message.chat.id, text1, reply_markup = markup1)
        print('Создаю процесс загрузки фотографии 1111')
        #process_creater(1, download_images, (message,real_user_id))
        proc1 = multiprocessing.Process(target = download_images, args=(message,real_user_id))
        proc1.start()
        print('Создаю процесс загрузки видео 1111')
        proc2 = multiprocessing.Process(target = download_videos, args=(message,real_user_id))
        proc2.start()
        #process_creater(0, download_videos, (message,real_user_id))
        
        proc1.join()
        proc2.join()
        b = 0
        bot.send_message(message.chat.id, text2)
        if os.path.exists(path):
            process_creater(0, processing, (message,real_user_id))
        else:
            bot.send_message(message.chat.id, 'Sorry, but there is no files to process.', reply_markup=markup2)
        #NeurN(message, real_user_id)
        
        
    
@bot.callback_query_handler(func=lambda call: True) # 22222222222222222222222222222222222
def bum_main(call):
    
    
    real_user_id = str(call.from_user.id)
    
    
    
    def start_loading(message, real_user_id):
        
        global b
        chat = message.chat.id
        user_id = str(message.from_user.id)
        print(user_id)
        path = f'C:/Users/Provonsal/source/repos/yolov5/bot-images/{real_user_id}'
        def deleting(real_user_id):
            print(real_user_id)
            sql.deleteData(real_user_id)
            bot.send_message(chat, 'Deleting previous files from my storage...')
            
            
            
            print('deleting')
            shutil.rmtree(path)
            
            time.sleep(5)
            bot.send_message(chat, 'Deleting complete.')
            
        
        if os.path.exists(path):
            deleting(real_user_id)

        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
        button_1 = telebot.types.KeyboardButton(text="✅ i'm done, please load these files ✅")
        
        text = """Okay let's start, send me your files. It can be photos or videos."""
        
        markup.add(button_1)
        
        bot.send_message(message.chat.id, text, reply_markup = markup)
        b = 1
    
    
    
        
        
    
       
    
    
    
    dict_1 = {'Load files':start_loading
              }         
    if call.data in dict_1:
        dict_1[call.data](call.message, real_user_id)            

@bot.message_handler(func= lambda message: message.text == "✅ i'm done, please load these files ✅")
def jopa(message):
    user_id = str(message.from_user.id)
    #end_loading(message, user_id)
    process_creater(1, end_loading, (message, user_id) ) 

@bot.message_handler(content_types=['photo', 'video'])   # 44444444444444444444444444444444444444444 
def checker(message):
    global b
    
    
    if b:
        print('1')
        loader(message)  
    

    
if __name__ == '__main__':
    

    bot.polling()