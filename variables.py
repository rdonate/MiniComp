# -*- coding: utf-8 -*-
import tipos

class Variable:
  def __init__(self, id, tipo, local, nlinea):
    self.id= id
    self.tipo= tipo
    self.\
      local= local
    self.nlinea= nlinea

  def talla(self):
    return self.tipo.talla()

  def fijaDireccion(self, dir):
    self.dir= dir
    if self.local:
      self.base= "fp"
    else:
      self.base= "zero"

  def __str__ (self):
    return "%s (tipo: %s; local: %s)" % (self.id, self.tipo, self.local)
