import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secretfile.json"
 
import dialogflow_v2 as dialogflow
dialogflow_session_client = dialogflow.SessionsClient()
PROJECT_ID = "weather-app-frosba"
 
from weather import query_api

from pymongo import MongoClient
client=MongoClient('mongodb+srv://admin:admin@cluster0-pjkgh.mongodb.net/test?retryWrites=true&w=majority')
db = client.get_database('weather_db')
records=db.weather_records

from gnewsclient import gnewsclient

client = gnewsclient.NewsClient(max_results=3)


def get_news(parameters):
	dbnews = {'Topic':parameters.get('news_type'),'Language':parameters.get('language'),'Location':parameters.get('geo-country')}
	client.topic = parameters.get('news_type')
	client.language = parameters.get('language')
	client.location = parameters.get('geo-country')
	client.max_results=3
	records.insert_one(dbnews)
	print(parameters)
	return client.get_news()
 
def get_weather(city):
	dbweather = {'Topic':city.get('query_type'),'Location':city.get('geo-ciy')}
	data = query_api(city)
	weather = data['weather'][0]
	records.insert_one(dbweather)
	return 'Weather Details are : \nMain: '+str(weather['main'])+'\nDescription: '+str(weather['description'])
 
def get_temperature(city):
	dbtemp = {'Topic':city.get('query_type'),'Location':city.get('geo-ciy')}
	data = query_api(city)
	main = data['main']
	temp = main['temp']
	temp_min = main['temp_min']
	temp_max = main['temp_max']
	records.insert_one(dbtemp)
	return 'Temperature: '+str(temp)+'\nMinimum Temperature: '+str(temp_min)+'\nMaximum Temperature: '+str(temp_max)
 
 
def detect_intent_from_text(text, session_id, language_code='en'):
	session = dialogflow_session_client.session_path(PROJECT_ID, session_id)
	text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
	query_input = dialogflow.types.QueryInput(text=text_input)
	response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
	return response.query_result
 
def fetch_reply(msg, session_id):
	response = detect_intent_from_text(msg,session_id)
	query_type = dict(response.parameters).get('query_type')
	city = dict(response.parameters).get('geo-city')
 
	print("Response Params: ",response.parameters)
 
	print(response.intent.display_name)
 
	if response.intent.display_name == 'get_weather':
 
		if query_type == 'Weather':
			weather = get_weather(city)
			return str(weather)
 
		elif query_type == 'Temperature':
			temp = get_temperature(city)
			return temp

	elif response.intent.display_name == 'get_news':
		news = get_news(dict(response.parameters))
		news_str = 'Here is your news:'
		for row in news:
			news_str += "\n\n{}\n\n{}\n\n".format(row['title'],
				row['link'])
		return news_str
	else:
		return response.fulfillment.text