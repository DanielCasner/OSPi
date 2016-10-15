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
try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("ERROR: MQTT Plugin requires paho mqtt.")
    print("\ttry: pip install paho-mqtt")
    mqtt = None

DATA_FILE = "./data/mqtt.json"

_client = None
_settings = {
    'broker_host': 'localhost',
    'broker_port': 1883,
    'publish_up_down': ''
}

# Add new URLs to access classes in this plugin.
urls.extend([
    '/mqtt-sp', 'plugins.mqtt.settings',
    '/mqtt-save', 'plugins.mqtt.save_settings'
    ])
gv.plugin_menu.append(['MQTT', '/mqtt-sp'])

NO_MQTT_ERROR = "MQTT plugin requires paho mqtt python library. On the command line run `pip install paho-mqtt` and restart SIP to get it."

class settings(ProtectedPage):
    """Load an html page for entering plugin settings.
    """
    def GET(self):
        settings = get_settings()
        return template_render.mqtt(settings, gv.sd[u'name'], NO_MQTT_ERROR if mqtt is None else "")  # open settings page

class save_settings(ProtectedPage):
    """Save user input to json file.
    Will create or update file when SUBMIT button is clicked
    CheckBoxes only appear in qdict if they are checked.
    """

    def GET(self):
        qdict = web.input()  # Dictionary of values returned as query string from settings page.
        with open(DATA_FILE, 'w') as f:
            try:
                port = int(qdict['broker_port'])
                assert port > 80 and port < 65535
                qdict['broker_port'] = port
            except:
                return template_render.proto(qdict, gv.sd[u'name'], "Broker port must be a valid integer port number")
            else:
                json.dump(qdict, f) # save to file
                publish_status()
        raise web.seeother('/')  # Return user to home page.

def get_settings():
    global _settings
    try:
        fh = open(DATA_FILE, 'r')
        try:
            _settings = json.load(fh)
        except ValueError as e:
            print("MQTT pluging couldn't parse data file:", e)
        finally:
            fh.close()
    except IOError as e:
        print("MQTT Plugin couldn't open data file:", e)
    print("MQTT settings:", _settings)
    return _settings

def get_client():
    global _client
    if _client is None and mqtt is not None:
        try:
            _client = mqtt.Client(gv.sd[u'name']) # Use system name as client ID
            _client.connect(_settings['broker_host'], _settings['broker_port'])
            if _settings['publish_up_down']:
                _client.will_set(_settings['publish_up_down'], json.dumps("DIED"), qos=1, retain=True)
            _client.loop_start()
        except Exception as e:
            print("MQTT plugin couldn't initalize client:", e)
    else:
        print(_client, mqtt)
    return _client

def publish_status(status="UP"):
    if _settings['publish_up_down']:
        print("MQTT publish", status)
        client = get_client()
        if client:
            client.publish(_settings['publish_up_down'], json.dumps(status), qos=1, retain=True)
    else:
        print(_settings['publish_up_down'])

### Restart ###
def on_restart(name, **kw):
    if _client is not None:
        publish_status("DOWN")
        _client.disconnect()
        _client.loop_stop()
        _client = None

restart = signal('restart')
rebooted = signal('rebooted')
restart.connect(on_restart)
rebooted.connect(on_restart)

get_settings()

publish_status()
