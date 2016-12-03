# -*- coding: utf-8 -*-
##############################################################################
#
# metacomp 3.0beta5: a metacompiler for RLL(1) grammars
# Copyright (C) 2011 Juan Miguel Vilar
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
# File: re2a.py
#
#   A converter from regular expresions to automata
#

import sys

from automaton import Automaton

def re2a(er, trace = False):
  S= Automaton()
  name= {}

  q0= er.shift(True, None)
  name[q0]= 0
  nq0= name[q0]
  if trace:
    sys.stderr.write("Initial state: %d\nItems:\n%s\n" % (nq0, q0))
  S.addState(nq0, q0)
  S.makeInitial(nq0)
  if q0.isFinal():
    S.makeFinal(nq0, q0.category())

  pending=set([q0])
  while len(pending)!= 0:
    q= pending.pop()
    nq= name[q]
    for charClass in q.movements():
      d = q.shift(False, charClass)
      if not name.has_key(d):
        pending.add(d)
        name[d]= len(name)
        nd= name[d]
        S.addState(nd, d)
        if trace:
          sys.stderr.write("Added state: %d%s, from %d with class %s\nItems:\n%s\n" % (nd, d.isFinal() and " (final)" or "", nq, charClass, d))
        if d.isFinal():
          S.makeFinal(nd, d.category())
      nd= name[d]
      S.addTransition(nq, charClass, nd)
  S.compactArcs()
  return S
