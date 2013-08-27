#!/usr/bin/python
import ospi
import subprocess

  #### Add any new page urls here ####
ospi.urls.extend(['/dht', 'ospi_addon.dht', '/uptime', 'ospi_addon.uptime'])

##print ospi.urls # for testing

  #### add new functions and classes here ####

  ### Example custom class. Uncomment and use to create a new web page. ###
##class custom_page_1:
##   """Add description here"""
##   def GET(self):
##      custpg = '<!DOCTYPE html>\n'
##      #Insert Custom Code here.
##      return custpg


class dht:
   """Add description here"""
   def GET(self):
      custpg = '<!DOCTYPE html>\n<html>\n<body>\n<pre>\n'
      p = subprocess.Popen(['Adafruit_DHT', '11', '24'], stdout=subprocess.PIPE)
      p.wait()
      custpg += p.communicate()[0]
      custpg += '\n</pre>\n</body>\n</html>\n'
      return custpg

class uptime:
   """Add description here"""
   def GET(self):
      custpg = '<!DOCTYPE html>\n<html>\n<body>\n<pre>\n'
      p = subprocess.Popen(['uptime'], stdout=subprocess.PIPE)
      p.wait()
      custpg += p.communicate()[0]
      custpg += '\n</pre>\n</body>\n</html>\n'
      return custpg



  
