# coding=utf-8
#----------------------------------------------#
# VideoLabelBot | Jahus | 2016-02-14           #
#----------------------------------------------#----------------
# Fork from Get500pxBot 1.0.3
# Change log
# * 2016-02-14 :
#     (0.0.0)               - First code (Alpha)
# * 2016-02-15 :
#     (1.0.0)               - First stable version
#     (1.1.0)               - Ajout d'une vérification avant
#                             l'envoi.
#     (1.1.1)               - Remplacement des éléments Markdown
#                             dans la description de la vidéo
#                             pour VideoLabel.
# * 2016-02-20 :
#     (1.1.2)               - Ajout d'un test sur la longueur
#                             de la description.
#     (1.1.3)               - Les noms de commandes sans
#                             paramètres s'affichent
#                             en texte et non en code.
# * 2016-05-26 :
#     (1.2.3)               - Cleaning the code for GitHub
#
bDEBUG = True
#---------------------------------------------------------------
# IMPORTS
#---------------------------------------------------------------
import json
import requests
import time
import os
requests.packages.urllib3.disable_warnings()
#---------------------------------------------------------------
# DATA
#---------------------------------------------------------------
def load_file_json(file_name):
	with open(file_name, 'r') as _file:
		content = _file.read()
		content_dict = json.loads(content)
		return content_dict
# CONFIG FILES
data_file = {
	"config": "VideoLabelBot_config.json"
}
config = load_file_json(data_file.get("config"))
# VARIABLES
HALT = False
PAUSE = None
__name__ = config.get("bot_name")
__version__ = config.get("bot_version")
print("#---------------------------------------------------------------")
print("# %s version %s, by Jahus & Mohus Softworks." % (__name__, __version__))
print("#---------------------------------------------------------------")
#---------------------------------------------------------------
# Telegram :: Classes
#---------------------------------------------------------------
#
# User or Bot
class telegram_classes_User:
	def __init__(self, data_json):
		self.id = data_json.get("id")
		self.first_name = data_json.get("first_name")
		if "last_name" in data_json:
			self.last_name = data_json.get("last_name")
		else:
			self.last_name = -1
		if "username" in data_json:
			self.username = data_json.get("username")
		else:
			self.username = -1
	def __str__(self):
		r_str = "User #%s | First name: %s" % (self.id, self.first_name)
		if self.last_name != -1:
			r_str += " | Last name: %s" % (self.last_name)
		if self.username != -1:
			r_str += " | Username: @%s" % (self.username)
		return r_str
#
# Group chat
class telegram_classes_GroupChat:
	def __init__(self, data_json):
		self.id = data_json.get("id")
		self.title = data_json.get("title")
	def __str__(self):
		return "Group chat #%s: ""%s""" % (self.id, self.title)
#
# Supergroup chat
class telegram_classes_SupergroupChat:
	def __init__(self, data_json):
		self.id = data_json.get("id")
		self.title = data_json.get("title")
	def __str__(self):
		return "Supergroup #%s: ""%s""" % (self.id, self.title)
#
# Channel
class telegram_classes_Channel:
	def __init__(self, data_json):
		self.id = data_json.get("id")
		self.title = data_json.get("title")
	def __str__(self):
		return "Channel #%s: ""%s""" % (self.id, self.title)
