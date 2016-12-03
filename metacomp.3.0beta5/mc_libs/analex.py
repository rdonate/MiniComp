#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
##############################################################################
#
# metacomp 3.0beta5: a metacompiler for RLL(1) grammars
# Copyright (C) 2011 Juan Miguel Vilar and Andrés Marzal
#                    Universitat Jaume I, Castelló (Spain)
#
# This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Any questions regarding this software should be directed to:
#
#   Juan Miguel Vilar
#   Departament de Llenguatges i Sistemes Informàtics
#   Universitat Jaume I
#   E12071 Castellón (SPAIN)
#
#   email: jvilar@lsi.uji.es
#
##############################################################################
#
# Fichero: analex.py
#

from string import *

import errores
import code

import re
import REParser

##############################################################################
# Analizador Lexico
#

_codificacion = "utf-8"

def cambiaCodificacion(codificacion):
  global _codificacion
  _codificacion = codificacion

###
# Clase ComponenteLexico
#

class ComponenteLexico:

  def __init__(self, cat, nlinea):
    self.cat = cat
    self.nlinea = nlinea

  def __str__(self):
    s = []
    for k, v in self.__dict__.items():
      if k != 'cat': s.append(`k`+': '+`v`)
    if s:
      return '%s (%s)' % (prettyCat(self.cat),', '.join(s))
    else:
      return prettyCat(self.cat)

def prettyCat(c):
  """Devuelve una forma agradable de la etiqueta de categoria"""
  if c != None and c[0] == "!":
    return '"%s"' % c[1:]
  return c

###
# Clase Analizador Lexico
#

try:
  from keyword import iskeyword
except:
  _python_kwds = split("and del for is raise assert elif from lambda return " +
                       "break else global not try class except if or while " +
                       "continue exec import pass yield def finally in print")
  def iskeyword(s):
    return s in _python_kwds

