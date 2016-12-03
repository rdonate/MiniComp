# -*- coding: latin1 -*-

from types import *
import errores

class Memoria:
  def __init__(self):
    self.inicializa()

  def inicializa(self):
    self.m = {}
    self.ultDir = -1		# Última dirección modificada
    self.ultValor = None	# Último valor asignado
    self.cambios = 0		# Indica si ha habido algún cambio en la memoria

  def __setitem__(self, d, v):
    if d < 0:
      raise errores.MemDirNegError, d
    else:
      self.cambios = 1
      self.m[d] = v
      self.ultDir = d
      self.ultValor = v

  def getEntero(self, d):
    if not self.m.has_key(d):
      raise errores.MemAccesoError, d
    elif not type(self.m[d]) in [IntType, LongType]:
      raise errores.MemEnteroError, d
    else:
      return self.m[d]

  def getReal(self, d):
    if not self.m.has_key(d):
      raise errores.MemAccesoError, d
    elif not type(self.m[d]) == FloatType:
      raise errores.MemRealError, d
    else:
      return self.m[d]
