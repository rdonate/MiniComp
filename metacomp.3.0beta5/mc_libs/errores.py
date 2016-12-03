#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################################
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
# Fichero: errores.py
#

from string import *
from types import *
import sys, os, re

#
# Errores
#

class DemasiadosErrores(Exception):
  pass

class Errores:

  def __init__(self, maximo_numero_de_errores = 20):
    self.e = []
    self.m = maximo_numero_de_errores

  def append(self, numlin, msg):
    self.e.append( (numlin, msg) )
    if len(self.e) > self.m: raise DemasiadosErrores

errores = Errores()
avisos = Errores(1000000)

try:
  _ancho_linea= int(os.getenv("COLUMNS"))
except:
  _ancho_linea= None

if not _ancho_linea:
  _ancho_linea=80

_sangria= 5

def escribe_error(f, mensaje):
  l= split(mensaje)
  pos= 0
  for i in range(len(l)):
    p= l[i]
    if i and pos< _ancho_linea:
      f.write(' ')
      pos= pos+1
    if pos+len(p)> _ancho_linea:
      f.write('\n'+' '*_sangria)
      pos= _sangria
    f.write(p.encode("utf8"))
    pos= pos+len(p)
  f.write('\n')

def muestra_errores_y_avisos():
  m = {}
  for nl, msg in errores.e:
    if m.has_key(nl): m[nl].append( ("Error:", msg) )
    else: m[nl] = [ ("Error:", msg) ]
  for nl, msg in avisos.e:
    if m.has_key(nl): m[nl].append( ("Aviso:", msg) )
    else: m[nl] = [ ("Aviso:", msg) ]
  k = m.keys()
  k.sort()
  for i in k:
    for j in m[i]:
      escribe_error(sys.stderr, u"Línea %d. %s %s" % (i, j[0], j[1]))

#
#
##############################################################################
