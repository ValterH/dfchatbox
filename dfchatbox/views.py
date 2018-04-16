from django.shortcuts import render
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.core import serializers

import re
import imgkit
import string
import random
from PIL import Image
from lxml.html import fromstring
import json
from bs4 import BeautifulSoup
import urllib3
import apiai
import requests


# Create your views here.
# -*- coding: utf-8 -*-

@require_http_methods(['POST','GET'])
def index(request):
	if request.method == 'POST':
		message = request.POST['message']
		#print("user input: ", message)

		url = "http://translate.dis-apps.ijs.si/translate?sentence=" + message

		response = requests.get(url)
		translation = response.text[1:-3]

		if translation != "":
			message = translation

		#print(message)

		CLIENT_ACCESS_TOKEN = "631305ebeec449618ddeeb2f96a681e9" 

		contexts = []

		ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

		request = ai.text_request()
		request.session_id = "123333"
		request.lang = 'en'
		request.contexts = contexts
		request.query = message

		data = request.getresponse().read().decode('utf-8')

		answer_json = json.loads(data)

		#print(answer_json)

		text_answer = answer_json['result']['fulfillment']['messages'][0]['speech']

		data = ""
		response_type = ""
		url = ""

		if 'data' in answer_json['result']['fulfillment']:
		    data = answer_json['result']['fulfillment']['data']['data']
		    response_type = answer_json['result']['fulfillment']['data']['responseType']
		    url = answer_json['result']['fulfillment']['data']['url']
		    if url[:5] != "https":
		    	url = "https:" + url[5:]

		    print("RESPONSE TYPE: ",url)

		#print("data: ",data)

		return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}","url":"{3}"}}'.format(text_answer,response_type,data,url))
	else:
		return render(request,'dfchatbox/index.html')
	

@require_http_methods(['POST'])
def check_links(request):
	if request.method == 'POST':
		message = request.POST['message']

		urls = re.findall("((https://www|http://www|www\.|http://|https://).*?(?=(www\.|http://|https://|$)))", message)

		print("These are the urls: ", urls)

		if len(urls) != 0:
			url = urls[0][0]

			print("We'll check this url: ", url)

			html = requests.get(url)

			# soup = BeautifulSoup(html.text,"lxml")

			# file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20)) + ".html"
			# file = "dfchatbox/static/dfchatbox/data/" + file_name

			# with open(file, "w", encoding='utf8') as f:
			# 	f.write(str(soup))

			tree = fromstring(html.content)
			title = tree.findtext('.//title')
			title = title.replace('"','\\"')

			image_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20)) + ".jpg"
			image_path = "dfchatbox/static/dfchatbox/img/" + image_name

			#config = imgkit.config(wkhtmltoimage='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltoimage.exe')
			options = {'zoom': '1.2', 'width': '500', 'height': '500'}
			#imgkit.from_url(url,image_path,config=config,options=options)
			imgkit.from_url(url,image_path,options=options)
		#	imgkit.from_file(file,image_path,config=config,options=options)

			img = Image.open(image_path)

			return HttpResponse('{{"url":"{0}", "data":"{1}", "image_name":"{2}"}}'.format(url,title,image_name))

		else:
			return HttpResponse(urls)

#stara metoda za komunikacijo z dialogflowom

# @require_http_methods(['POST','GET'])
# def index(request):
#     if request.method == 'POST':
#         message = request.POST['message']

#         dialogflow = Dialogflow(**settings.DIALOGFLOW)
        
#         answer = dialogflow.text_request(message)
        
#         print("The answer: ", answer)

#         if len(answer) == 0 or answer[0][-6:] == "again?":
#         	print("Agent did not respond")
#         	response = [{'option': 'How are you?','6': 7},{'option': 'Do you like the weather?','6': 7}]
#         	data = [msg['option'] for msg in response]
#         	data = json.dumps(data)
#         	return HttpResponse(data)
#         	#return HttpResponse("*Agent did not answer*")
#         else:
#         	return HttpResponse(answer[0])
    
#     else: 
#         return render(request,'dfchatbox/index.html')



        
        
        