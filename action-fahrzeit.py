#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import logging

CONFIG_INI = "config.ini"

# If this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
# Hint: MQTT server is always running on the master device
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

class Fahrzeit(object):
    """Class used to wrap action code with mqtt connection
        
        Please change the name refering to your application
    """
	logger = logging.getLogger(__name__)
	
    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            self.config = None

		logger.setLevel(logging.WARN)
		# create console handler and set level to warn
		ch = logging.StreamHandler()
		ch.setLevel(logging.WARN)
		# add ch to logger
		logger.addHandler(ch)

        # start listening to MQTT
        self.start_blocking()
        
    # --> Sub callback function, one per intent
    def intent_1_callback(self, hermes, intent_message):
	
   if len(intentMessage.slots.ziel) > 0:

        logger.debug(conf['secret']['heimatort'])
        logger.debug(conf['secret']['heimatortlonlat'])

        ziel = intentMessage.slots.ziel.first().value # We extract the value from the slot "Ziel"
        logger.debug(ziel)

        # Search if ort is saved
        logger.debug(conf['secret']['ort1'] + ': ' + conf['secret']['ort1lonlat'])

        lonlat="NA"

        if ziel == conf['secret']['ort1'] :
            lonlat = conf['secret']['ort1lonlat']

        if ziel == conf['secret']['ort2'] :
            lonlat = conf['secret']['ort2lonlat']

        if lonlat == "NA":
            result_sentence = "Der Zielort {0} wurde nicht hinterlegt.".format(ziel) 
        else:
            url = 'https://api.tomtom.com/routing/1/calculateRoute/' + conf['secret']['heimatortlonlat'] + ':' + lonlat +'/json?computeTravelTimeFor=all&routeType=fastest&avoid=unpavedRoads&travelMode=car&key='+conf['secret']['apikey']
            logger.debug(url)
            req = urllib.request.Request(url)
            r = urllib.request.urlopen(req).read()
            cont = json.loads(r.decode('utf-8'))
            #logger.debug(cont)
            
            travel_time = cont['routes'][0]['summary']['noTrafficTravelTimeInSeconds'] // 60
            travel_time_historic = cont['routes'][0]['summary']['historicTrafficTravelTimeInSeconds'] // 60
            travel_time_live = cont['routes'][0]['summary']['liveTrafficIncidentsTravelTimeInSeconds'] // 60
            arrival_time = cont['routes'][0]['summary']['arrivalTime']
            logger.debug("Fahrzeit: {0}, Normal: {1}, Live: {2}, Ankunftszeit: {3}".format(str(travel_time), str(travel_time_historic), str(travel_time_live), str(arrival_time)))
            #travel_time = travel_time % 60
            #travel_time_historic = travel_time_historic % 60
            #travel_time_live = travel_time_live % 60
            #logger.debug("Fahrzeit: {0}, Normal: {1}, Live: {2}, Ankunftszeit: {3}".format(str(travel_time), str(travel_time_historic), str(travel_time_live), str(arrival_time)))
            
            # The response that will be said out loud by the TTS engine.
            diff = travel_time_live - travel_time_historic
            if diff < 4:
                result_sentence = "Die Fahrzeit nach {0} beträgt {1:d} Minuten. ".format(ziel, travel_time_live)
            else:
                result_sentence = "Die Fahrzeit nach {0} beträgt {1:d} Minuten. Das sind {2:d} Minuten mehr als normal. ".format(ziel, travel_time_live, diff)
            
            # Und die Ankunftszeit
            pos = arrival_time.find('+')
            if pos > 0:
                arrival_time = arrival_time[0:pos]
            a_time=datetime.datetime.strptime(arrival_time,'%Y-%m-%dT%H:%M:%S')
            logger.debug(a_time)
            hours = a_time.hour
            minutes = a_time.minute
            if minutes == 0:
                minutes = ""
            if hours == 1:
                time = "ein Uhr {0}".format(minutes)
            else:
                time = "{0} Uhr {1}".format(hours, minutes)
            
            result_sentence += "Die Ankunftzeit ist {0}.".format(time) 
    else:
        result_sentence = "Turning on lightKein Ziel angegeben	
	
	
	
	
	
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")
        
        # action code goes here...
        print '[Received] intent: {}'.format(intent_message.intent.intent_name)

        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, "Action1 has been done", "")

    def intent_2_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")

        # action code goes here...
        print '[Received] intent: {}'.format(intent_message.intent.intent_name)

        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, "Action2 has been done", "")

    # More callback function goes here...

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        if coming_intent == 'FahrzeitZiel':
            self.intent_1_callback(hermes, intent_message)
        #if coming_intent == 'intent_2':
        #    self.intent_2_callback(hermes, intent_message)

        # more callback and if condition goes here...

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    Fahrzeit()
