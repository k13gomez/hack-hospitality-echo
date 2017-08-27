from __future__ import print_function
import requests
import json

def lambda_handler(event, context):

	""" Route the incoming request based on type (LaunchRequest, IntentRequest,
	etc.) The JSON body of the request is provided in the event parameter.
	"""
	print("event.session.application.applicationId=" +
		  event['session']['application']['applicationId'])

	"""
	Uncomment this if statement and populate with your skill's application ID to
	prevent someone else from configuring a skill that sends requests to this
	function.
	"""
	# if (event['session']['application']['applicationId'] !=
	#         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
	#     raise ValueError("Invalid Application ID")

	if event['session']['new']:
		on_session_started({'requestId': event['request']['requestId']},
						   event['session'])

	if event['request']['type'] == "LaunchRequest":
		return on_launch(event['request'], event['session'])
	elif event['request']['type'] == "IntentRequest":
		return on_intent(event['request'], event['session'])
	elif event['request']['type'] == "SessionEndedRequest":
		return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
	""" Called when the session starts """

	print("on_session_started requestId=" + session_started_request['requestId']
		  + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
	""" Called when the user launches the skill without specifying what they
	want
	"""

	print("on_launch requestId=" + launch_request['requestId'] +
		  ", sessionId=" + session['sessionId'])
	# Dispatch to your skill's launch
	return get_welcome_response()


def on_intent(intent_request, session):
	""" Called when the user specifies an intent for this skill """

	print("on_intent requestId=" + intent_request['requestId'] +
		  ", sessionId=" + session['sessionId'])

	intent = intent_request['intent']
	intent_name = intent_request['intent']['name']

	# Dispatch to your skill's intent handlers
	if intent_name == "getOrdersIntent":
		return getOrders(intent, session)
	elif intent_name == "getCancelledIntent":
		return getCancelled(intent, session)
	elif intent_name == "getSpecialIntent":
		return getSpecial(intent, session)
	elif intent_name == "getRenewalRateIntent":
		return getRenewalRate(intent, session)
	elif intent_name == "AMAZON.HelpIntent":
		return get_welcome_response()
	elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
		return handle_session_end_request()
	else:
		raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
	""" Called when the user ends the session.

	Is not called when the skill returns should_end_session=true
	"""
	print("on_session_ended requestId=" + session_ended_request['requestId'] +
		  ", sessionId=" + session['sessionId'])
	# add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
	session_attributes = {}
	card_title = None
	reprompt_text = None
	speech_output = "Welcome to the Fit Life Sales Admininstration Skill. You can ask me about sales, retention, and other metrics for your business."
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session, speech_output))


def handle_session_end_request():
	should_end_session = True
	return build_response({}, build_speechlet_response(
		None, None, None, should_end_session, None))

######### THIS GETS THE USERS DOMAIN ###########
def getCancelled(intent, session):
	session_attributes = {}
	card_title = None
	reprompt_text = None
	should_end_session = True
	
	r = requests.get('http://redash-dev.hack-hospitality-fitlife.k13labs.com/api/queries/8/results.json?api_key=7zFvAaukqKKUAE5ffG3slVviGe10V73LGHISlETg')
	orders = dict(r.json())['query_result']['data']['rows'][0]['SUM(unique_users)']

	speech_output = "There are " + str(round(int(orders),-1)) + " orders cancelled this week."

	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session, speech_output))

def getRenewalRate(intent, session):

	session_attributes = {}
	card_title = None
	reprompt_text = None
	should_end_session = True
	r = requests.get('http://redash-dev.hack-hospitality-fitlife.k13labs.com/api/queries/10/results.json?api_key=FavXQREkxIhV0u5CSf7wTjY0zx4oe1glgMoVCQ23')
	data1 = float(dict(r.json())['query_result']['data']['rows'][-1]['renewal_orders'])
	data2 = float(dict(r.json())['query_result']['data']['rows'][-1]['total_orders'])

	print(str(data1) + "\n\n")
	print(data2)
	renewalRate = float(data1/data2)*100
	print(renewalRate)

	speech_output = "The renewal percent for this week is " + str(round(renewalRate, 2)) + " percent based on the " + str(int(data1)) + " renewal orders out of " + str(int(data2)) + " total orders."

	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session, speech_output))

def getOrders(intent, session):
	session_attributes = {}
	card_title = None
	reprompt_text = None
	should_end_session = True

	r = requests.get('http://redash-dev.hack-hospitality-fitlife.k13labs.com/api/queries/6/results.json?api_key=AIER9n6VOq0NWGZMZwwO3XZz9QEpTs7ueyYKcymK')
	orders = dict(r.json())['query_result']['data']['rows'][0]['order_total']

	r = requests.get('http://redash-dev.hack-hospitality-fitlife.k13labs.com/api/queries/11/results.json?api_key=8iKWmkaGCXQERXQxrk3w3cg6ITVlWiy1VeByHiYW')
	revenue = dict(r.json())['query_result']['data']['rows'][0]['total_revenue']

	speech_output = "There are " + str(orders) + " orders confirmed this week, for a total revenue of $" + str(round(revenue, 2))

	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session, speech_output))

def getSpecial(intent, session):
	session_attributes = {}
	card_title = None
	reprompt_text = None
	should_end_session = True

	if 'value' in intent['slots']['type']:
		type_of_order = intent['slots']['type']['value']
		if "new" in type_of_order:
			checkvalue = 'new_customer_orders'
			type_name = "New Customer Orders"
		elif "returning" in type_of_order or "reordering" in type_of_order:
			checkvalue = 'renewal_orders'
			type_name = "Renewal Customer Orders"

		r = requests.get('http://redash-dev.hack-hospitality-fitlife.k13labs.com/api/queries/10/results.json?api_key=FavXQREkxIhV0u5CSf7wTjY0zx4oe1glgMoVCQ23')
		data = dict(r.json())['query_result']['data']['rows'][-1][checkvalue]

	speech_output = "There are " + str(data) + " " + str(type_name) + " confirmed this week."

	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session, speech_output))

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session, card_text):
	if output == None:
		return {
			'shouldEndSession': should_end_session
		}
	elif title == None:
		return {
			'outputSpeech': {
				'type': 'PlainText',
				'text': output
			},
			'reprompt': {
				'outputSpeech': {
					'type': 'PlainText',
					'text': reprompt_text
				}
			},
			'shouldEndSession': should_end_session
		}
	else:
		return {
			'outputSpeech': {
				'type': 'PlainText',
				'text': output
			},
			'card': {
				'type': 'Simple',
				'title':  title,
				'content': card_text
			},
			'reprompt': {
				'outputSpeech': {
					'type': 'PlainText',
					'text': reprompt_text
				}
			},
			'shouldEndSession': should_end_session
		}


def build_response(session_attributes, speechlet_response):
	return {
		'version': '1.0',
		'sessionAttributes': session_attributes,
		'response': speechlet_response
	}