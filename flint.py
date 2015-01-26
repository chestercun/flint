#!/usr/bin/python

import flags

import os
import re
import sys
import urllib
import urllib2

__location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

flags.DefineFlag('core', '0', str)
flags.DefineFlag('pin', 'D0', str)

FLAGS = flags.FLAGS

# Cloud API URL.
SPARK_CLOUD = 'https://api.spark.io/v1/devices/%s/'

# Spark Core token.
ACCESS_TOKEN = '' # Set by the TOKEN file.

try:
  filename = os.path.join(__location__, 'TOKEN')
  ACCESS_TOKEN = [token.strip() for token in open(filename, 'r')][0]
except IOError as e:
  print 'TOKEN file not found: ', e
  exit()

# Access token is usually required.
def DefaultParams():
  return {'access_token': ACCESS_TOKEN}

# Registered Cores.
CORE_IDS = {} # Set by the CORES file.

try:
  filename = os.path.join(__location__, 'CORES')
  lines = [line.strip() for line in open(filename, 'r')]
  for line in lines:
    core, uid = line.split(',')
    CORE_IDS[core] = uid
except IOError as e:
  print 'CORES file not found: ', e
  exit()

FLAG_PATTERN = re.compile('^-{1,2}')

def IsFlag(value=''):
  return FLAG_PATTERN.match(value) != None

def GetRequest(url='', params={}):
  print url, params
  data = urllib.urlencode(params)
  request = url + '?' + data
  try:
    response = urllib2.urlopen(request)
    result = response.read()
    print result
  except urllib2.HTTPError as e:
    print 'Request failed: ', e.reason

def PostRequest(url='', params={}):
  print url, params
  data = urllib.urlencode(params)
  request = urllib2.Request(url, data)
  response = urllib2.urlopen(request)
  result = response.read()
  print result

def tinker(args=[]):
  args = filter(lambda arg : not IsFlag(arg), args)
  is_digital = FLAGS.pin.startswith('D')
  is_read = len(args) == 0
  params = DefaultParams()

  if is_digital and is_read:
    cmd = 'digitalRead'
    params['params'] = FLAGS.pin
  elif is_digital and not is_read:
    cmd = 'digitalWrite'
    # Check for the presence of a high or low in the cmd line args.
    high_ct = map(lambda x: x.lower(), args).count('high')
    low_ct = map(lambda x: x.lower(), args).count('low')
    setting = 'HIGH' if high_ct > low_ct else 'LOW'
    params['params'] = FLAGS.pin + ',' + setting
  elif not is_digital and is_read:
    cmd = 'analogRead'
    params['params'] = FLAGS.pin
  elif not is_digital and not is_read:
    cmd = 'analogWrite'
    params['params'] = FLAGS.pin + ',' + args[0]
  # Send tinker request.
  url = SPARK_CLOUD % CORE_IDS[FLAGS.core] + cmd
  PostRequest(url, params)

def variable(args=[]):
  for variable in args:
    url = SPARK_CLOUD % CORE_IDS[FLAGS.core] + variable
    GetRequest(url, DefaultParams())

def event(args=[]):
  print 'Not implemented yet'

CMDS = {
	'tinker': {
		  'help' : '--pin=D7 <high, low, or blank for a read>',
      'function': tinker,
    },
	'variable': {
		  'help' : '<variable to read>',
      'function': variable,
    },
	'event': {
		  'help' : '<event to subscribe to>',
      'function': event,
    },
}

def Usage():
  print ''
  print 'Usage:'
  print ''
  print '\t--core=<spark core id>'
  print '\t--pin=<D0-D7 or A0-A7>'
  print ''
  cmds = CMDS.keys()
  cmds.sort()
  for cmd in cmds:
    print '\tflint ' + cmd + ' ' + CMDS[cmd]['help']
  print ''

def main(argv):
  if len(argv) and CMDS.keys().count(argv[0]):
  	cmd = argv[0]
  	args = argv[1:]
  	CMDS[cmd]['function'](args)
  else:
  	Usage()

if __name__ == '__main__':
  main(sys.argv[1:])
