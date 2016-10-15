# !/usr/bin/env python
from __future__ import print_function
""" SIP plugin uses mqtt plugin to broadcast station status every time it changes.
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
    '/mqtt-zones-sp', 'plugins.mqtt-zones.settings',
    '/mqtt-zones-save', 'plugins.mqtt-zones.save_settings'
    ])
gv.plugin_menu.append(['MQTT Zones', '/mqtt-zones-sp'])

class settings(ProtectedPage):
    """Load an html page for entering plugin settings.
    """
    def GET(self):
        settings = mqtt.get_settings()
        zone_topic = settings.get('zone_topic', gv.sd[u'name'] + '/zones')
        return template_render.mqtt(settings, "")  # open settings page

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
        raise web.seeother('/')  # Return user to home page.

### valves ###
def notify_zone_change(name, **kw):
    print("MQTT Zones:", gv.srvals) #  This shows the state of the zones.

zones = signal('zone_change')
zones.connect(notify_zone_change)
