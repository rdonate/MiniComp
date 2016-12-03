# -*- coding: utf-8 -*-

import errores

class TDS:
  def __init__(self):
    self.globales= {}
    self.locales= {}
    self.tactual= self.globales
    self.factual= None

  def entraFuncion(self, f):
    self.locales= {}
    self.tactual= self.locales
    self.factual= f

  def salFuncion(self):
    self.tactual= self.globales
    self.factual= None

  def existe(self, id):
    return self.tactual.has_key(id) or ( self.tactual is self.locales and self.globales.has_key(id))

  def recupera(self, id):
    if self.tactual.has_key(id):
      return self.tactual[id]
    else:
      return self.globales.get(id, None)

  def define(self, id, info, linea):
    if self.tactual.has_key(id):
      errores.semantico("Error, el identificador %s ya esta definido en este ambito." % id, linea)
    else:
      self.tactual[id]= info

  def enFuncion(self):
    return self.factual
