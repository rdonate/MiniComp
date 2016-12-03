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
# File: Nodes.py
#
# Nodes for representing regular expresions with marks
#

import charClass

_markedChar = u"·"

def ensureParent(s):
  """Returns s with parethensis only if it does not already have them"""
  if s[0]!= "(" or s[-1]!= ")":
    return "(%s)" % s
  else:
    return s

def _mixMovements(s1, s2):
    r = s2
    aux = set()
    for c1 in s1:
        r2 = set()
        for c2 in r:
            i = c1 & c2
            c1 = c1 - i
            c2 = c2 - i
            for e in (i, c2):
                if not e.isEmpty():
                    r2.add(e)
        r = r2
        if not c1.isEmpty():
          aux.add(c1)
    return r | aux

class Node:
  """Base class for the rest of the nodes"""
  def __unicode__(self):
    return "__unicode__ method for %s not implemented" % self.__class__.__name__

  def __hash__(self):
    return hash(unicode(self))

  def __eq__(self, other):
    return unicode(self) == unicode(other)

  def isEmpty(self):
    """Returns True if the expression accepts the emtpy string"""
    return self._empty

  def isFinal(self):
    """Returns True if the expression has a mark at the end"""
    return self._final

  def category(self):
    """Returns the category associated to the current marks or None if
    isFinal is False"""
    return self._category

  def shift(self, mark, charClass):
    """Moves the mark according to the characters in the class"""
    pass

  def movements(self):
    """The movements that are possible given the marks"""
    return set()

class OrNode(Node):
  """The or operator"""
  def __init__(self, l):
    self.l= l
    for e in l:
      if e.isEmpty():
        self._empty = True
        break
    else:
      self._empty = False
    for e in l:
      if e.isFinal():
        self._final = True
        break
    else:
      self._final = False
    if self._final:
      self._category = min([ e.category() for e in l ])
    else:
      self._category = None

  def shift(self, mark, charClass):
    return OrNode([ e.shift(mark, charClass) for e in self.l ])

  def movements(self):
    m = set()
    for e in self.l:
      m = _mixMovements(m, e.movements())
    return m

  def __unicode__(self):
    return ensureParent(u"|".join([unicode(child) for child in self.l]))

class Concatenation(Node):
  """The concatenation operator"""
  def __init__(self, lhs, rhs):
    self.lhs= lhs
    self.rhs= rhs
    self._empty = lhs.isEmpty() and rhs.isEmpty()
    self._final = lhs.isFinal() and rhs.isEmpty() or rhs.isFinal()
    if self._final:
      if lhs.isFinal() and rhs.isEmpty():
        self._category = min(lhs.category(), rhs.category())
      else:
        self._category = rhs.category()
    else:
      self._category = None

  def shift(self, mark, charClass):
    l = self.lhs.shift(mark, charClass)
    r = self.rhs.shift(mark and l.isEmpty() or l.isFinal(), charClass)
    return Concatenation(l, r)

  def movements(self):
    return _mixMovements(self.lhs.movements(), self.rhs.movements())

  def __unicode__(self):
    return u"%s%s" % (self.lhs,self.rhs)

class Closure(Node):
  """The closure operator. If positive is True, represents Kleene closure"""
  def __init__(self, exp, positive):
    self.exp= exp
    self.positive= positive
    self._empty = not self.positive or exp.isEmpty()
    self._final = exp.isFinal()
    if self._final:
      self._category = exp.category()
    else:
      self._category = None

  def shift(self, mark, charClass):
    e = self.exp.shift(mark, charClass)
    if not mark and e.isFinal():
        e = self.exp.shift(True, charClass)
    return Closure(e, self.positive)

  def movements(self):
    return self.exp.movements()

  def __unicode__(self):
    return ensureParent(unicode(self.exp)) + (self.positive and u"+" or u"*")

class Optional(Node):
  """Represents the ? operator"""
  def __init__(self, exp):
    self.exp= exp
    self._empty = True
    self._final = exp.isFinal()
    if self._final:
      self._category = exp.category()
    else:
      self._category = None


  def shift(self, mark, charClass):
    return Optional(self.exp.shift(mark, charClass))

  def movements(self):
    return self.exp.movements()

  def __unicode__(self):
    return ensureParent(unicode(self.exp))+u"?"

class SymbolSet(Node):
  """A set of symbols, represented by a character class. The symbolic representation
  is used for printing. For instance, a single symbol can be [a] but is symbolic representation
  will be only a."""
  def __init__(self, charClass, symbolic, marked= False, final= False):
    self.charClass= charClass
    self.symbolic= symbolic
    self.marked= marked
    self._final= final
    self._empty = self.charClass.isEmpty()
    self._category = None

  def shift(self, mark, charClass):
    return SymbolSet(self.charClass, self.symbolic, mark, self.marked and not (self.charClass & charClass).isEmpty())

  def movements(self):
    if self.marked:
      return set([self.charClass])
    else:
      return set()

  def __unicode__(self):
    if self.marked:
      return _markedChar + self.symbolic
    else:
      return self.symbolic

class EmptyString(Node):
  """The empty string"""
  def __init__(self, symbolic):
    self.symbolic= symbolic
    self._empty = True
    self._final = False
    self._category = None

  def shift(self, mark, charClass):
    return self

  def __unicode__(self):
    return self.symbolic

class EmptySet(Node):
  """The empty set. Generates the empty language"""
  def __init__(self, symbolic):
    self.symbolic= symbolic
    self._empty = False
    self._final = False
    self._category = None

  def shift(self, mark, charClass):
    return self

  def __unicode__(self):
    return self.symbolic

class End(Node):
  """An empty string representing the end of the expression. Used
  as placeholder when transforming an expression to an automaton"""
  def __init__(self, marked = False):
    self.marked = marked
    self._empty = True
    self._final = marked
    self._category = None

  def shift(self, mark, charClass):
    return End(mark)

  def __unicode__(self):
    if self.marked:
      return _markedChar
    else:
      return u""

class Category(Node):
  """An empty string representing a category"""
  def __init__(self, info, marked = False):
    self.marked = marked
    self._empty = True
    self._final = marked
    self.info = info
    if self._final:
      self._category = info
    else:
      self._category = None

  def shift(self, mark, charClass):
    return Category(self.info, mark)

  def __unicode__(self):
    if self.marked:
      r = _markedChar
    else:
      r = u""
    r += u"#%s#" % self.info
    return r
