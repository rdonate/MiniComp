# -*- coding: utf-8 -*-

import errores

class Registro:
  def __init__(self):
    self.inicializa()

  def __setitem__(self, i, v):
    if i not in ["$zero", "$fzero"]:
      self.cambios = 1
      self.r[i] = v
      self.ultReg = i
      self.ultValor = v
    
  def __getitem__(self, i):
    if not self.r.has_key(i) or self.r[i] == None:
      raise errores.RegVacioError, i
    else:
      return self.r[i]

class RegEnteros(Registro):
  def inicializa(self):
    self.r = {}
    self.ultReg = None		# Indica el último registro modificado
    self.ultValor = None	# Indica el último valor asignado
    self.cambios = 0		# Indica si ha habido cambios en los registros enteros
    # Registros específicos enteros
    self.r["$zero"] = 0
    self.r["$sp"] = None
    self.r["$fp"] = None
    self.r["$ra"] = None
    self.r["$sc"] = None
    self.r["$a0"] = None
    self.r["$a1"] = None

class RegReales(Registro):
  def inicializa(self):
    self.r = {}
    self.ultReg = None		# Indica el último registro modificado
    self.ultValor = None	# Indica el último valor asignado
    self.cambios = 0		# Indica si ha habido cambios en los registros reales
    # Registro específicos reales
    self.r["$fzero"] = 0.0
    self.r["$fa"] = None
