"""Command flags parsing module."""

__all__ = ['FLAGS']

import re
import sys


class Error(Exception):
  pass


class InvalidFlagError(Error):
  pass


class NotParseableFlag(Error):
  pass


class FlagHolder(object):

  FLAG_PATTERNS = [
      '^-{1,2}(\w+)="([\d\w\ -\.\\/]|[^"]+)"$',
      '^-{1,2}(\w+)=\'([\d\w\ -\.\\/]|[^\']+)\'$',
      '^-{1,2}(\w+)=([\.\\/\w-]+)$',
    ]

  def __init__(self, argv):
    self._flag_dict = {}
    self._default_mappers = {}
    for arg in argv:
      self.ProcessFlag(arg)

  def ProcessFlag(self, arg):
    holder = self._flag_dict
    flag, value = self.ParseFlag(arg)
    if flag != None:
      if not flag in holder:
        holder[flag] = value

  def ParseFlag(self, arg):
    # print 'arg: %s' % arg
    for index, flag_pattern in enumerate(self.FLAG_PATTERNS):
      # print 'pattern: %s' % flag_pattern
      pattern = re.compile(flag_pattern)
      match = pattern.match(arg)
      if match:
        # print "whole: %s  at index %d" % (arg, index)
        return match.groups()
    # print arg
    return None, None

  def __getattr__(self, flag):
    holder = self._flag_dict
    mappers = self._default_mappers
    if holder.has_key(flag):
      mapper = mappers[flag] if mappers.has_key(flag) else None
      if mapper != None:
        return mapper(holder[flag])
      else:
        return holder[flag]
    else:
      raise InvalidFlagError('Flag undefined: %s' % flag)

  def ProcessDefault(self, flag_name, default, mapper=str):
    holder = self._flag_dict
    if not holder.has_key(flag_name):
      holder[flag_name] = mapper(default)
    self._default_mappers[flag_name] = mapper


FLAGS = FlagHolder(sys.argv)


def DefineFlag(flag_name, default, mapper=str):
  FLAGS.ProcessDefault(flag_name, default, mapper)