# 
# Types for Message
telegram_types = {
	"text": "T",
	"forward_from": "F",
	"reply_to_message": "R",
	"audio": "A",
	"document": "G",
	"photo": "I",
	"sticker": "S",
	"video": "V",
	"contact": "U",
	"location": "L",
	"new_chat_participant": "cpn",
	"left_chat_participant": "cpl",
	"new_chat_title": "ctn",
	"new_chat_photo": "cin",
	"delete_chat_photo": "cid",
	"group_chat_created": "gcc",
	"supergroup_chat_created": "sgcc",
	"channel_chat_created": "ccc",
	"migrate_to_chat_id": "mtci",
	"migrate_from_chat_id": "mfci"
}
#
class telegram_classes_Message:
	def __init__(self, data_json):
		self.type = ""
		self.message_id = data_json.get("message_id")
		if "from" in data_json:
			self.sender = telegram_classes_User(data_json.get("from"))
		else:
			self.sender = "[N/A]"
		self.date = data_json.get("date")
		# NEW API ELEMENTS (2016-02-05) for channels
		if data_json["chat"]["type"] == "private":
			self.chat = telegram_classes_User(data_json.get("chat"))
			self.chat_type = "private"
		elif data_json["chat"]["type"] == "group":
			self.chat = telegram_classes_GroupChat(data_json.get("chat"))
			self.chat_type = "group"
		elif data_json["chat"]["type"] == "supergroup":
			self.chat = telegram_classes_SupergroupChat(data_json.get("chat"))
			self.chat_type = "supergroup"
		else: #elif
			self.chat = telegram_classes_Channel(data_json.get("chat"))
			self.chat_type = "channel"
		#
		if "forward_from" in data_json:
			self.forward_from = telegram_classes_User(data_json.get("forward_from"))
			if telegram_types.get("forward_from") not in self.type: self.type += telegram_types.get("forward_from")
		if "forward_date" in data_json:
			self.forward_date = data_json.get("forward_date")
		if "reply_to_message" in data_json:
			self.reply_to_message = telegram_classes_Message(data_json.get("reply_to_message"))
			if telegram_types.get("reply_to_message") not in self.type: self.type += telegram_types.get("reply_to_message")
		if "text" in data_json:
			self.text = data_json.get("text")
			if telegram_types.get("text") not in self.type: self.type += telegram_types.get("text")
		if "audio" in data_json:
			self.audio = data_json.get("audio") #TODO: Audio structure
			if telegram_types.get("audio") not in self.type: self.type += telegram_types.get("audio")
		if "document" in data_json:
			self.document = data_json.get("document") #TODO: Document structure
			if telegram_types.get("document") not in self.type: self.type += telegram_types.get("document")
		if "photo" in data_json:
			self.photo = data_json.get("photo") #TODO: Photo structure
			if telegram_types.get("photo") not in self.type: self.type += telegram_types.get("photo")
		if "sticker" in data_json:
			self.sticker = data_json.get("sticker") #TODO: Sticker structure
			if telegram_types.get("sticker") not in self.type: self.type += telegram_types.get("sticker")
		if "video" in data_json:
			self.video = data_json.get("video") #TODO: Video structure
			if telegram_types.get("video") not in self.type: self.type += telegram_types.get("video")
		if "caption" in data_json:
			self.caption = data_json.get("caption")
		if "contact" in data_json:
			self.contact = data_json.get("contact") #TODO: Contact structure
			if telegram_types.get("contact") not in self.type: self.type += telegram_types.get("contact")
		if "location" in data_json:
			self.location = data_json.get("location") #TODO: Location structure
			if telegram_types.get("location") not in self.type: self.type += telegram_types.get("location")
		if "new_chat_participant" in data_json:
			self.new_chat_participant = telegram_classes_User(data_json.get("new_chat_participant"))
			if telegram_types.get("new_chat_participant") not in self.type: self.type += telegram_types.get("new_chat_participant")
		if "left_chat_participant" in data_json:
			self.left_chat_participant = telegram_classes_User(data_json.get("left_chat_participant"))
			if telegram_types.get("left_chat_participant") not in self.type: self.type += telegram_types.get("left_chat_participant")
		if "new_chat_title" in data_json:
			self.new_chat_title = data_json.get("new_chat_title")
			if telegram_types.get("new_chat_title") not in self.type: self.type += telegram_types.get("new_chat_title")
		if "new_chat_photo" in data_json:
			self.new_chat_photo = data_json.get("new_chat_photo") #TODO: Photo structure
			if telegram_types.get("new_chat_photo") not in self.type: self.type += telegram_types.get("new_chat_photo")
		if "delete_chat_photo" in data_json:
			self.delete_chat_photo = data_json.get("delete_chat_photo") # Boolean
			if telegram_types.get("delete_chat_photo") not in self.type: self.type += telegram_types.get("delete_chat_photo")
		if "group_chat_created" in data_json:
			self.group_chat_created = data_json.get("group_chat_created") # Boolean
			if telegram_types.get("group_chat_created") not in self.type: self.type += telegram_types.get("group_chat_created")
		# added 2016-02-05
		if "supergroup_chat_created" in data_json:
			self.supergroup_chat_created = data_json.get("supergroup_chat_created") # Boolean
			if telegram_types.get("supergroup_chat_created") not in self.type: self.type += telegram_types.get("supergroup_chat_created")
		if "channel_chat_created" in data_json:
			self.channel_chat_created = data_json.get("channel_chat_created") # Boolean
			if telegram_types.get("channel_chat_created") not in self.type: self.type += telegram_types.get("channel_chat_created")
		if "migrate_to_chat_id" in data_json:
			self.channel_chat_created = data_json.get("migrate_to_chat_id") # integer
			if telegram_types.get("migrate_to_chat_id") not in self.type: self.type += telegram_types.get("migrate_to_chat_id")
		if "migrate_from_chat_id" in data_json:
			self.channel_chat_created = data_json.get("migrate_from_chat_id") # Boolean
			if telegram_types.get("migrate_from_chat_id") not in self.type: self.type += telegram_types.get("migrate_from_chat_id")
	def __str__(self):
		return "Message #%s at %s. From %s to %s." % (self.message_id, self.date, self.sender, self.chat)
#
class telegram_classes_Update:
	def __init__(self, data_json):
		self.update_id = data_json.get("update_id")
		self.type = ""
		if "message" in data_json:
			self.message = telegram_classes_Message(data_json.get("message"))
			self.type += "m"
		if "inline_query" in data_json:
			self.inline_query = telegram_classes_InlineQuery(data_json.get("inline_query"))
			self.type += "iq"
		if "chosen_inline_result" in data_json:
			self.chosen_inline_result = telegram_classes_ChosenInlineResult(data_json.get("chosen_inline_result"))
			self.type += "ir"
	def __str__(self):
		return "Update #%s | Type: %s" % (self.update_id, self.type)
