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
		OGrequest = request
		message = request.POST['message']
		sessionID = request.POST['sessionID']

		print("*****SESSION ID*****   ",sessionID)
		if(message=="pomoč"):
			help ="<b>Da vam pomagam najti razpoložljivo storitev potrebujem naslednje informacije:<br><em>-kateri poseg iščete (npr. rentgen kolena)<br><em>-v kateri regiji iščete (npr. Gorenjska)<br><em>-kako nujno potrebujete poseg (npr. redno)<br><br><small>Vendar ne skrbite za regijo in nujnost vas bom povprašal sam.<br>Vi mi samo povejte katero storitev iščete."
			return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}"}}'.format(help,"none",[]))
		messageSLO = message

		if message == "!nujnosti":
			data = OGrequest.session['data']
			region = getRegion(data['region'])
			data_str = data['procedure'] + "; " + region + "; "
			urgencies = [{"name":"Redno","value":"3"},{"name":"Hitro","value":"2"},{"name":"Zelo hitro","value":"7"}]
			remove = []
			print(data['urgency'])
			for urgency in urgencies:
				if urgency['value'] == data['urgency']:
					remove.append(urgency)
				else:
					urgency['value'] = data_str + urgency['value'] +";"
			for item in remove:
				urgencies.remove(item)
			return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}"}}'.format("Kako hitro potrebujete poseg?","procedures",urgencies))

		if not hasNumbers(message) or message.find("24")>-1 and message!="reset":
			if messageSLO.find("NONESLO") > -1:
				message = translate(message.replace("NONESLO",""))+"NONESLO"
			elif messageSLO.find("NONE") > -1:
				message = translate(message.replace("NONE",""))+"NONE"
			else:
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
		print("messageSLO:",messageSLO)


		if message != "reset" and (message.find("NONE") < 0 or message.find("NONESLO")>-1) and not isUrgency(message) and (not hasNumbers(message) or message.find("24") > -1):
			if not isRegion(messageSLO, message):
				if message.find("NONESLO")>-1:
					message=message.replace("NONESLO","")
					whoosh_data = findSLO(lemmatize(messageSLO), message)
					OGrequest.session['procedures'] = notRight(OGrequest.session['procedures'],whoosh_data)
					if len(whoosh_data) > 1:
						return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}"}}'.format("Ste mislili:","procedures",whoosh_data))
				else:
					whoosh_data = whoosh(message, messageSLO)
					if(len(whoosh_data) < 2):
						whoosh_data = findSLO(lemmatize(messageSLO), message)
					if len(whoosh_data) > 1:
						if not 'procedures' in OGrequest.session:
							OGrequest.session['procedures'] = notRight([],whoosh_data)
						else:
							OGrequest.session['procedures'] = notRight(OGrequest.session['procedures'],whoosh_data)
						if len(whoosh_data) > 1:
							return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}"}}'.format("Ste mislili:","procedures",whoosh_data))
			message+= " NONE"

		print(message)
		#if 'procedures' in OGrequest.session:
		#	print('not right:',OGrequest.session['procedures'],"\n")
		#else: 
		#	print("All right")

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
		
		if  message != 'reset':
			try:
				OGrequest.session['urgency']=answer_json['result']['parameters']['urgency']
				print("urg:",OGrequest.session['urgency'])
			except:
				print("No urgency")

		if  message != 'reset':
			try:
				OGrequest.session['region']=answer_json['result']['parameters']['region']
				print("reg:",OGrequest.session['region'])
			except:
				print("No region")

		if  message != 'reset':
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
			pro = Procedure.objects.all().filter(procedure_id=procedure)
			if len(pro) > 0:
				text_answer = text_answer.replace("poseg","<b>" + pro[0].nameSLO + "</b>")
			else: text_answer = "Žal je prišlo do napake v naši bazi posegov, morda poseg ni več na voljo."
		else:
			if groups:
				OGrequest.session['group']=1
				if len(groups)>1:
					answer = text_answer
					text_answer = "Našel sem naslednje skupine posegov: "
					for group in groups:
						group = translateToSlo(group)
						text_answer += "<br>-<b>" + group +"</b>"
					text_answer += "<br>" + answer
				else:
					text_answer = "Ste mislili:" #Našel sem skupino posegov <b>" + translateToSlo(groups[0]) + "</b>.<br>" + text_answer
			
			
		#text_answer = text_answer.replace('\\','\\\\')

		print(text_answer)

		data = []
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
			if 'procedures' in OGrequest.session:
				OGrequest.session['procedures'] = notRight(OGrequest.session['procedures'],data)
			else:
				OGrequest.session['procedures'] = notRight([],data)
			none={}
			none['name']="Nobeden izmed zgoraj naštetih"
			none['value']= "reset"
			data.append(none)
		if text_answer.find("Ste mislili") > -1 or text_answer.find("skupine posegov") > -1 or text_answer.find("Izberi poseg")> -1:
			if OGrequest.session['urgency'] or OGrequest.session['region']:
				for item in data:
					if item['value'] != "reset":
						item['value'] += "; " + getRegion(OGrequest.session['region']) + "; " + OGrequest.session['urgency'] + ";"
			return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}"}}'.format(text_answer,"procedures",data))

		if text_answer.find("Kako hitro potrebujete")>-1:
			urgencies = [{"name":"Redno","value":"normal"},{"name":"Hitro","value":"fast"},{"name":"Zelo hitro","value":"very fast"}]
			return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}"}}'.format(text_answer,"procedures",urgencies))

		if text_answer.find("V kateri regiji iščete?")>-1:
			regions = [{ "name": "Vse regije", "value": "all regions" }, { "name": "Gorenjska regija", "value": "Gorenjska" }, { "name": "Goriška regija", "value": "Goriska" }, { "name": "Jugovzhodna Slovenija", "value": "Southeast" }, { "name": "Koroška regija", "value": "Koroška" }, { "name": "Obalno-kraška regija", "value": "Obalno-Kraska" }, { "name": "Osrednjeslovenska regija", "value": "Ljubljana" }, { "name": "Podravska regija", "value": "Podravska" }, { "name": "Pomurska regija", "value": "Pomurje" }, { "name": "Posavska regija", "value": "Posavska region" }, { "name": "Primorsko-notranjska regija", "value": "Primorsko-Inner" }, { "name": "Savinjska regija", "value": "Savinjska" }, { "name": "Zasavska regija", "value": "Zasavska" }]
			return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}"}}'.format(text_answer,"procedures",regions))

		if text_answer == "Poseg, ki ga iščete pod trenutnimi pogoji ni na voljo. Poskusite iskati v drugih regijah ali pod drugo nujnostjo." and not 'regions' in OGrequest.session and answer_json['result']['parameters']['region'] != "A":
			OGrequest.session['regions']=1
			text_answer = "Poseg v vaši regiji trenutno ni na voljo. Ali želite, da iščem v vseh regijah?"
			value="A " + answer_json['result']['parameters']['urgency'] + " " + answer_json['result']['parameters']['procedure']
			data = [{"name":"DA", "value":value},{"name":"NE","value":"reset"}]
			response_type="procedures"
			return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}"}}'.format(text_answer,"procedures",data))

		if response_type == 'waitingTimes' or text_answer == "Prosim ponovno začnite z iskanjem":
			if text_answer == "Poseg, ki ga iščete pod trenutnimi pogoji ni na voljo. Poskusite iskati v drugih regijah ali pod drugo nujnostjo." and answer_json['result']['parameters']['region'] == "A":
				text_answer = "Žal zgleda, da poseg ki ga iščete ni na voljo v nobeni izmed objavljenih ustanov."
			else:
				if text_answer != "Prosim ponovno začnite z iskanjem":
					text_answer += "<br><i><small>Če želite iskati pod drugimi nujnostmi napišite: !nujnosti</small></i>"
					current_data={}
					current_data['procedure']=answer_json['result']['parameters']['procedure']
					current_data['region']=answer_json['result']['parameters']['region']
					current_data['urgency']=answer_json['result']['parameters']['urgency']
					OGrequest.session['data']=current_data
			resetSession(OGrequest)
			return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}","url":"{3}"}}'.format(text_answer,response_type,data,url))
		resetSession(OGrequest)
		if text_answer:
			return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}"}}'.format(text_answer,"error",[]))
		else:
			return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}"}}'.format("Zgleda, da je prišlo do napake.","error",[]))
	else:
		return render(request,'dfchatbox/index.html')

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
	if req.text.find("html>")>0:
		return translate(input)
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
			return output.replace("'s"," is").replace("'m"," am").replace("'ve"," have").replace("n't"," not")
		return input
	return req.text[1:-3].replace("'s"," is").replace("'m"," am").replace("'ve"," have").replace("n't"," not")

