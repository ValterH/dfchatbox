from django.shortcuts import render
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

import re
import imgkit
import string
import random
from PIL import Image
from lxml.html import fromstring
from lxml import etree
import json
from bs4 import BeautifulSoup
import urllib3
import apiai
import requests
import base64
from datetime import datetime
from dfchatbox.models import Procedure
from haystack.query import SearchQuerySet

# Create your views here.
# -*- coding: utf-8 -*-

@require_http_methods(['POST','GET'])
def index(request):
	if request.method == 'POST':
		message = request.POST['message']
		sessionID = request.POST['sessionID']

		print("*****SESSION ID*****   ",sessionID)
		if(message=="pomoč"):
			help ="<b>Da vam pomagam najti razpoložljivo storitev potrebujem naslednje informacije:<br><em>-kateri poseg iščete (npr. rentgen kolena)<br><em>-v kateri regiji iščete (npr. Gorenjska)<br><em>-kako nujno potrebujete poseg (npr. redno)<br><br><small>Vendar ne skrbite za regijo in nujnost vas bom povprašal sam.<br>Vi mi samo povejte katero storitev iščete."
			return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}"}}'.format(help,"none",[]))
		messageSLO = message
		if not hasNumbers(message) or message.find("24")>-1:
			message=translate(message)

		#print("user input: ", message)

		# url = "http://translation-api.docker-e9.ijs.si/translate?sentence=" + message

		# response = requests.get(url)
		# translation = response.text[1:-3]

		# if translation != "":
		# 	message = translation

		# TODO:
		# prepoznavanje regije?

		print("message:",message)
		if (not hasNumbers(message) or message.find("24") > -1) and message.find("NONE") < 0 and message != "reset":
			if checkRegion(message):
				whoosh_data = findSLO(lemmatize(messageSLO))
				#print("SLO", whoosh_data)
				if(len(whoosh_data) < 2):
					whoosh_data = whoosh(message)
				#print(whoosh_data)
				if len(whoosh_data) > 1:
					return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}"}}'.format("Ste mislili:","procedures",whoosh_data))
				else:
					message+= " NONE"
		print(message)

		#THINKEHR
		#CLIENT_ACCESS_TOKEN = "631305ebeec449618ddeeb2f96a681e9"
		#WAITING LINES
		CLIENT_ACCESS_TOKEN = "15bddeda0b5246cba6cd27fcd67576a3"
		#MyEHR
		#CLIENT_ACCESS_TOKEN = "7f7cb0e7be2e4b83b08b7106485a2078"

		contexts = []

		ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
		OGrequest = request
		request = ai.text_request()
		request.session_id = sessionID
		request.lang = 'en'
		request.contexts = contexts
		request.query = message

		data = request.getresponse().read().decode('utf-8')

		answer_json = json.loads(data)

		print(answer_json)

		text_answer = answer_json['result']['fulfillment']['messages'][0]['speech']
		
		groups = []
		procedure =""
		if not 'procedure' in OGrequest.session and message != 'reset':
			if not 'group' in OGrequest.session:
				try: 
					groups = answer_json['result']['parameters']['group']
				except:
					print('No group')
			try: 
				procedure = answer_json['result']['parameters']['procedure']
			except:
				print('No procedure')
		if procedure:
			OGrequest.session['procedure']=1
			procedures =Procedure.objects.all()				
			for pro in procedures:
				if pro.procedure_id == procedure:
					p = pro
					break
			text_answer = "Našel sem <b>" + pro.nameSLO + "</b><br>" + text_answer
		else:
			if groups:
				OGrequest.session['group']=1
				if len(groups)>1:
					answer = text_answer
					text_answer = "Našel sem naslednje skupine posegov: "
					for group in groups:
						group = requests.get('http://translation-api.docker-e9.ijs.si/translate', params={'sentence':group,'fromLang':'en','toLang':'sl'}).text[1:-3]
						text_answer += "<br>-" + group
					text_answer += "<br>" + answer
				else:
					text_answer = "Našel sem skupino posegov <b>" + requests.get('http://translation-api.docker-e9.ijs.si/translate', params={'sentence':groups[0],'fromLang':'en','toLang':'sl'}).text[1:-3] + "</b><br>" + text_answer
			
			
		#text_answer = text_answer.replace('\\','\\\\')

		print(text_answer)

		data = ""
		response_type = ""
		url = ""

		if 'data' in answer_json['result']['fulfillment']:
		    data = answer_json['result']['fulfillment']['data']['data']
		    response_type = answer_json['result']['fulfillment']['data']['responseType']
		    print("RESPONSE TYPE: ",response_type)
		    url = answer_json['result']['fulfillment']['data']['url']
		    if url[:5] != "https":
		    	url = "https:" + url[5:]

		if response_type == "procedures":
			none={}
			none['name']="Nobeden izmed zgoraj naštetih"
			none['value']= "NONE"
			answer_json['result']['fulfillment']['data']['data'] = answer_json['result']['fulfillment']['data']['data'].append(none)


		if text_answer.find("Kako hitro potrebujete poseg?")>-1:
			urgencies = [{"name":"Redno","value":"normal"},{"name":"Hitro","value":"fast"},{"name":"Zelo hitro","value":"very fast"}]
			return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}"}}'.format(text_answer,"procedures",urgencies))

		if text_answer.find("V kateri regiji iščete?")>-1:
			print("A")
			regions = [{ "name": "Vse regije", "value": "all regions" }, { "name": "Gorenjska regija", "value": "Gorenjska" }, { "name": "Goriška regija", "value": "Goriska" }, { "name": "Jugovzhodna Slovenija", "value": "Southeast" }, { "name": "Koroška regija", "value": "Koroška" }, { "name": "Obalno-kraška regija", "value": "Obalno-Kraska" }, { "name": "Osrednjeslovenska regija", "value": "Ljubljana" }, { "name": "Podravska regija", "value": "Podravska" }, { "name": "Pomurska regija", "value": "Pomurje" }, { "name": "Posavska regija", "value": "Posavska region" }, { "name": "Primorsko-notranjska regija", "value": "Primorsko-Inner" }, { "name": "Savinjska regija", "value": "Savinjska" }, { "name": "Zasavska regija", "value": "Zasavska" }]
			return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}"}}'.format(text_answer,"procedures",regions))

		if text_answer == "Poseg, ki ga iščete pod trenutnimi pogoji ni na voljo. Poskusite iskati v drugih regijah ali pod drugo nujnostjo." and not 'regions' in OGrequest.session and answer_json['result']['parameters']['region'] != "A":
			OGrequest.session['regions']=1
			text_answer = "Poseg v vaši regiji trenutno ni na voljo. Ali želite, da iščem v vseh regijah?"
			value="A " + answer_json['result']['parameters']['urgency'] + " " + answer_json['result']['parameters']['procedure']
			data = [{"name":"DA", "value":value},{"name":"NE","value":"reset"}]
			response_type="procedures"

		if text_answer.find("Našel sem naslednje posege...")>-1 or text_answer == "Poseg, ki ga iščete pod trenutnimi pogoji ni na voljo. Poskusite iskati v drugih regijah ali pod drugo nujnostjo." or text_answer == "Prosim ponovno začnite z iskanjem":
			if 'regions' in OGrequest.session:
				del OGrequest.session['regions']
			if 'procedure' in OGrequest.session:
				del OGrequest.session['procedure']
			if 'group' in OGrequest.session:
				del OGrequest.session['group']
			OGrequest.session.modified = True
			if text_answer == "Poseg, ki ga iščete pod trenutnimi pogoji ni na voljo. Poskusite iskati v drugih regijah ali pod drugo nujnostjo." and answer_json['result']['parameters']['region'] == "A":
				text_answer = "Žal zgleda, da poseg ki ga iščete ni na voljo v nobeni izmed objavljenih ustanov."
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

			img = Image.open(image_path)

			return HttpResponse('{{"url":"{0}", "data":"{1}", "image_name":"{2}"}}'.format(url,title,image_name))

		else:
			return HttpResponse(urls)

