# -*- coding: utf-8 -*-
# File: code.py
#
##############################################################################
#
# code.py: a module for helping in generating Python code
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
##############################################################################
#

def _ensureCode(code):
    if not isinstance(code, _Code):
        if isinstance(code, basestring):
            code = _Code(code)
        elif isinstance(code, _CodeControl):
            code = code.code()
        else:
            raise Exception("Don't know how to transform %s in code" % code)
    return code

class _Code:
    offset = " " * 4

    def __init__(self, head = None):
        self.head = head
        self.children = []
        self.brothers = [self]

    def __div__(self, code):
        control = _CodeControl(self)
        return control / code

    def __floordiv__(self, code):
        control = _CodeControl(self)
        return control // code

    def addChild(self, code):
        self.brothers[-1].children.append(_ensureCode(code))
        return self

    def addBrother(self, code):
        self.brothers.append(_ensureCode(code))
        return self

    def _toList(self, indent):
        if self.head:
            r= [indent + self.head]
            r.extend(sum([ c._toList(indent + _Code.offset) for c in self.children ], []))
        else:
            if self.children:
                r = sum([ c._toList(indent) for c in self.children ], [])
            elif not self.brothers:
                r = [ indent + u"pass" ]
            else:
                r = []
        for b in self.brothers[1:]:
            r.extend(b._toList(indent))
        return r

    def __unicode__(self):
        return u"\n".join(self._toList(u""))

    def __str__(self):
        return unicode(self)

class _CodeControl:
    def __init__(self, code):
        self.path = [code]

    def code(self):
        return self.path[0]

    def __div__(self, code):
        self.path[-1].addBrother(code)
        return self

    def __mod__(self, code):
        self.path.pop()
        if code != None:
            self.path[-1].addBrother(code)
        return self

    def __floordiv__(self, code):
        code = _ensureCode(code)
        self.path[-1].addChild(code)
        self.path.append(code)
        return self

def empty():
    """Returns an empty sentence"""
    return _Code()

def sentence(s):
    """Returns a sentence using s"""
    return _Code(s)

def binarySearch(actions, variable, left = 0, right = None):
    """Returns code that executes actions[variable], where
    actions contains code segments. The search uses binary search,
    it is assumed that the variable is in range(left, right), if right is
    None, it is changed to len(actions)."""
    if right is None:
        right = len(actions)
    if right-left == 1:
        return actions[left]
    center = (right+left) // 2
    return (sentence(u"if %s < %d:" % (variable, center))
            // binarySearch(actions, variable, left, center)
            % u"else:"
            // binarySearch(actions, variable, center, right)
            ).code()

def _intervalTest(variable, interval, default, lower, upper):
    begin, end, action = interval
    if begin == lower:
        begin = None
    if end == upper:
        end = None
    if begin is None and end is None:
        return action
    if begin is None:
        test = "%s <= %s" % (variable, repr(end))
    elif end is None:
        test = "%s <= %s" % (repr(begin), variable)
    elif begin == end:
        test = "%s == %s" % (repr(begin), variable)
    else:
        test = "%s <= %s <= %s" % (repr(begin), variable, repr(end))
    s = sentence(u"if %s:" % test) // action
    if default != None:
        (s % u"else:"
           // default)
    return s.code()

def intervalSearch(intervals, variable, default = None, prev = None, lower = None, upper = None):
    """Returns code that executes the action associated to the interval
    that contains the variable. If no interval contains the value of variable,
    the default code is executed if is different begin None, otherwise nothing
    is done. The list intervals contais a sorted list of triples in which each
    triple is of the form (begin, end, action) where action is to be executed if
    begin <= variable <= end. If begin is None, action is executed when variable <= end,
    if end is None, action is executed if begin <= variable. It is assumed that
    the intervals do not overlap. Lower and upper are bounds on the value of the
    variable. If prev is not none it is used to compute a more acurate upper bound
    after a test of the form variable < limit."""
    if len(intervals) == 0:
        return default
    if len(intervals) == 1:
        return _intervalTest(variable, intervals[0], default, lower, upper)
    center = len(intervals)//2
    left = intervals[:center]
    right = intervals[center:]
    limit = intervals[center][0]
    if prev == None:
        newUpper = limit
    else:
        newUpper = prev(limit)
    return (sentence (u"if %s < %s:" % (variable, repr(limit)))
            // intervalSearch(left, variable, default, prev, lower, newUpper)
            % u"else:"
            // intervalSearch(right, variable, default, prev, limit, upper)
           ).code()
