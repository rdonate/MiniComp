# -*- coding: utf-8 -*-

class Tipo:
  def __init__(self):
    pass

  def __ne__(self, otro):
    return not self.__eq__(otro)

  def talla(self):
    return self.tamanyo

class Elemental(Tipo):
  def __init__(self, nombre):
    self.nombre= nombre
    self.tamanyo= 1

  def __eq__(self, otro):
    return self.nombre== otro.nombre

  def __str__(self):
    return self.nombre

  def elemental(self):
    return True

Entero= Elemental("Entero")
Cadena= Elemental("Cadena")
Real = Elemental("Real")
Logico= Elemental("Logico")
Error= Elemental("Error")

class Array(Tipo):
  def __init__(self, rango, base):
    self.nombre= "Array"
    self.base= base
    self.rango= rango
    self.tamanyo= rango*base.talla()

  def __eq__(self, otro):
    return otro.nombre== self.nombre and \
           otro.rango== self.rango and otro.base== self.base

  def __str__(self):
    return "array [%s] de %s" % ( self.rango, self.base)

  def elemental(self):
    return False

class _Funcion(Tipo):
  def __init__(self):
    self.nombre= "Funcion"

  def __eq__(self, otro):
    return self.nombre== otro.nombre

  def __str__(self):
    return "Funcion"

  def elemental(self):
    return False

Funcion= _Funcion()

def igualOError(t1, t2):
  return t1== Error or t2== Error or t1==t2