@require_http_methods(['GET'])
def entry_tree(request,data):
	return render(request,'dfchatbox/tree.html',{data:data})


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

############################################################## WEBHOOK ##################################################################

@csrf_exempt
def webhook(request):

	answer_json = json.loads(request.body)
	
	print("=========== WEBHOOK =============")

	parameter_action = answer_json['result']['action']
	json_response = {}
	response_data = {}
	answer = "Prosim ponovno postavite zahtevo."

	if parameter_action == "labResults":
		print("labResults")
		json_response = getLabResultsData(answer_json)
	if parameter_action == "patientInfo":
		print("patientInfo")
		json_response = getPatientInfoData(answer_json)
	if parameter_action == "ECGResults":
		print("ECGResults")
		json_response = getECGResultsData(answer_json)
	if parameter_action == "allEntries":
		print("allEntries")
		json_response = getAllEntries(answer_json)
		response_data['ehrid'] = json_response['ehrid']
		del json_response['ehrid']
	if parameter_action == "getEntry":
		print("getEntry")
		json_response = getEntryData(answer_json)
		print(json_response)

	answer = json_response['answer']
	del json_response['answer']
	response_data['speech'] = answer
	response_data['displayText'] = answer
	response_data['data'] = json_response
	response_data['source'] = "thinkEHR"
	print("=========== END WEBHOOK =============")
	return HttpResponse(
			json.dumps(response_data, indent=4),
			content_type="application/json"
			)