#
# UPDATE 2016-01-05 InLine query
class telegram_classes_InlineQuery:
	def __init__(self, data_json):
		self.id = data_json.get("id")
		self.sender = telegram_classes_User(data_json.get("from"))
		self.query = data_json.get("query")
		self.offset = data_json.get("offset")
#
class telegram_classes_ChosenInlineResult:
	def __init__(self, data_json):
		self.result_id = data_json.get("result_id")
		self.sender = data_json.get("from")
		self.query = data_json.get("query")
#
#---------------------------------------------------------------
# Telegram :: Bot
#---------------------------------------------------------------
telegram_bot_token = config.get("telegram_params").get("token")
telegram_bot_request = "https://api.telegram.org/bot"
#
telegram_bot_info = None
telegram_bot_offset = 0
#
# Error messages can be formatted with simple Markdown or simple HTML
error_messages = {
	"err_source": [
		"*Error*",
		"_Sorry, I can't do this with these arguments._",
		"Usage: `/command_name <opt1> [opt2]`",
		"Example: `/command_name DOGE BTC`",
		"Another line here"
		],
	"err_source_2": [
		"*Warning*",
		"foo",
		"`boo`",
		"Example: `blah`"
		],
	"api_error": [
		"*Error*",
		"Source returned:"
		]
	}
#
def telegram_bot_get_bot_info():
	if bDEBUG:
		print("** get_bot_info(): getting bot information...")
	global telegram_bot_info
	req = requests.get("%s%s%s" % (telegram_bot_request, telegram_bot_token, "/getMe"))
	if (req.status_code != 200):
		print("** get_bot_info(): Error %s" % req.status_code)
	else:
		req_json = req.json()
		if "ok" in req_json:
			if (req_json.get("ok") == True):
				_me = telegram_classes_User(req_json.get("result"))
				telegram_bot_info = _me
				print(telegram_bot_info)
			else:
				print("** get_bot_info(): Error %s" % "There has been an unknown error")
		else:
			print("** get_bot_info(): Error %s" & "There has been an unknown error.")
#
def telegram_bot_get_updates():
	global telegram_bot_offset
	req_data = {
		"offset": telegram_bot_offset + 1,
		"limit": "",
		"timeout": ""
		}
	req = requests.get("%s%s%s" % (telegram_bot_request, telegram_bot_token, "/getUpdates"), req_data)
	if (req.status_code != 200):
		print("** get_updates(): Error %s" % req.status_code)
	else:
		req_json = req.json()
		# print(req_json)
		if "ok" in req_json:
			if (req_json.get("ok") == True):
				# print("-- telegram_bot_get_updates(): Got %s updates." % len(req_json.get("result")))
				for update_json in req_json.get("result"):
					_update = telegram_classes_Update(update_json)
					print("** get_updates(): reading update '%s'..." % _update.update_id)
					if _update.update_id > telegram_bot_offset: telegram_bot_offset = _update.update_id
					# Traiter le message reçu
					if _update.type == "m":
						telegram_bot_read_message(_update.message)
					else:
						telegram_bot_read_inlinequery(_update)
			else:
				print("** get_updates(): Error %s" % "There has been an unknown error")
		else:
			print("** get_updates(): Error %s" & "There has been an unknown error.")
