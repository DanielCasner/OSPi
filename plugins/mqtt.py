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
            }  # Default settings. can be list, dictionary, etc.
        return template_render.proto(settings, gv.sd[u'name'])  # open settings page

class save_settings(ProtectedPage):
    """Save user input to json file.
    Will create or update file when SUBMIT button is clicked
    CheckBoxes only appear in qdict if they are checked.
    """

    def GET(self):
        qdict = web.input()  # Dictionary of values returned as query string from settings page.
        with open(DATA_FILE, 'w') as f:  # Edit: change name of json file
            try:
                qdic['broker_port'] = int(qdic['broker_port'])
            except:
                # Do something with this
                pass
            else:
                json.dump(qdict, f) # save to file
        raise web.seeother('/')  # Return user to home page.

def get_client():
    if _client is None:
        try:
            with json.load(open(DATA_FILE, 'r')) as settings:
                _client = mqtt.Client(gv.sd[u'name']) # Use system name as client ID
                client.loop_start()
                client.connect(settings['broker_host'], settings['broker_port'])
        except IOError as e:
            print("MQTT Pluging could not load settings file", str(e))
    return _client

### Restart ###
def on_restart(name, **kw):
    if _client is not None:
        client.disconnect()
        client.loop_stop()
        _client = None

restart = signal('restart')
restart.connect(on_restart)