def getPatientInfoData(answer_json):

	baseUrl = 'https://rest.ehrscape.com/rest/v1'
	base = base64.b64encode(b'ales.tavcar@ijs.si:ehrscape4alestavcar')
	authorization = "Basic " + base.decode()

	queryUrl = baseUrl + "/demographics/party/query"

	searchData = []
	json_response = {"responseType": "userInfo"}
	json_object = {}

	parameter_name =answer_json['result']['parameters']['given-name']
	parameter_last_name =answer_json['result']['parameters']['last-name']

	if parameter_name != "":
		searchData.append({"key": "firstNames", "value": parameter_name})
	if parameter_last_name != "":
		searchData.append({"key": "lastNames", "value": parameter_last_name})

	print("queryUrl: ", queryUrl)
	print("searchData: ", searchData)

	r = requests.post(queryUrl, data=json.dumps(searchData), headers={"Authorization": authorization, 'content-type': 'application/json'})

	if r.status_code == 200:
		js = json.loads(r.text)
		json_object["name"] = js['parties'][0]['firstNames']
		json_object["lastname"] = js['parties'][0]['lastNames']
		json_object["gender"] = js['parties'][0]['gender']
		json_object["dateofbirth"] = js['parties'][0]['dateOfBirth']

		answer = "Za podano ime sem našel sledeče podatke."
	else:
		answer = "Za podano ime nisem našel ustreznih vnosov."	


	json_response['answer'] = answer
	json_response['data'] = json_object
	json_response['url'] = "http://www.rtvslo.si"

	return json_response