def translateToSlo(input):
	output = requests.get('http://translation-api.docker-e9.ijs.si/translate?sentence=' + input +'&fromLang=en&toLang=sl').text
	if output.find("html") > 0:
		return translateToSlo(input)
	return output[1:-3]

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

def notRight(incorrect, data):
	remove = []
	for item in data:
		if item['name'] != 'Nobeden izmed zgoraj naštetih':
			if item['name'] in incorrect:
				remove.append(item)
			incorrect.append(item['name'])
	for item in remove:
		data.remove(item)
	return incorrect

def whoosh(input, inSLO):
	input = standardize_input(input)
	keywords = getKeywords(input)
	all_results = SearchQuerySet().all()
	data = []
	if keywords:
		all_results = query(all_results, keywords)
		print(len(all_results))
		for result in all_results:
			if result.object:
				dict ={}
				dict['name']=result.object.nameSLO.replace('"','')
				dict['value']=input + " " + result.object.procedure_id
				data.append(dict)
		none={}
		none['name']="Nobeden izmed zgoraj naštetih"
		none['value']=inSLO + " NONESLO"
		data.append(none)

	return data

def getKeywords(input):
	words = input.split(' ')
	keywords = []
	for keyword in words:
		if not keyword:
			continue
		if(keyword not in ["like"] and SearchQuerySet().filter(content=keyword).count() > 0):
			keywords.append(keyword)
	print("keywords:",keywords)
	return keywords

