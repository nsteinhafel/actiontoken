from datetime import datetime
from hashlib import sha1
from random import random

from django.contrib.auth.models import User
from django.db import models

import app_settings

class Token(models.Model):
  token = models.CharField(max_length=40)
  expires = models.DateTimeField()
  user = models.ForeignKey(User) # user performing action
  
  # use on save if no token assigned
  def __create_token(self):
    self.token = sha1(str(datetime.now()) + str(random())).hexdigest()

  # use on save if no expiration assigned
  def __set_expiration(self):
    self.expires = datetime.now() + app_settings.DEFAULT_EXPIRATION

  def can_create(self, model, field=None):
    return any(rule.can_create(model, field) for rule in Rule.objects.filter(token=self))

  def can_read(self, model, field=None):
    return any(rule.can_create(model, field) for rule in Rule.objects.filter(token=self))

  def can_udpate(self, model, field=None):
    return any(rule.can_create(model, field) for rule in Rule.objects.filter(token=self))

  def can_delete(self, model, field=None):
    return any(rule.can_create(model, field) for rule in Rule.objects.filter(token=self))


  def save(self, *args, **kwargs):
    if not self.token:
      self.__create_token()
    if not self.expires:
      self.__set_expiration()
    super(Token, self).save(*args, **kwargs)

  def __unicode__(self):
    return 'Token %s for user %s defined by rules \'%s\' expires on %s' % (self.token,
      self.user, 
      ' '.join(unicode(rule) for rule in Rule.objects.filter(token=self)),
      self.expires)

class InvalidModelName(Exception):
  pass

class Rule(models.Model):
  model = models.TextField()
  token = models.ForeignKey(Token)

  def can_create(self, model, field=None):
    if field:
      return any(field.can_create() for field in Field.objects.filter(rule=self).filter(name=field))
    return self.rule.get_class() == model and any(action.is_create() for action in Action.objects.filter(rule=self))

  def can_read(self, model, field=None):
    if field:
      return any(field.can_read() for field in field.objects.filter(rule=self).filter(name=field))
    return self.rule.get_class() == model and any(action.is_read() for action in Action.objects.filter(rule=self))

  def can_udpate(self, model, field=None):
    if field:
      return any(field.can_update() for field in field.objects.filter(rule=self).filter(name=field))
    return self.rule.get_class() == model and any(action.is_update() for action in action.objects.filter(rule=self))

  def can_delete(self, model, field=None):
    if field:
      return any(field.can_delete() for field in field.objects.filter(rule=self).filter(name=field))
    return self.rule.get_class() == model and any(action.is_delete() for action in action.objects.filter(rule=self))


  def is_class(self):
    return isinstance(self.get_class(), type)

  # revisit this later
  def get_class(self):
    import_dict = self.model.rsplit('.', 1)
    if not len(import_dict) == 2:
      raise InvalidModelName('Model could not be imported (is it fully qualified?).')
    return getattr(__import__(import_dict[0], fromlist=[import_dict[1]]), import_dict[1])

  def __unicode__(self):
    return '%s' % self.model

class Field(models.Model):
  name = models.TextField()
  rule = models.ForeignKey(Rule)

  def can_create(self):
    return any(action.is_create() for action in Action.objects.filter(field=self))

  def can_read(self):
    return any(action.is_read() for action in Action.objects.filter(field=self))

  def can_udpate(self):
    return any(action.is_update() for action in action.objects.filter(field=self))

  def can_delete(self):
    return any(action.is_delete() for action in action.objects.filter(field=self))

  def is_field(self):
    return self.name in map(lambda x: x.name, self.rule.get_class()._meta.fields)

  def __unicode__(self):
    return 'field(%s on %s)' % (' '.join(unicode(action) for action in action.objects.filter(field=self)), self.name)

class Action():
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
  rule = models.ForeignKey(Rule)
  field = models.ForeignKey(Field)

  def is_create(self):
    return self.action == CREATE

  def is_read(self):
    return self.action == READ

  def is_update(self):
    return self.action == UPDATE

  def is_delete(self):
    return self.action == DELETE

  def __unicode__(self):
    return dict(ACTIONS)[action]
