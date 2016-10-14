# !/usr/bin/env python
from __future__ import print_function
""" SIP plugin adds an MQTT client to SIP for other plugins to broadcast and receive via MQTT
The intent is to facilitate joining SIP to larger automation systems
"""
__author__ = "Daniel Casner <daniel@danielcasner.org>"

import web  # web.py framework
import gv  # Get access to SIP's settings
from urls import urls  # Get access to SIP's URLs
from sip import template_render  #  Needed for working with web.py templates
from webpages import ProtectedPage  # Needed for security
from blinker import signal
import json  # for working with data file
import paho.mqtt.client as mqtt

DATA_FILE = "./data/mqtt.json"

_client = None

# Add new URLs to access classes in this plugin.
urls.extend([
    '/mqtt-sp', 'plugins.mqtt.settings',
    '/mqtt-save', 'plugins.mqtt.save_settings'
    ])

class settings(ProtectedPage):
    """Load an html page for entering plugin settings.
    """
    def GET(self):
        try:
            with open(DATA_FILE, 'r') as f:  # Read settings from json file if it exists
                settings = json.load(f)
        except IOError:  # If file does not exist return empty value
            settings = {
                'broker_host': 'localhost',
                'broker_port': 1883,
                'publish_up_down': ''
            }  # Default settings. can be list, dictionary, etc.
        return template_render.proto(settings, gv.sd[u'name'], "")  # open settings page

class save_settings(ProtectedPage):
    """Save user input to json file.
    Will create or update file when SUBMIT button is clicked
    CheckBoxes only appear in qdict if they are checked.
    """

    def GET(self):
        qdict = web.input()  # Dictionary of values returned as query string from settings page.
        with open(DATA_FILE, 'w') as f:  # Edit: change name of json file
            try:
                port = int(qdic['broker_port'])
                assert port > 80 and port < 65535
                qdic['broker_port'] = port
            except:
                return template_render.proto(qdic, gv.sd[u'name'], "Broker port must be a valid integer port number")
            else:
                json.dump(qdict, f) # save to file
        raise web.seeother('/')  # Return user to home page.

def get_client():
    if _client is None:
        try:
            with json.load(open(DATA_FILE, 'r')) as settings:
                try:
                    _client = mqtt.Client(gv.sd[u'name']) # Use system name as client ID
                    if settings['publish_up_down']:
                        _client.will_set(settings['publish_up_down'], json.dumps("DIED"), qos=1, retain=True)
                    _client.loop_start()
                    _client.connect(settings['broker_host'], settings['broker_port'])
                except Exception as e:
                    print("Could not initalize MQTT client: {}".format(str(e)))
        except IOError as e:
            print("MQTT Pluging could not load settings file", str(e))
    return _client

### Restart ###
def on_restart(name, **kw):
    if _client is not None:
        with json.load(open(DATA_FILE, 'r')) as settings:
            if settings['publish_up_down']:
                _client.publish(settings['publish_up_down'], json.dumps("DOWN"), qos=1, retain=True)
        _client.disconnect()
        _client.loop_stop()
        _client = None

restart = signal('restart')
restart.connect(on_restart)

try:
    with json.load(open(DATA_FILE, 'r')) as settings:
        if settings['publish_up_down']:
            with get_client as c:
                if c:
                    c.publish(settings['publish_up_down'], json.dumps("UP"), qos=1, retain=True)
except IOError as e:
    pass