def hasNumbers(inputString):
	return any(char.isdigit() for char in inputString)

def isRegion(SLO, ENG):
	if SLO in ["all regions", "Gorenjska", "Goriska", "Southeast", "Koroška", "Obalno-Kraska", "Ljubljana", "Podravska", "Pomurje", "Posavska region", "Primorsko-Inner","Savinjska", "Zasavska"]:
		return True
	if ENG.find('regions') > -1:
		wsh = ENG.replace('regions','')
		data = whoosh(wsh, SLO)
		if len(data) > 1:
			return False
		return True
	return False

def isUrgency(input):
	return input in ['normal','fast','very fast']

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
	sentences = root[0][0][0]
	exceptions=[]
	for els in sentences:
		for el in els:
			try: 
				lemmatized += el.attrib['lemma'] + " "
			except:
				exceptions.append(el)
	return lemmatized

def findSLO(input, english):
	words = input.split(" ")

	keywords = []
	results = Procedure.objects.all()
	for word in words:
		if word and len(word)>1:
			if (len(word)>3 and len(results.filter(lemma__icontains=word))>0) or len(results.filter(lemma__icontains=" " +word+" "))>0:
				keywords.append(word)
	print("keywordsSLO:",keywords)
	if not keywords:
		return []
	badKeywords=True
	for word in keywords:
		if word not in ["pri","na","čez","s","do","iz","po","za","biti","ali","ja","ne","no"]:
			badKeywords=False
			if len(word)>3:
				results = results.filter(lemma__icontains=word)
			else:
				results = results.filter(lemma__icontains=" "+word)
				if not results:
					results = results.filter(lemma__icontains=word+" ")
	if badKeywords:
		return []
	if len(results) < 1:
		for word in keywords:
			if word not in ["pri","na","čez","do","iz","po","za","biti","ali","ja","ne","no"]:
				results |= Procedure.objects.filter(lemma__icontains=word+" ")
	data = []
	print(len(results))
	for result in results:
		dicti ={}
		dicti['name']= result.nameSLO.replace('"','')
		dicti['value']= english + " " + result.procedure_id
		data.append(dicti)
	none={}
	none['name']="Nobeden izmed zgoraj naštetih"
	none['value']= english + " NONE"
	data.append(none)
	return data

def resetSession(request):
	if 'regions' in request.session:
		del request.session['regions']
	if 'procedure' in request.session:
		del request.session['procedure']
	if 'group' in request.session:
		del request.session['group']
	if 'urgency' in request.session:
		del request.session['urgency']
	if 'region' in request.session:
		del request.session['region']
	if 'procedures' in request.session:
		del request.session['procedures']
	request.session.modified = True
	return

def getRegion(reg):
	regions = [{"id":"A","value":"all regions"}, 	{ "id":"9", "value": "Gorenjska" }, { "id":"11", "value": "Goriska" }, { "id":"7", "value": "Southeast" }, { "id":"1", "value": "Koroška" }, { "id":"12", "value": "Obalno-Kraska" }, { "id":"8", "value": "Ljubljana" }, { "id":"3" , "value": "Podravska" }, { "id":"2", "value": "Pomurje" }, { "id":"6", "value": "Posavska region" }, { "id":"10", "value": "Primorsko-Inner" }, { "id":"4", "value": "Savinjska" }, { "id":"5" , "value": "Zasavska" }]
	for region in regions:
		if region["id"] == reg:
			return region["value"]
	return reg