def getLabResultsData(answer_json):
	print(answer_json)

	baseUrl = 'https://rest.ehrscape.com/rest/v1'
	#ehrId = 'd8dcc924-edaf-4df5-8b84-e9e6d0ec590f'
	ehrId = ''
	base = base64.b64encode(b'ales.tavcar@ijs.si:ehrscape4alestavcar')
	authorization = "Basic " + base.decode()

	# Match the action -> provide correct data
	parameter_action = answer_json['result']['action']
	json_response = {"responseType": "list"}
	searchData = []
	json_lab_results = []
	json_object = {} 

	# Obtain ehrID of patient from name
	queryUrl = baseUrl + "/demographics/party/query"

	parameter_name =answer_json['result']['parameters']['given-name']
	parameter_last_name =answer_json['result']['parameters']['last-name']

	if parameter_name != "":
		searchData.append({"key": "firstNames", "value": parameter_name})
	if parameter_last_name != "":
		searchData.append({"key": "lastNames", "value": parameter_last_name})

	r = requests.post(queryUrl, data=json.dumps(searchData), headers={"Authorization": authorization, 'content-type': 'application/json'})

	if r.status_code == 200:
		js = json.loads(r.text)
		ehrId = js['parties'][0]['partyAdditionalInfo'][0]['value']
		print("Found ehrid "+ehrId+" for user "+parameter_name+" "+parameter_last_name)
		answ_part = "Za pacienta "+parameter_name+" "+parameter_last_name

	#Use provided ehrid
	parameter_ehrid =answer_json['result']['parameters']['ehrid']
	if parameter_ehrid != "":
		ehrId = str(parameter_ehrid)
		answ_part = "Za ehrid "+ehrId

	#User wants to see lab results for a specific date or date period.
	if ehrId != '':
		parameter_date_range =answer_json['result']['parameters']['date-period']
		parameter_date =answer_json['result']['parameters']['date']
		queryUrl = baseUrl + "/view/"+ehrId+"/labs"
		r = requests.get(queryUrl, headers={"Authorization": authorization})
		js = json.loads(r.text)

		answer = "Za podan datum ni zabeleženih rezultatov laboratorijskih preiskav."
		if parameter_date_range != "":
			dateFrom  = datetime.strptime(parameter_date_range.split("/")[0], '%Y-%M-%d')
			dateTo  = datetime.strptime(parameter_date_range.split("/")[1], '%Y-%M-%d')

			for lab in js:
				datetime_object = datetime.strptime(lab['time'].split('T')[0], '%Y-%M-%d')
				if dateFrom <= datetime_object <= dateTo:
					print(lab['name']+" = "+lab['name']+" time: "+str(datetime_object))
					json_object['name'] = lab['name']
					json_object['value'] = str(lab['value'])+" "+lab['unit']
					json_object['date'] = str(datetime_object)
					json_lab_results.append(json_object)
					json_object = {}
			if json_lab_results:	
				answer = answ_part + " in podani casovni okvir sem nasel sledece izvide laboratorijskih preiskav:"
		elif parameter_date != "":
			print(parameter_date)
			dateFrom  = datetime.strptime(parameter_date, '%Y-%M-%d')
			dateTo  = dateFrom
			for lab in js:
				datetime_object = datetime.strptime(lab['time'].split('T')[0], '%Y-%M-%d')
				if dateFrom <= datetime_object <= dateTo:
					print(lab['name']+" = "+lab['name']+" time: "+str(datetime_object))
					json_object['name'] = lab['name']
					json_object['value'] = str(lab['value'])+" "+lab['unit']
					json_object['date'] = str(datetime_object)
					json_lab_results.append(json_object)
					json_object = {}
			if json_lab_results:	
				answer = answ_part + " in podan datum "+str(parameter_date)+" sem nasel sledece laboratorijske izvide:"
		else:
			for lab in js:
				datetime_object = datetime.strptime(lab['time'].split('T')[0], '%Y-%M-%d')
				json_object['name'] = lab['name']
				json_object['value'] = str(lab['value'])+" "+lab['unit']
				json_object['date'] = str(datetime_object)
				json_lab_results.append(json_object)
				json_object = {}
				if json_lab_results:	
					answer = answ_part + " sem nasel sledece laboratorijske izvide:"
	else: 
		answer = "Za podanega pacienta nisem nasel podatkov v sistemu."
	# Generate the JSON response
	json_response['answer'] = answer
	json_response['data'] = json_lab_results
	json_response['url'] = "http://www.rtvslo.si"

	return json_response