class AnalizadorLexico:

  def __init__(self, entrada):
    self.esprimera= 1
    self.entrada= entrada
    self.actual= ComponenteLexico(None, 0)
    self.nlactual= 0
    self.nlfichero= 1
    self.finfichero= False
    self.buffer=[]
    self._linea = ""
    self.posLinea = 0

  def lee_especificacion_lexica(self):
    # Desde el comienzo hasta el primer \n%
    self.actual= ComponenteLexico("especificacion_lexica", 1)
    self.actual.esp= []
    erterminal= re.compile("[a-zA-Z_]*[a-zA-Z]$")
    dentro= False
    while True:
      l= self.entrada.readline().decode(_codificacion)
      if l=="":
        self.finfichero= True
        errores.errores.append(self.nlactual, u"Se ha terminado el fichero mientras leía la especificación léxica.")
        break
      self.nlactual= self.nlfichero
      self.nlfichero= self.nlfichero+1
      l= lstrip(l)
      if l=="" or l[0]=="#": continue
      if l[0]=="%":
        self.devuelve(l)
        self.nlfichero= self.nlfichero-1
        break
      l= rstrip(l)
      ee= re.split(r"[ \t]+", l)
      if len(ee)==0 or ee[0]=='': continue
      if not erterminal.match(ee[0]):
        errores.errores.append(self.nlactual, (u"Las categorías léxicas están compuestas de letras y del símbolo _ y no terminan en _"))
        continue
      if len(ee)<= 2:
        errores.errores.append(self.nlactual, (u"Cada línea de la especificación léxica debe constar de:"
                             u" identificador de categoría léxica, función de tratamiento del componente"
                             u" léxico y expresión regular."))
        continue
      else:
        if iskeyword(ee[0]):
          errores.errores.append(self.nlactual, u"El identificador de categoría léxica '%s' es una palabra reservada de Python." % ee[0])
          continue
        if ee[0]=="error":
          errores.errores.append(self.nlactual, u"La categoría error está reservada")
          continue
        if ee[0][:3]=="mc_":
          errores.errores.append(self.nlactual, u"El prefijo mc_ está reservado")
          continue
        if ee[0][-1]=="_":
          errores.errores.append(self.nlactual, u"Las categorías léxicas no pueden terminar en _")
          continue
        if ee[0] == "None":
          ee[0] = None
        er= join(ee[2:], " ")
        try:
          erAnalizada = REParser.reParse(er)
        except REParser.mc_error_abandonar:
          erAnalizada = None
        if not erAnalizada is None:
          self.actual.esp.append((ee[0], ee[1], erAnalizada))
        else:
          errores.errores.append(self.nlactual, u"La expresión '%s' está mal formada.\n" % er)
          continue
    return self.actual

  def linea(self):
    return self.nlactual

  def nuevo_caracter(self):
    if self.buffer==[]:
      if self.posLinea >= len(self._linea):
        self._linea = self.entrada.readline().decode(_codificacion)
        if self._linea == u"":
          self.finfichero = True
          return u""
        self.posLinea = 0
      c = self._linea[self.posLinea]
      self.posLinea += 1
      return c
    else:
      c= self.buffer[-1]
      del self.buffer[-1]
      return c

  def nuevo_caracter_avanzando(self):
    c= self.nuevo_caracter()
    if c=='\n':
      self.nlfichero= self.nlfichero+1
    return c

  def devuelve(self,cad):
    for l in reversed(cad):
      self.buffer.append(l)

  def sincroniza(self, sincr, enEOF):
    while self.actual.cat not in sincr and self.actual.cat!= "mc_EOF":
      self.avanza()
    if self.actual.cat=="mc_EOF" and not "mc_EOF" in sincr:
      enEOF()

  def avanza(self):
    if self.finfichero:
      self.actual= ComponenteLexico("mc_EOF", self.nlactual)
      return self.actual

    if self.esprimera:
      self.esprimera= 0
      return self.lee_especificacion_lexica()

    while True:
      c= self.nuevo_caracter()
      if c=="": # Fin de fichero
        self.nlactual= self.nlfichero
        self.actual= ComponenteLexico("mc_EOF", self.nlactual)
        return self.actual
      elif c==' ' or c=='\t' or c=='\r': # Nos cargamos el espacio en blanco
        pass
      elif c=='#': # Comentario
        while c!='\n' and c!="": c= self.nuevo_caracter()
        self.devuelve(c)
      elif c=='\n': # Nueva línea
        self.nlfichero= self.nlfichero+1
      elif c=='<': # Posible no terminal
        id = u''
        self.nlactual= self.nlfichero
        while True:
          c= self.nuevo_caracter()
          if c in letters or c=="_":
            id= id+c
          elif c=='>':
            self.actual= ComponenteLexico("noterminal", self.nlactual)
            self.actual.id= id
            if iskeyword(id):
              errores.errores.append(self.nlactual, "El no terminal %s coincide con una palabra reservada de Python." % id)
            if id[-1]== "_":
              errores.errores.append(self.nlactual, "Un no terminal no puede terminar en _")
            return self.actual
          else:
            self.devuelve(c)
            if id=='':
              errores.errores.append(self.nlactual, u"El carácter < sólo puede utilizarse para no terminales.")
              break
            errores.errores.append(self.nlactual, u"El no terminal %s no tiene el símbolo > al final" % id)
            self.actual= ComponenteLexico("noterminal", self.nlactual)
            self.actual.id= id
            return self.actual
      elif c in letters or c=="_": # Terminal
        lexema= c
        self.nlactual= self.nlfichero
        self.actual= ComponenteLexico("terminal", self.nlactual)
        self.actual.directo= False
        while True:
          c= self.nuevo_caracter()
          if c in letters or c=="_":
            lexema= lexema+c
          else:
            self.devuelve(c)
            if lexema== "error":
              self.actual= ComponenteLexico("tokenerror", self.nlactual)
            elif iskeyword(lexema):
              errores.errores.append(self.nlactual, u"Vaya, el identificador %s ya está reservado por Python." % lexema)
            if lexema[-1]=="_":
              errores.errores.append(self.nlactual, u"Un identificador de categoría léxica no puede terminar en _")
            self.actual.id= lexema
            return self.actual
      elif c=='"': # Terminal directo
        lexema= "!"
        self.nlactual= self.nlfichero
        self.actual= ComponenteLexico("terminal", self.nlactual)
        self.actual.directo= True
        while True:
          c= self.nuevo_caracter()
          if c=='"':
            self.actual.id= lexema
            return self.actual
          elif c in [" ","\t","\n"]:
            errores.errores.append(self.nlactual, 'He encontrado un terminal directo no terminado, asumire que es "%s"' % lexema[1:])
            self.devuelve(c)
            self.actual.id= lexema
            return self.actual
          lexema= lexema+c
      elif c=="@": # Posible acción
        self.nlactual= self.nlfichero
        lexema=""
        self.actual= ComponenteLexico("accion", self.nlactual)
        escape= False
        while True:
          c= self.nuevo_caracter()
          lexema= lexema+c
          if c=="@":
            if escape:
              escape= False
            else:
              self.actual.codigo= code.sentence(lexema[:-1])
              return self.actual
          elif c=="\\":
            escape= True
          elif c=="" or c=="\n":
            errores.errores.append(self.nlactual, u"La acción semántica que empieza en esta línea no está terminada.")
            self.actual.codigo = code.empty()
            if c=="\n": self.devuelve(c)
            return self.actual
          else:
            escape= False
      elif c=="$": # Error dos
        self.nlactual= self.nlfichero
        lexema=""
        self.actual= ComponenteLexico("errordos", self.nlactual)
        escape= False
        while 1:
          c= self.nuevo_caracter_avanzando()
          lexema= lexema+c
          if c=="$":
            if escape:
              escape= False
            else:
              self.actual.codigo= code.sentence(lexema[:-1])
              return self.actual
          elif c=="\\":
            escape= True
          elif c=="" or c=="\n":
            errores.errores.append(self.nlactual, u"El tratamiento de error de tipo dos de esta línea no está terminado.")
            self.actual.codigo= code.empty()
            if c=="\n": self.devuelve(c)
            return self.actual
          else:
            escape= False
      elif c=="%": # Código
        self.nlactual= self.nlfichero
        lexema=""
        self.actual= ComponenteLexico("codigo", self.nlactual)
        finlinea= False
        while True:
          c= self.nuevo_caracter_avanzando()
          lexema= lexema+c
          if (c=="%" and finlinea) or c=="":
            if c== "%":
              lexema= lexema[:-1] # Quitamos el último %
            codigo = [ code.sentence(s) for s in lexema.split("\n") ]
            codigo = reduce (lambda c,s: c.addBrother(s), codigo)
            self.actual.cod= codigo
            return self.actual
          finlinea = c == "\n"
      elif c=="-": # Posible flecha
        c= self.nuevo_caracter()
        if c==">":
          self.nlactual= self.nlfichero
          self.actual= ComponenteLexico("flecha", self.nlactual)
          return self.actual
        else:
          errores.errores.append(self.nlfichero, u"He encontrado un triste y solitario guión.")
          self.devuelve(c)
      elif c==";": # Punto y coma
        self.nlactual= self.nlfichero
        self.actual= ComponenteLexico("pyc", self.nlactual)
        return self.actual
      elif c=="*": # Asterisco
        self.nlactual= self.nlfichero
        self.actual= ComponenteLexico("asterisco", self.nlactual)
        return self.actual
      elif c=="+": # Cruz
        self.nlactual= self.nlfichero
        self.actual= ComponenteLexico("cruz", self.nlactual)
        return self.actual
      elif c=="?": # Interrogante
        self.nlactual= self.nlfichero
        self.actual= ComponenteLexico("interrogante", self.nlactual)
        return self.actual
      elif c=="|": # Barra
        self.nlactual= self.nlfichero
        self.actual= ComponenteLexico("barra", self.nlactual)
        return self.actual
      elif c=="(": # Abre paréntesis
        self.nlactual= self.nlfichero
        self.actual= ComponenteLexico("abre", self.nlactual)
        return self.actual
      elif c==")": # Cierra paréntesis
        self.nlactual= self.nlfichero
        self.actual= ComponenteLexico("cierra", self.nlactual)
        return self.actual
      else:
        errores.errores.append(self.nlfichero, u"He encontrado el carácter %s y no sé que hacer con él." % c)
#
#
##############################################################################

if __name__=="__main__":
  import sys
  f= sys.stdin
  a= AnalizadorLexico(f)
  a.avanza()
  try:
    while a.actual.cat!= "mc_EOF":
      print a.linea(),"---",a.actual
      a.avanza()
    print a.linea(),"---",a.actual
  except errores.DemasiadosErrores:
    print "Demasiados errores"
  errores.muestra_errores_y_avisos()
