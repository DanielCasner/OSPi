# !/usr/bin/env python
from __future__ import print_function
""" SIP plugin uses mqtt plugin to receive run once program commands over MQTT
"""
__author__ = "Daniel Casner <daniel@danielcasner.org>"

import web  # web.py framework
import gv  # Get access to SIP's settings
from urls import urls  # Get access to SIP's URLs
from sip import template_render  #  Needed for working with web.py templates
from webpages import ProtectedPage  # Needed for security
from blinker import signal # To receive station notifications
import json  # for working with data file
from plugins import mqtt

# Add new URLs to access classes in this plugin.
urls.extend([
    '/mr1-sp', 'plugins.mqtt_schedule.settings',
    '/mr1-save', 'plugins.mqtt_schedule.save_settings'
    ])
gv.plugin_menu.append(['MQTT scheduler', '/mr1-sp'])

class settings(ProtectedPage):
    """Load an html page for entering plugin settings.
    """
    def GET(self):
        settings = mqtt.get_settings()
        zone_topic = settings.get('schedule_topic', gv.sd[u'name'] + '/schedule')
        return template_render.mqtt_zones(zone_topic, "")  # open settings page

class save_settings(ProtectedPage):
    """Save user input to json file.
    Will create or update file when SUBMIT button is clicked
    CheckBoxes only appear in qdict if they are checked.
    """
    def GET(self):
        qdict = web.input()  # Dictionary of values returned as query string from settings page.
        settings = mqtt.get_settings()
        settings.update(qdict)
        with open(mqtt.DATA_FILE, 'w') as f:
            json.dump(settings, f) # save to file
        subscribe()
        raise web.seeother('/')  # Return user to home page.

def on_message(client, msg):
    "Callback when MQTT message is received."
    

def subscribe():
    "Subscribe to messages"
    topic = mqtt.get_settings('schedule_topic')
    if topic:
        mqtt.subscribe(topic, on_message, 2)

subscribe()
