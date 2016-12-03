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
# File: automaton.py
#
#   A class for automata
#

import charClass
import code

def escape(s):
  return s.replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t").replace("\"", "\\\"")

def escapeDot(s):
  return s.replace("\\", "\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t").replace("\"", "\\\"")

class Automaton:
  def __init__(self):
    self.initials = set()
    self.states = set()
    self.movements = {}
    self.finals = set()
    self.info = {}
    self.items = {}

  def addState(self, s, item):
    self.states.add(s)
    self.items[s]= item

  def getInitial(self):
    for q in self.initials:
        return q
    else:
        return None

  def makeInitial(self, s):
    self.initials.add(s)

  def makeFinal(self, s, info = None):
    self.finals.add(s)
    if info:
      self.info[s] = info

  def isFinal(self, s):
      return s in self.finals

  def numStates(self):
    return len(self.states)

  def numArcs(self):
    return len(self.movements)

  def addTransition(self, orig, cClass, end):
    if not orig in self.movements:
      self.movements[orig]= set()
    self.movements[orig].add((cClass, end))

  def deterministicParse(self, string):
      p = self.path(string)
      return len(p) == len(string) + 1 and self.isFinal(p[-1])

  def path(self, string):
      q1 = self.getInitial()
      if q1 is None:
          return []
      p = [q1]
      q = q1
      for c in string:
          if not q in self.movements:
              return p
          for (cClass,q1) in self.movements[q]:
              if cClass.contains(c):
                  q = q1
                  p.append(q)
                  break
          else:
              return p
      else:
          return p
      return p

  def compactArcs(self):
    for q in self.states:
      if not q in self.movements:
        continue
      dest = {}
      for cClass, end in self.movements[q]:
        if not end in dest:
          dest[end] = charClass.empty
        dest[end] = dest[end] | cClass
      self.movements[q] = set()
      for end in dest:
        if not dest[end].isEmpty():
          self.movements[q].add((dest[end], end))

  def toDot(self, showItems = True, prologue = None):
    r=[]
    r.append(u'digraph re2a{')
    if prologue == None:
      prologue = [u'size = "10,7.5"', u'rotate = 90;']
    r.extend(prologue)
    r.append(u'  rankdir = "LR";')
    r.append(u'  node [shape = "ellipse"];')
    r.append(u'  "falso" [shape = plaintext, label = "", width = 0.001, height = 0.001];')
    for q in self.states:
      if showItems:
          aux= u'  %d [ label = "%s' % (q, escapeDot(unicode(self.items[q])))
          aux+= u'"'
          if q in self.finals:
            aux+= u", peripheries = 2"
          aux+= u"];"
          r.append(aux)
      elif q in self.finals:
          aux= u'  %d [ peripheries = 2 ];' % q
          r.append(aux)
      if q in self.initials:
        r.append(u'  falso -> %d;' % q)
      if q in self.movements:
        for (cClass, end) in self.movements[q]:
          r.append(u'  %d -> %d [ label = "%s" ];' % (q,end,escape(unicode(cClass))))
    r.append(u'}')
    return u"\n".join(r)

  def __str__(self):
    r= ""
    for q in self.states:
      r+= "State %s" % q
      if q in self.initials:
        r+= " i=1"
      if q in self.finals:
        r+= " f=1"
      r+="\n"
      if q in self.movements:
        for (cClass, end) in self.movements[q]:
          r+= "%s\t%s\t\"%s\"\n" % (q,end,escape(unicode(cClass)))
    return r

  def toCode(self, name, isMethod = False):
    if isMethod:
      header = code.sentence("def %s(self, i, s):" % name)
    else:
      header = code.sentence("def %s(i, s):" % name)
    q = self.getInitial()
    if q is None:
      return (header // "return False").code()
    body = code.sentence("q = %s" % q)
    if self.isFinal(q):
      (body / ("uf = %d" % q)
            / "ufi = i")
    else:
      (body / "uf = None"
            / "ufi = None")

    loop = (code.sentence("while i <= len(s):")
                         // "if i == len(s):"
                         //    "c = ''"
                         %  "else:"
                         //    "c = s[i]"
            ).code()
    body / loop

    stateActions = []
    for q in self.states:
      action = code.empty()
      if self.isFinal(q):
        action / ("uf = %s" % self.info[q]) / "ufi = i"
      if q in self.movements:
        intervals = []
        for (cClass, end) in self.movements[q]:
          intervals += [ (interval[0], interval[1], code.sentence("q = %d" % end)) for interval in cClass.toIntervals() ]
        intervals.sort()
        testChar = code.intervalSearch(intervals, "c", "break", lambda c: unichr(ord(c)-1))
      else:
        testChar = "break"
      action / testChar
      stateActions.append(action)
    (loop // code.binarySearch(stateActions, "q")
           / "i += 1")
    body / "return (uf, ufi)"

    return header // body

