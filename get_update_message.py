# from telebot import TeleBot
# from telebot import ReplyParameters
import telebot
import subprocess
import json
import os



telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
telegram_channel_id = int(os.environ.get("TELEGRAM_CHAT_ID"))



bot = telebot.TeleBot(telegram_bot_token);

# 가장 마지막으로 처리한 값.
lastestUpdateId = 0

try: 
	with open('lastestUpdateId.txt','r') as updateFile:
		savedID = updateFile.readline()
		lastestUpdateId = int(savedID)
except:
	lastestUpdateId = 0

print(f'오프셋 : {lastestUpdateId}')

processedId = 0

messageList = bot.get_updates(offset=lastestUpdateId+1)
for message in messageList:

	# 여기에 들어왔다면 일단 처리 된것이다. 
	if(message.update_id > processedId):
		processedId = message.update_id

	# 가장 먼저 정상적인 채팅방에서 들어온 값인지 확인한다. 아니라면 그냥 끝..
	if(message.message == None or message.message.chat == None or message.message.chat.id !=  telegram_channel_id):
		continue

	# 텍스트 값을 보고 이 값이 youtube 음악이라면 다운로드 받아서 값을 반환 해준다. 
	text = message.message.text
	print(f'test {text}')

	if(text != None and text.startswith('https://youtu.be')):
		print('가자')
		# print(subprocess.check_output(['yt-dlp', '-j', text]))
		musicInfoString = subprocess.check_output(['yt-dlp', '-j', text])
		musicInfo = json.loads(musicInfoString)
		if(musicInfo != None and musicInfo['formats'] != None):
			for f in musicInfo['formats']:
				# print(f'{f.get('audio_ext','null')}/{f.get('video_ext','null')}/{f.get('resolution','null')}/{f.get('format_note','null')}/{f.get('filesize','null')}/')
				# 오디오 포멧. 중간이상 품질, m4a 포멧 이면 다운로드 하자. 
				if(f.get('resolution','null') == 'audio only' and f.get('format_note','null') == 'medium' and f.get('audio_ext','null') == 'm4a' and f.get('format_id','null')!= 'null'):
					formatId = f.get('format_id','null')
					subprocess.run(['yt-dlp', '--paths', './songs', '-f', formatId, text])
					songList = os.listdir('./songs')
					print(songList)
					if(len(songList) > 0):
						filePath = os.path.join('songs',songList[0])
						print(f'file path : {filePath}')
						re = telebot.types.ReplyParameters(message_id=message.message.message_id,chat_id=message.message.chat.id, allow_sending_without_reply=True)
						bot.send_audio(chat_id=message.message.chat.id, audio=open(filePath,'rb'), reply_parameters=re)
						#보내고 나면 삭제 한다. 
						subprocess.run(['rm', '-rf', filePath])


print(processedId)


if(processedId != lastestUpdateId):
	os.system(f'echo \'list_count={processedId}\' >> $GITHUB_OUTPUT')
	with open('lastestUpdateId.txt','w') as updateFile:
		 updateFile.write(str(processedId))