def getECGResultsData(answer_json):
	#print(answer_json)

	baseUrl = 'https://rest.ehrscape.com/rest/v1'
	ehrId = ''
	base = base64.b64encode(b'ales.tavcar@ijs.si:ehrscape4alestavcar')
	authorization = "Basic " + base.decode()

	# Match the action -> provide correct data
	parameter_action = answer_json['result']['action']
	json_response = {"responseType": "list"}
	searchData = []
	json_lab_results = []
	json_object = {} 

	# Obtain ehrID of patient from name
	queryUrl = baseUrl + "/demographics/party/query"

	parameter_name =answer_json['result']['parameters']['given-name']
	parameter_last_name =answer_json['result']['parameters']['last-name']

	if parameter_name != "":
		searchData.append({"key": "firstNames", "value": parameter_name})
	if parameter_last_name != "":
		searchData.append({"key": "lastNames", "value": parameter_last_name})

	r = requests.post(queryUrl, data=json.dumps(searchData), headers={"Authorization": authorization, 'content-type': 'application/json'})

	if r.status_code == 200:
		js = json.loads(r.text)
		ehrId = js['parties'][0]['partyAdditionalInfo'][0]['value']
		print("Found ehrid "+ehrId+" for user "+parameter_name+" "+parameter_last_name)
		answ_part = "Za pacienta "+parameter_name+" "+parameter_last_name

	#Use provided ehrid
	parameter_ehrid =answer_json['result']['parameters']['ehrid']
	if parameter_ehrid != "":
		ehrId = str(parameter_ehrid)
		answ_part = "Za ehrid "+ehrId

	#User wants to see lab results for a specific date or date period.
	if ehrId != '':
		parameter_date_range =answer_json['result']['parameters']['date-period']
		parameter_date =answer_json['result']['parameters']['date']

		aql = "/query?aql=select a from EHR e[ehr_id/value='{}'] contains COMPOSITION a".format(ehrId)

		queryUrl = baseUrl + aql

		r = requests.get(queryUrl, headers={"Authorization": authorization,'content-type': 'application/json'})

		js = json.loads(r.text)
		js = js['resultSet']

		answer = "Za podan datum ni zabeleženih rezultatov EKG preiskav."

		if parameter_date_range != "":
			dateFrom  = datetime.strptime(parameter_date_range.split("/")[0], '%Y-%M-%d')
			dateTo  = datetime.strptime(parameter_date_range.split("/")[1], '%Y-%M-%d')

			for item in js:
				if item['#0']['archetype_details']['template_id']['value'] == "Measurement ECG Report":
					datetime_object = datetime.strptime(item['#0']['context']['start_time']['value'].split('T')[0], '%Y-%M-%d')

					if dateFrom <= datetime_object <= dateTo:
						#print(lab['name']+" = "+lab['name']+" time: "+str(datetime_object))
						#json_object['name'] = lab['name']
						json_object['start_time'] = str(datetime_object)
						json_object['setting'] = item['#0']['context']['setting']['value']
						json_lab_results.append(json_object)
						json_object = {}

			if json_lab_results:	
				answer = answ_part + " in podani casovni okvir sem nasel sledece izvide EKG preiskav:"

		elif parameter_date != "":
			print(parameter_date)
			dateFrom  = datetime.strptime(parameter_date, '%Y-%M-%d')
			dateTo  = dateFrom

			for item in js:
				if item['#0']['archetype_details']['template_id']['value'] == "Measurement ECG Report":
					datetime_object = datetime.strptime(item['#0']['context']['start_time']['value'].split('T')[0], '%Y-%M-%d')

					if dateFrom <= datetime_object <= dateTo:
						#print(lab['name']+" = "+lab['name']+" time: "+str(datetime_object))
						#json_object['name'] = lab['name']
						json_object['start_time'] = str(datetime_object)
						json_object['setting'] = item['#0']['context']['setting']['value']
						json_lab_results.append(json_object)
						json_object = {}

			if json_lab_results:	
				answer = answ_part + " in podan datum "+str(parameter_date)+" sem nasel sledece EKG izvide:"
		else:
			for item in js:
				if item['#0']['archetype_details']['template_id']['value'] == "Measurement ECG Report":
					datetime_object = datetime.strptime(item['#0']['context']['start_time']['value'].split('T')[0], '%Y-%M-%d')

					#json_object['name'] = lab['name']
					json_object['start_time'] = str(datetime_object)
					json_object['setting'] = item['#0']['context']['setting']['value']
					json_lab_results.append(json_object)
					json_object = {}

			if json_lab_results:	
				answer = answ_part + " sem nasel sledece EKG izvide:"
	else:
		answer = "Za podanega pacienta nisem nasel podatkov v sistemu."

	# Generate the JSON response
	json_response['answer'] = answer
	json_response['data'] = json_lab_results
	json_response['url'] = "http://www.rtvslo.si"

	return json_response

