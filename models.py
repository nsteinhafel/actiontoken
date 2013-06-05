from datetime import datetime
from hashlib import sha1
from random import random

from django.contrib.auth.models import User
from django.db import models

import app_settings

class InvalidModelName(Exception):
  pass

class Rule(models.Model):
  CREATE  = 'C'
  READ    = 'R'
  UPDATE  = 'U'
  DELETE  = 'D'
  ACTIONS = (
    (CREATE,  'create'),
    (READ,    'read'), 
    (UPDATE,  'update'), 
    (DELETE,  'delete'),
  )

  action = models.CharField(max_length=1, choices=ACTIONS, default=READ)
  model = models.CharField(max_length=255)

  def is_class(self):
    return isinstance(self.get_class(), type)

  def get_class(self):
    import_dict = self.model.rsplit('.', 1)
    if not len(import_dict) == 2:
      raise InvalidModelName('Model could not be imported (is it fully qualified?).')
    return getattr(__import__(import_dict[0], fromlist=[import_dict[1]]), import_dict[1])

  def __unicode__(self):
    return '%s %ss' % (dict(Rule.ACTIONS)[self.action], self.model)

class Field(models.Model):
  name = models.CharField(max_length=255)
  rule = models.ForeignKey(Rule)

  def is_valid_for_rule(self):
    return self.rule.action in [Rule.READ, Rule.UPDATE]

  def is_field(self):
    return self.name in map(lambda x: x.name, self.rule.get_class()._meta.fields)

  def __unicode__(self):
    return '%s %s\'s %s' % (self.rule.action, self.rule.model, self.name)

class Token(models.Model):
  token = models.CharField(max_length=40)
  expires = models.DateTimeField()
  user = models.ForeignKey(User) # user performing action
  rule = models.ForeignKey(Rule)

  def __create_token(self):   # use on save if no token assigned
    self.token = sha1(str(datetime.now()) + str(random())).hexdigest()

  def __set_expiration(self): # use on save if no expiration assigned
    self.expires = datetime.now() + app_settings.DEFAULT_EXPIRATION

  def __allow_perform(self, member):
    if member:
      return member in map(lambda x: x.name, Field.objects.filter(rule=self.rule))
    return True

  def can_create(self, model):
    return self.rule.action == Rule.CREATE and self.rule.get_class() == model

  def can_read(self, model, member=None):
    return self.rule.action == Rule.READ and self.rule.get_class() == model and self.__allow_perform(member)

  def can_udpate(self, model, member=None):
    return self.rule.action == Rule.UPDATE and self.rule.get_class() == model and self.__allow_perform(member)

  def can_delete(self, model):
    return self.rule.action == Rule.DELETE and self.rule.get_class() == model

  def __unicode__(self):
    return 'Token %s for user %s defined by rule \'%s\' expires on %s' % (self.token, self.user, self.rule, self.expires)