#
def telegram_bot_send_message(chat_id, text, parse_mode = None, disable_web_page_preview = None, reply_to_message_id = None, reply_markup = None):
	req_data = {
		"chat_id": chat_id,
		"text": text
	}
	print("** Sending message to chat # %s. Text: %s" % (chat_id, text.encode("utf-8")))
	if parse_mode != None:
		req_data.update([("parse_mode", parse_mode)])
	if disable_web_page_preview != None:
		req_data.update([("disable_web_page_preview", disable_web_page_preview)])
	if reply_to_message_id != None:
		req_data.update([("reply_to_message_id", reply_to_message_id)])
	if reply_markup != None:
		req_data.update([("reply_markup", reply_markup)])
	req = requests.post(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/sendMessage"), data = req_data)
	if (req.status_code != 200):
		print("-- answerInlineQuery(): Error %s (::%s)" % (req.status_code, req.content))
	else:
		req_json = req.json()
		# print(req_json)
		#TODO: Verify if send message is equal to received message
#
def telegram_bot_read_message(message):
	# Checking message type
	if telegram_types.get("text") in message.type:
		telegram_bot_handle_message_text(message)
	elif telegram_types.get("new_chat_participant") in message.type:
		telegram_bot_handle_message_chat_participant_new(message)
	elif telegram_types.get("left_chat_participant") in message.type:
		telegram_bot_handle_message_chat_participant_left(message)
	elif telegram_types.get("new_chat_title") in message.type:
		telegram_bot_handle_message_chat_title_new(message)
	elif telegram_types.get("group_chat_created") in message.type:
		telegram_bot_handle_message_group_chat_created(message)
	elif telegram_types.get("photo") in message.type:
		telegram_bot_handle_message_picture(message)
	elif telegram_types.get("channel_chat_created") in message.type:
		telegram_bot_handle_message_channel_chat_created(message)
	elif telegram_types.get("video") in message.type:
		telegram_bot_handle_message_video(message)
	elif telegram_types.get("document") in message.type:
		telegram_bot_handle_message_document(message)
	else:
		print("-- read_message(): Message type unhandled")
#
def telegram_bot_read_inlinequery(Update):
	print("** read_inlinequery(): Reading update...")
	if Update.type == "iq":
		print("--- telegram_bot_read_inlinequery(): Reading inline query...")
		inline_query = Update.inline_query
		sender = inline_query.sender # user that sent the request
		query = inline_query.query # important
		offset = inline_query.offset # not important
		print("---> Query:\n\t#%s: %s" % (inline_query.id, inline_query.query.encode("utf-8")))
		# Add a line to call the main function of your bot with query.split(' ') arguments.
	elif Update.type == "ir":
		print("--- telegram_bot_read_inlinequery(): Reading inline result choice...")
		chosen_inline_result = Update.chosen_inline_result
		# Optional: Add a line to make your bot know what people choose
#
def telegram_bot_sendDocument(chat_id, file_name, reply_to_message_id = None, reply_markup = None, file_name_suppl = '', file_ext = '', mime_type = None, existing_file = False):
	head_data = {
		"chat_id": chat_id
		}
	if reply_to_message_id != None:
		head_data.update([("reply_to_message_id", reply_to_message_id)])
	if reply_markup != None:
		head_data.update([("reply_markup", reply_markup)])
	if existing_file:
		head_data.update([("document", file_name)])
		req = requests.get(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/sendDocument"), params = head_data)
	else:
		_file = {'document': (file_name + file_name_suppl + file_ext, open(file_name + file_ext, 'rb'))}
		req = requests.get(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/sendDocument"), params = head_data, files = _file)
	if (req.status_code != 200):
		print("-- sendDocument(): Error %s\n*** %s" % (req.status_code, req.content))
		return None
	else:
		req_json = req.json()
		if bDEBUG: print("-- sendDocument(): Success\nAnswer:%s" % ("%s" % req_json).encode("utf-8"))
		returned_message = telegram_classes_Message(req_json["result"])
		return {"file_id": returned_message.document["file_id"], "message_id": returned_message.message_id}
#
def telegram_bot_sendPhoto(chat_id, photo, existing_file = False, caption = None, reply_to_message_id = None, reply_markup = None):
	head_data = {
		"chat_id": chat_id
		}
	if caption != None:
		head_data.update([("caption", caption)])
	if reply_to_message_id != None:
		head_data.update([("reply_to_message_id", reply_to_message_id)])
	if reply_markup != None:
		head_data.update([("reply_markup", reply_markup)])
	if existing_file:
		head_data.update([("photo", photo)])
		req = requests.get(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/sendPhoto"), params = head_data)
	else:
		_file = {'photo': (photo, open(photo, 'rb'), "image/jpeg")}
		req = requests.get(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/sendPhoto"), params = head_data, files = _file)
	if (req.status_code != 200):
		print("** sendPhoto(): Error %s\n*** %s" % (req.status_code, req.content))
		return None
	else:
		req_json = req.json()
		if bDEBUG: print("** sendPhoto(): Success\n*** Answer:%s" % ("%s" % req_json).encode("utf-8"))
		returned_message = telegram_classes_Message(req_json["result"])
		return {"file_id": returned_message.photo[-1]["file_id"], "message_id": returned_message.message_id}
#
def telegram_bot_sendVideo(chat_id, video, existing_file = False, duration = None, caption = None, reply_to_message_id = None, reply_markup = None):
	head_data = {
		"chat_id": chat_id
		}
	if bDEBUG: # remove this if you have correct video files sent as videos (not files)
		if duration == None: duration = 5
	if duration != None:
		head_data.update([("duration", duration)])
	if caption != None:
		head_data.update([("caption", caption)])
	if reply_to_message_id != None:
		head_data.update([("reply_to_message_id", reply_to_message_id)])
	if reply_markup != None:
		head_data.update([("reply_markup", reply_markup)])
	if existing_file:
		head_data.update([("video", video)])
		req = requests.get(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/sendVideo"), params = head_data)
	else:
		_file = {'video': (video, open(video, 'rb'))}
		req = requests.get(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/sendVideo"), params = head_data, files = _file)
	if (req.status_code != 200):
		print("** sendVideo(): Error %s\n*** %s" % (req.status_code, req.content))
		return None
	else:
		req_json = req.json()
		if bDEBUG: print("** sendVideo(): Success\n*** Answer:%s" % ("%s" % req_json).encode("utf-8"))
		returned_message = telegram_classes_Message(req_json["result"])
		return {"file_id": returned_message.video["file_id"], "message_id": returned_message.message_id}
#
def telegram_bot_answerInlineQuery(inline_query_id, results, cache_time = None, is_personal = None, next_offset = None):
	req_data = {
		"inline_query_id": int(inline_query_id),
		"results": json.dumps(results)
		}
	if cache_time != None:
		req_data.update([("cache_time", cache_time)])
	if is_personal != None:
		req_data.update([("is_personal", is_personal)])
	if next_offset != None:
		req_data.update([("next_offset", next_offset)])
	print("-- telegram_bot_answerInlineQuery()\n\tData = %s" % req_data)
	req = requests.post(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/answerInlineQuery"), data = req_data)
	if (req.status_code != 200):
		print("-- answerInlineQuery(): Error %s (::%s)" % (req.status_code, req.content))
	else:
		req_json = req.json()
		print("** answerInlineQuery():\n\tRequest sent. Result: %s" % req_json)
		#TODO: True is returned on success.
#
def telegram_bot_createInlineQueryResult_article(id, title, message_text, parse_mode = None, disable_web_page_preview = None, url = None, hide_url = None, description = None, thumb_url = None, thumb_width = None, thumb_height = None):
	type = "article"
	r = {
		"type": type,
		"id": id,
		"title": title,
		"message_text": message_text
		}
	if parse_mode != None:
		r.update([("parse_mode", parse_mode)])
	if disable_web_page_preview != None:
		r.update([("disable_web_page_preview", disable_web_page_preview)])
	if url != None:
		r.update([("url", url)])
	if hide_url != None:
		r.update([("hide_url", hide_url)])
	if description != None:
		r.update([("description", description)])		
	if thumb_url != None:
		r.update([("thumb_url", thumb_url)])
	if thumb_width != None:
		r.update([("thumb_width", thumb_width)])
	if thumb_height != None:
		r.update([("thumb_height", thumb_height)])
	return r
#---------------------------------------------------------------
# Message handles
#---------------------------------------------------------------
def telegram_bot_handle_message_text(message):
	_to = ""; _from = ""
	_text = message.text
	if message.sender.id != message.chat.id:
		_to = "@%s" % message.chat.title
	if telegram_types.get("forward_from") in message.type:
		_from = " [fwd: %s]" % message.forward_from.first_name
		if _text[0] == "<":
			_from = " [fwd: %s]" % _text[1:].split(">")[0]
			_text = ' '.join(_text[1:].split(">")[1:])[1:]
	print("[#%s]\t<%s(%s)%s%s> %s" % (message.message_id, message.sender.first_name.encode("utf-8"), message.sender.id, _to.encode("utf-8"), _from, _text.encode("UTF-8")))
	# Handle commands
	# user / chat / command / arguments(full_text)
	if len(_text) > 2 and _text[0] == "/":
		if _to == "":
			# Privé
			_command = _text[1:].split()[0]
			_args = _text[1:].split()[1:]
			print("--- Private command is: %s | With args: %s" % (_command.encode("utf-8"), ((' '.join(_args)).encode("utf-8")).split()))
			telegram_bot_command_user(_command, _args, message.sender, message.message_id)
		elif ("@" + telegram_bot_info.username.lower()) in _text.lower():
			# Groupe + Hilight
			# /command@MyBot
			_bot_username = _text[1:].split('@')[1][:len(telegram_bot_info.username)].lower()
			#print("_bot_username = %s" % _bot_username)
			if _bot_username.lower() == telegram_bot_info.username.lower():
				_command = _text[1:].split('@')[0]
				_args = (" ".join(_text[1:].split('@')[1:])[len(_bot_username):]).split()
				print("--- Group command is: %s | With args: %s" % (_command.encode("utf-8"), ((' '.join(_args)).encode("utf-8")).split()))
				telegram_bot_command_user(_command, _args, message.sender, message.message_id, message.chat)
		else:
			# Group /without hilight
			# /command [args]
			_command = _text[1:].split()[0]
			_args = _text[1:].split()[1:]
			print("--- Group command is: %s | With args: %s" % (_command.encode("utf-8"), ((' '.join(_args)).encode("utf-8")).split()))
			telegram_bot_command_user(_command, _args, message.sender, message.message_id, message.chat)
#
def telegram_bot_handle_message_chat_participant_new(message):
	print("[#%s]\t** %s joined group %s" % (message.message_id, message.new_chat_participant.first_name, message.chat.title.encode("utf-8")))
	if message.new_chat_participant.id != telegram_bot_info.id:
		telegram_bot_send_message(message.chat.id, "Hello, %s." % message.new_chat_participant.first_name, reply_to_message_id = message.message_id)
	else:
		telegram_bot_send_message(message.chat.id, "Salut tout le monde ! [chat #%s]" % message.chat.id, reply_to_message_id = message.message_id)
def telegram_bot_handle_message_chat_participant_left(message):
	print("[#%s]\t** %s left group %s" % (message.message_id, message.left_chat_participant.first_name, message.chat.title.encode("utf-8")))
	if message.left_chat_participant.id != telegram_bot_info.id:
		telegram_bot_send_message(message.chat.id, "Bye, %s." % message.left_chat_participant.first_name, reply_to_message_id = message.message_id)
def telegram_bot_handle_message_chat_title_new(message):
	print("[#%s]\t** Group %s changed title to ""%s""" % (message.message_id, message.chat.id, message.new_chat_title.encode("utf-8")))
def telegram_bot_handle_message_group_chat_created(message):
	print("[#%s]\t** Group chat ""%s"" created" % (message.message_id, message.chat.title.encode("utf-8")))
	#telegram_bot_send_message(message.chat.id, "Salut tout le monde !")
# Added 2016-02-05
def telegram_bot_handle_message_channel_chat_created(message):
	print("[#%s]\t** Channel chat ""%s"" created" % (message.message_id, message.chat.title.encode("utf-8")))
	#telegram_bot_send_message(message.chat.id, "Salut tout le monde !")
#
def telegram_bot_handle_message_audio(message):
	print("Sorry, I can't hear audio for now.")
#
def telegram_bot_handle_message_video(message):
	if bDEBUG: telegram_bot_send_message(message.chat.id, "*Video* received.", parse_mode = "Markdown", reply_to_message_id = message.message_id)
	if message.chat_type == "private":
		user_id = message.chat.id
		# Video Label Bot
		if user_id in config["telegram_params"]["admins"]:
			VideoLabelBot(message, isVideo = True)
#
def telegram_bot_handle_message_document(message):
	if bDEBUG: telegram_bot_send_message(message.chat.id, "*File* received.", parse_mode = "Markdown", reply_to_message_id = message.message_id)
	if message.chat_type == "private":
		user_id = message.chat.id
		# Video Label Bot
		if user_id in config["telegram_params"]["admins"]:
			VideoLabelBot(message)
#
VideoLabel = {
	"file_id": None,
	"file_path": None,
	"file_ready": False,
	"caption": None,
	"ready": False,
	"send": False
}
# Remove markdown characters
def Markdown_RemoveChars(string):
	Markdown_chars = {
		"`": {
			"description": "code"
		},
		"*": {
			"description": "bold"
		},
		"_": {
			"description": "italic"
		},
		"[": {
			"description": "link_start"
		}
	}
	_string = string
	for char in Markdown_chars.keys():
		_string = _string.replace(char, "\\%s" % char)
	return _string
#
def VideoLabelBot_Send():
	isVideo = VideoLabel["isVideo"]
	channel = VideoLabel["channel"]
	message_id = VideoLabel["message_id"]
	user_id = VideoLabel["user_id"]
	if isVideo:
		sendVideo = telegram_bot_sendVideo(channel, VideoLabel["file_id"], existing_file = True, caption = VideoLabel["caption"], duration = VideoLabel["duration"])
		if not sendVideo:
			telegram_bot_send_message(user_id, "*Error*\nCan't *re*send video.\n_Something went wrong during the process._", parse_mode = "Markdown", reply_to_message_id = message_id)
		else:
			print("* Video resent.")
			for key in VideoLabel.keys():
				VideoLabel.update([(key, None)])
			telegram_bot_send_message(user_id, "*Done!*\nCheck: %s." % Markdown_RemoveChars(channel), parse_mode = "Markdown", reply_to_message_id = message_id)
	else:
		sendVideo = telegram_bot_sendVideo(channel, VideoLabel["file_local_path"], existing_file = False, caption = VideoLabel["caption"])
		if not sendVideo:
			telegram_bot_send_message(user_id, "*Error*\nCan't send video file.\n_Something went wrong during upload process._", parse_mode = "Markdown", reply_to_message_id = message_id)
		else:
			print("* Video received and uploaded.")
			for key in VideoLabel.keys():
				VideoLabel.update([(key, None)])
			telegram_bot_send_message(user_id, "*Done!*\nCheck: %s." % Markdown_RemoveChars(channel), parse_mode = "Markdown", reply_to_message_id = message_id)
			DeleteFile(file_local_path)
#
def VideoLabelBot(message, isVideo = False):
	global VideoLabel
	user_id = message.chat.id
	VideoLabel.update([("user_id", user_id)])
	message_id = message.message_id
	VideoLabel.update([("message_id", message_id)])
	channel = config["telegram_params"]["channels"][0]
	VideoLabel.update([("channel", channel)])
	if VideoLabel["caption"]:
		if isVideo:
			VideoLabel.update([("isVideo", True)])
			file_id = message.video["file_id"]
			VideoLabel.update([("file_id", file_id)])
			duration = message.video["duration"]
			VideoLabel.update([("duration", duration)])
			thumb = message.video["thumb"]
			VideoLabel.update([("thumb", thumb)])
			if bDEBUG: telegram_bot_send_message(user_id, "*Video* received.\n`file_id = %s`" % file_id, parse_mode = "Markdown", reply_to_message_id = message_id)
			VideoLabel.update([("ready", True)])
			if VideoLabel["send"]: #HERE
				VideoLabelBot_Send()
			else:
				sendVideo = telegram_bot_sendVideo(user_id, file_id, existing_file = True, caption = VideoLabel["caption"], duration = duration)
				telegram_bot_send_message(user_id, "*Please, check if everything is okay.*\nUse /send to send video to %s.\nUse /cancel to cancel current video or just send another video to replace it." % Markdown_RemoveChars(channel), parse_mode = "Markdown", reply_to_message_id = sendVideo["message_id"])
		else:
			VideoLabel.update([("isVideo", False)])
			file_id = message.document["file_id"]
			VideoLabel.update([("file_id", file_id)])
			file_name = message.document["file_name"]
			VideoLabel.update([("file_name", file_name)])
			if bDEBUG: telegram_bot_send_message(channel, "*File* received.\n`file_id = %s`" % file_id, parse_mode = "Markdown", reply_to_message_id = message_id)			
			# Get path to the file
			file_remote = telegram_bot_getFile(file_id)
			if file_remote["success"]:
				# download file
				VideoLabel.update([("file_path", "https://api.telegram.org/file/bot%s/%s" % (config["telegram_params"]["token"], file_remote["file_path"]))])
				if bDEBUG: telegram_bot_send_message(user_id, "Ready to download remote file `%s`, in order to upload it." % file_remote["file_path"], parse_mode = "Markdown", reply_to_message_id = message_id)
				file_local = DownloadFile(VideoLabel["file_path"])
				if file_local["success"]:
					file_local_path = file_local["file_path"]
					VideoLabel.update([("file_local_path", file_local_path)])
					VideoLabel.update([("ready", True)])
					if VideoLabel["send"]:
						VideoLabelBot_Send()
					else:
						sendVideo = telegram_bot_sendVideo(user_id, file_local_path, existing_file = True, caption = VideoLabel["caption"])
						telegram_bot_send_message(user_id, "*Please, check if everything is okay.*\nUse /send to send video to %s.\nUse /cancel to cancel current video or just send another video to replace it." % Markdown_RemoveChars(channel), parse_mode = "Markdown", reply_to_message_id = sendVideo["message_id"])
						# TODO: The bot shouldn't upload twice.
				else:
					telegram_bot_send_message(user_id, "*Error*: Can not download file from path `%s`.\n_Problem during the download process._" % file_remote["file_path"], parse_mode = "Markdown", reply_to_message_id = message_id)
			else:
				telegram_bot_send_message(user_id, "*Error*: Can not download file `%s`.\n_No download link received._" % file_id, parse_mode = "Markdown", reply_to_message_id = message_id)	
	else:
		print("Can't do anything without a caption.")
		telegram_bot_send_message(user_id, "*Error*: Please, send a caption with `/video <caption>` first.", parse_mode = "Markdown", reply_to_message_id = message_id)
#
def telegram_bot_getFile(file_id):
	head_data = {
		"file_id": file_id
		}
	req = requests.get(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/getFile"), params = head_data)
	if (req.status_code != 200):
		print("-- getFile(): Error %s (::%s)" % (req.status_code, req.content))
		return {"success": False, "reason": "Error %s" % req.status_code}
	else:
		req_json = req.json()
		if bDEBUG: print("** getFile():\n\tResult: %s" % req_json)
		req_json_result = req_json["result"]
		_file_id = req_json_result["file_id"]
		_file_size = None
		_file_path = None
		if "file_size" in req_json_result: _file_size = req_json_result["file_size"]
		if "file_path" in req_json_result: _file_path = req_json_result["file_path"]
		# TODO: Check if file_id is the same as requested
		# TODO: Add file_size to returned answer on success
		if not _file_path:
			return {"success": False, "reason": "No file returned. Can't download. Sorry"}
		else:
			return {"success": True, "file_path": _file_path}
#
def telegram_bot_handle_message_picture(message):
	print("Sorry, I can't see pictures for now.")
def telegram_bot_handle_message_sticker(message):
	print("Sorry, I don't care about stickers for now.")
def telegram_bot_handle_message_contact(message):
	print("Sorry, I have nothing to do with this contact for now.")
def telegram_bot_handle_message_location(message):
	print("Sorry, I can't change location, nor look at it for now.")
def telegram_bot_handle_message_chat_photo_new(message):
	print("Sorry, I can't see chat photos for now.")
def telegram_bot_handle_message_chat_photo_delete(message):
	print("Sorry, I don't care about photos for now.")
#
def telegram_bot_command_about(context, original_message_id):
	# Fournit le texte d'à propos
	telegram_bot_send_message(context, "@%(name)s\n%(name)s version %(version)s\nPar @Jahus.\nSay /help to learn how to use the bot." % {"name": __name__, "version": __version__}, reply_to_message_id = original_message_id)
def telegram_bot_command_user(msg, args, user, original_message_id, chat = None):
	global PAUSE
	global HALT
	global VideoLabel
	if chat == None: chat = user
	cmd = msg.split()[0]
	# print("Received command '%s' with arguments '%s'." % (cmd, args))
	if cmd.lower() == "about":
		telegram_bot_command_about(chat.id, original_message_id)
	if cmd.lower() == "keskifichou":
		telegram_bot_send_message(chat.id, "Une vraie chaudasse !", reply_to_message_id = original_message_id)
	# Video Label Bot
	if cmd.lower() == "video" and user.id in config["telegram_params"]["admins"]:
		if len(args) == 0:
			telegram_bot_send_message(chat.id, "Please, send caption before uploading file. Use `/video <caption>`.", reply_to_message_id = original_message_id, parse_mode = "Markdown")
		else:
			caption = ' '.join(args)
			caption = caption.replace("{n}", "\n")
			if len(caption) > 140:
				telegram_bot_send_message(chat.id, "Your caption is too long. Use `/video <caption>` to send a new one.", reply_to_message_id = original_message_id, parse_mode = "Markdown")
			else:
				VideoLabel.update([("caption", caption)])
				telegram_bot_send_message(chat.id, "Now, send me the video or the file you want published as a video with caption:\n*%s*" % caption, reply_to_message_id = original_message_id, parse_mode = "Markdown")
	if cmd.lower() == "cancel" and user.id in config["telegram_params"]["admins"]:
		if VideoLabel["ready"]:
			VideoLabel.update([("ready", False)])
			telegram_bot_send_message(chat.id, "Video canceled. Use /cancel if you want to change caption.\nElse, send file or video you want published with caption:\n*%s*" % VideoLabel["caption"], reply_to_message_id = original_message_id, parse_mode = "Markdown")
		elif VideoLabel["caption"]:
			VideoLabel.update([("caption", None)])
			telegram_bot_send_message(chat.id, "Process canceled. Use `/video <caption>` if you want to publish a video.", reply_to_message_id = original_message_id, parse_mode = "Markdown")
		VideoLabel.update([("send", False)])		
	if cmd.lower() == "send":
		if not VideoLabel["ready"]:
			if VideoLabel["caption"]:
				telegram_bot_send_message(chat.id, "No ready video to send.\nSend me the file or video you want published as a video with caption:\n*%s*" % caption, reply_to_message_id = original_message_id, parse_mode = "Markdown")
			else:
				telegram_bot_send_message(chat.id, "No ready video to send. Use `/video <caption>` if you want to publish a video.\nUse /cancel to cancel current process.", reply_to_message_id = original_message_id, parse_mode = "Markdown")
		else:
			VideoLabel.update([("send", True)])
			if bDEBUG: telegram_bot_send_message(chat.id, "Sending...", reply_to_message_id = original_message_id, parse_mode = "Markdown")
			VideoLabelBot_Send()
#
telegram_bot_get_bot_info()
print("EoF@offset: %s" % telegram_bot_offset)
#
#---------------------------------------------------------------
# Get500pxBot - Legacy
#---------------------------------------------------------------
#
def DownloadFile(url, name = None, name_alt = None):
	print("* DownloadFile(): Downloading file '%s'..." % url.encode("utf-8"))
	if name != None:
		_FileName = name
	elif name_alt != None:
		_FileName = name_alt
	else:
		_FileName = url.split('/')[-1]
	try:
		# Downloading file...
		req = requests.get(url = url, stream = True)
		try:
			with open(_FileName, 'wb') as _File:
				for chunk in req.iter_content(chunk_size = 512):
					if chunk:
						_File.write(chunk)
			print("* DownloadFile(): File downloaded.")
			return {"success": True, "file_path": _FileName}
		except:
			try:
				with open(name_alt, 'wb') as _File:
					for chunk in req.iter_content(chunk_size = 512):
						if chunk:
							_File.write(chunk)
					print("* DownloadFile(): File downloaded.")
					return {"success": True, "file_path": name_alt}
			except:
				print("* DownloadFile(): ERROR Can't create destination file.")
				return {"success": False, "reason": "Can't create destination file."}
	except:
		print("* DownloadFile(): ERROR Can't download file.")
		return {"success": False, "reason": "Can't download file."}
#
#---------------------------------------------------------------
# SCRIPT
#---------------------------------------------------------------
if bDEBUG:
	print("* script is ok to load!")
#
# Turn around and check for new messages each timeout time
timeout = config.get("telegram_params").get("timeout")
timeout_first = config.get("telegram_params").get("timeout_first")
def logger_loop():
	while not HALT:
		try:
			print("* logger_loop(): -- time: %s" % (time.strftime("%Y-%m-%d @ %H-%M-%S", time.gmtime())))
			telegram_bot_get_updates()
		except:
			print("<> ERROR <> logger_loop(): -- time: %s" % (time.strftime("%Y-%m-%d @ %H-%M-%S", time.gmtime())))
		print("* logger_loop(): Waiting %ss" % timeout)
		time.sleep(float(timeout))
	telegram_bot_get_updates()
#
# Running script
logger_loop()
#
# EXITTING
print("* Script terminated!")
#EOF