def getAllEntries(answer_json):
	print(answer_json)

	baseUrl = 'https://rest.ehrscape.com/rest/v1'
	ehrId = ''
	base = base64.b64encode(b'ales.tavcar@ijs.si:ehrscape4alestavcar')
	authorization = "Basic " + base.decode()

	# Match the action -> provide correct data
	parameter_action = answer_json['result']['action']
	json_response = {"responseType": "button"}
	searchData = []
	json_entries = []
	json_object = {} 

	# Obtain ehrID of patient from name
	queryUrl = baseUrl + "/demographics/party/query"

	parameter_name =answer_json['result']['parameters']['given-name']
	parameter_last_name =answer_json['result']['parameters']['last-name']

	if parameter_name != "":
		searchData.append({"key": "firstNames", "value": parameter_name})
	if parameter_last_name != "":
		searchData.append({"key": "lastNames", "value": parameter_last_name})

	r = requests.post(queryUrl, data=json.dumps(searchData), headers={"Authorization": authorization, 'content-type': 'application/json'})

	if r.status_code == 200:
		js = json.loads(r.text)
		ehrId = js['parties'][0]['partyAdditionalInfo'][0]['value']
		print("Found ehrid "+ehrId+" for user "+parameter_name+" "+parameter_last_name)
		answ_part = "Za pacienta "+parameter_name+" "+parameter_last_name

	#Use provided ehrid
	parameter_ehrid = answer_json['result']['parameters']['ehrid']

	if parameter_ehrid != "":
		ehrId = str(parameter_ehrid)

	if ehrId != '':
		json_response['ehrid'] = ehrId

		aql = "/query?aql=select a from EHR e[ehr_id/value='{}'] contains COMPOSITION a".format(ehrId)

		queryUrl = baseUrl + aql

		r = requests.get(queryUrl, headers={"Authorization": authorization,'content-type': 'application/json'})

		js = json.loads(r.text)
		js = js['resultSet']

		if not len(js):
			answer = "Podani pacient nima vpisov v sistemu."
		else:
			answer = "Za podanega pacienta sem našel naslednje vpise v sistemu:"

			for counter,item in enumerate(js):
				json_object['name'] = item['#0']['archetype_details']['template_id']['value']
				json_object['value'] = str(counter)
				json_entries.append(json_object)
				json_object = {}

	else: 
		answer = "Za podanega pacienta nisem nasel podatkov v sistemu."
		json_response['ehrid'] = ehrId
	# Generate the JSON response
	json_response['answer'] = answer
	json_response['data'] = json_entries
	json_response['url'] = "http://www.rtvslo.si"


	return json_response

