#/usr/bin/env python
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
###############################################################################
#
# Fichero: tabla.py
#
# Tabla de símbolos para metacomp
#

from gramatica import *;

class Tabla:
  def __init__(self):
    self.noterminales= {}
    self.terminales= {}

  def noterminal(self, id, nl):
    if not self.noterminales.has_key(id):
      nt= NoTerminal(id, nl)
      self.noterminales[id]= nt
    return self.noterminales[id]

  def listaterminales(self):
    l= self.terminales.keys()
    l.sort()
    r= []
    for i in l:
      r.append(self.terminales[i])
    return r

  def listanoterminales(self):
    l= self.noterminales.keys()
    l.sort()
    r= []
    for i in l:
      r.append(self.noterminales[i])
    return r