def getEntryData(answer_json):
	baseUrl = 'https://rest.ehrscape.com/rest/v1'
	ehrId = ''
	base = base64.b64encode(b'ales.tavcar@ijs.si:ehrscape4alestavcar')
	authorization = "Basic " + base.decode()

	# Match the action -> provide correct data
	parameter_action = answer_json['result']['action']
	json_response = {"responseType": "entry"}
	searchData = []
	json_entries = []
	#json_object = {}

	number = answer_json['result']['contexts'][0]['parameters']['number']
	#ehrId = answer_json['result']['fulfillment']['data']['ehrid']

	queryUrl = baseUrl + "/demographics/party/query"

	parameter_name =answer_json['result']['contexts'][0]['parameters']['given-name']
	parameter_last_name =answer_json['result']['contexts'][0]['parameters']['last-name']

	if parameter_name != "":
		searchData.append({"key": "firstNames", "value": parameter_name})
	if parameter_last_name != "":
		searchData.append({"key": "lastNames", "value": parameter_last_name})

	r = requests.post(queryUrl, data=json.dumps(searchData), headers={"Authorization": authorization, 'content-type': 'application/json'})

	if r.status_code == 200:
		js = json.loads(r.text)
		ehrId = js['parties'][0]['partyAdditionalInfo'][0]['value']
		print("Found ehrid "+ehrId+" for user "+parameter_name+" "+parameter_last_name)
		answ_part = "Za pacienta "+parameter_name+" "+parameter_last_name

	#Use provided ehrid
	parameter_ehrid = answer_json['result']['parameters']['ehrid']

	if parameter_ehrid != "":
		ehrId = str(parameter_ehrid)

	if ehrId != '':
		aql = "/query?aql=select a from EHR e[ehr_id/value='{}'] contains COMPOSITION a".format(ehrId)

		queryUrl = baseUrl + aql

		r = requests.get(queryUrl, headers={"Authorization": authorization,'content-type': 'application/json'})

		js = json.loads(r.text)
		js = js['resultSet']

		if not len(js):
			answer = "Podani pacient nima vpisov v sistemu."
		elif int(number) >= len(js):
			answer = "Izbrani vpis ne obstaja."
		else:
			answer = "Našel sem podatke o vpisu."

			for counter,item in enumerate(js):
				print(counter,number)
				if counter == int(number):
					uid = item['#0']['uid']['value']

					queryUrl = baseUrl + "/composition/"

					queryUrl += uid

					r = requests.get(queryUrl, headers={"Authorization": authorization, 'content-type': 'application/json'})

					if r.status_code == 200:
						json_entries = json.loads(r.text)['composition']
						print(json_entries)
						json_response['tree_url'] = "/entry_tree/{}".format(str(data))
						break

					else:
						answer = "Prišlo je do napake. Prosim, poskusite ponovno."
						break


	else: 
		answer = "Prišlo je do napake. Prosim, poskusite ponovno."

	# Generate the JSON response
	json_response['answer'] = answer
	json_response['data'] = json_entries

	return json_response

@require_http_methods(['GET'])
def update_db(request):
	url = "https://cakalnedobe.ezdrav.si/Home/GetProcedures"
	procedures = json.loads(requests.get(url).text)
	print (len(procedures))
	Procedure.objects.all().delete()
	print(len(Procedure.objects.all()))
	for procedure in procedures:
		nameSLO=edit(procedure['Name'])
		nameENG=translate(nameSLO).lower()
		pid=procedure['Id']
		print("SLO:",nameSLO)
		lem =lemmatize(nameSLO)
		print("LEM:",lem)
		#print(nameENG)
		#print()
		new_procedure=Procedure(nameENG=nameENG, nameSLO=nameSLO, procedure_id=pid, lemma=lem)
		new_procedure.save()
	print(len(Procedure.objects.all()))
	return HttpResponse('Database Updated')

def edit(input):
	return input.replace(",","").replace("("," ").replace(")"," ").replace("-"," ").replace("/"," ")

def translate(input):
	url = "http://translation-api.docker-e9.ijs.si/translate?sentence="+input.replace(","," ")
	req = requests.get(url)
	if req.text == '{"errors": {"sentence": "Invalid text value provided"}}' or req.text[1:-3] == '':
		output=""
		words=input.split(" ")
		if(len(words)>1):
			for word in words:
				#print(word)
				word=word.replace('rad','like to')
				#print(word)
				if word:
					output+=translate(word)+" "
			return output
		return input
	return req.text[1:-3]

def standardize_input(input):
	input = input.lower()
	return input.replace('arm', 'hand').replace('operation','surgery').replace("'"," ").replace("x-ray","rtg")

def standardize_db(procedures):
	for procedure in procedures:
		name = procedure.nameENG
		print (name)
		name = name.replace("operation","surgery").replace("operations","surgery").replace("surgerys","surgery").replace('need','needs')
		print(name)
		procedure.nameENG=name
		procedure.save()
	return

def whoosh(input):
	input = standardize_input(input)
	keywords = getKeywords(input)
	all_results = SearchQuerySet().all()
	data = []
	if keywords:
		all_results = query(all_results, keywords)
		# for keyword in keywords:
		# 	all_results = all_results.filter(content=keyword)
		for result in all_results:
			dict ={}
			dict['name']=result.object.nameSLO
			dict['value']=input + " " + result.object.procedure_id
			data.append(dict)
			#print(result.score)
		none={}
		none['name']="Nobeden izmed zgoraj naštetih"
		none['value']=input + " NONE"
		data.append(none)

	return data

def getKeywords(input):
	words = input.split(' ')
	keywords = []
	for keyword in words:
		if not keyword:
			continue
		if(SearchQuerySet().filter(content=keyword).count() > 0):
			keywords.append(keyword)
	print("keywords:",keywords)
	return keywords

def hasNumbers(inputString):
	return any(char.isdigit() for char in inputString)

def checkRegion(message):
	if message.find('regions') > -1:
		message = message.replace('regions','')
		data = whoosh(message)
		if len(data) > 1:
			return True
		return False
	return True

def query(set,keywords):
	if len(keywords) == 1:
		return set.filter(content=keywords[0])
	pairs = pair(keywords)
	result = set
	for p in pairs:
		new_set = set.filter(content=p[0]).filter(content=p[1])
		result |= new_set
	if len(result) == 0 and len(keywords)>1:
		for keyword in keywords:
			new_set = set.filter(content=keyword)
			result |= new_set
	return result

def pair(list):
	result = []
	for item in list:
		for item2 in list:
			if list.index(item) > list.index(item2):
				result.append([item,item2])
	return result

def lemmatize(input):

	url = "http://oznacevalnik.slovenscina.eu/Vsebine/Sl/SpletniServis/SpletniServis.aspx"

	#GET FORM DATA
	response = requests.get(url)
	html = response.text
	soup = BeautifulSoup(html,"html.parser")
	viewstate=soup.find("input", {"id":"__VIEWSTATE"}).attrs['value']
	viewstategenerator=soup.find("input", {"id":"__VIEWSTATEGENERATOR"}).attrs['value']
	eventvalidation=soup.find("input", {"id":"__EVENTVALIDATION"}).attrs['value']

	d = {"ctl00$ctl00$ContentPlaceHolder$ContentFullPlaceHolder$TextBox":input,
		 "ctl00$ctl00$ContentPlaceHolder$ContentFullPlaceHolder$OutputType":"TEI-XML",
		 "ctl00$ctl00$ContentPlaceHolder$ContentFullPlaceHolder$Submit":"Označi besedilo",
		 "__VIEWSTATE":viewstate,
		 "__VIEWSTATEGENERATOR":viewstategenerator,
		 "__EVENTVALIDATION":eventvalidation
		 }
	lemmatized =""

	response = requests.post(url, data = d)
	html = response.text
	soup = BeautifulSoup(html,"html.parser")
	xml=soup.find_all('pre')[0].text
	root = etree.fromstring(xml)
	els = root[0][0][0][0]
	i = 0
	for el in els:
		if i%2==0:
			try: 
				lemmatized += el.attrib['lemma'] + " "
			except: 
				print("element has no lemma")
		i+=1
	return lemmatized

def findSLO(input):
	words = input.split(" ")

	keywords = []
	results = Procedure.objects.all()
	for word in words:
		if word and len(results.filter(lemma__icontains=word+" "))>0:
			keywords.append(word)
	print("keywordsSLO:",keywords)
	if not keywords:
		return []
	for word in keywords:
		if word not in ["z", "v","pri","na","čez","s","do","iz","h","k","po","za","biti"]:
			results = results.filter(lemma__icontains=word+" ")
	print(len(results))
	if len(results) < 1:
		for word in keywords:
			if word not in ["z", "v","pri","na","čez","s","do","iz","h","k","po","za","biti"]:
				results |= Procedure.objects.filter(lemma__icontains=word+" ")

	data = []
	for result in results:
		dict ={}
		dict['name']= result.nameSLO
		dict['value']= result.procedure_id
		data.append(dict)
	none={}
	none['name']="Nobeden izmed zgoraj naštetih"
	none['value']=translate(input).replace("'m"," am") + " NONE"
	data.append(none)
	return data


