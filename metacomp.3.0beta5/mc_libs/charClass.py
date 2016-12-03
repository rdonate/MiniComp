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
# File: charClass.py
#
# Class for manipulating character classes
#

def _normalize(intervals):
    """Normalizes the list of intervals so that they are ordered by their first
    component and do not overlap"""
    if len(intervals) == 0:
        return intervals
    r = [] # result
    s = sorted(intervals)
    current = s[0]
    for i in s[1:]:
        if current[1] < _prev(i[0]):
            # No overlap, add current
            r.append(current)
            current = i
        elif current[1] < i[1]:
            # current and i overlap, merge current and i
            current = (current[0], i[1])
        # else current contains i, do nothing
    r.append(current)
    return r

def _intersect(l1, l2):
    """Computes the intersection of two normalized lists of intervals"""
    i1 = i2 = 0
    r = []
    while i1 < len(l1) and i2 < len(l2):
        c1 = l1[i1]
        c2 = l2[i2]
        if c1[1] <= c2[1]:
            i1+= 1
        else:
            i2+= 1
        if c1[0] > c2[0]:
            c1, c2 = c2, c1
        if c1[1] < c2[0]:
            pass
        elif c1[1] <= c2[1]:
            r.append((c2[0], c1[1]))
        else:
            r.append(c2)
    return r

def _next(c):
    return unichr(ord(c)+1)

def _prev(c):
    return unichr(ord(c)-1)

def _mixIntersect(positive, negative):
    """Computes the intersection of a positive and negative lists of
    intervals, both normalized"""
    r = []
    posn = 0
    for p in positive:
        while posn < len(negative) and negative[posn][0] <= p[1]:
            pn = negative[posn]
            if pn[1] < p[0]:
                posn+= 1
                continue
            ls = _prev(pn[0])
            if ls >= p[0]:
                r.append((p[0],ls))
            p = (_next(pn[1]), p[1])
            if p[0]> p[1]:
                break
            posn += 1
        if p[0] <= p[1]:
            r.append(p)
    return r

def _escape(c):
    if c == u"\n":
        c = u"\\n"
    elif c == u"\t":
        c = u"\\t"
    elif c == u"\\":
        c = u"\\\\"
    return c


class CharClass:
    def __init__(self, positive, intervals):
        self.positive = positive
        self.intervals = _normalize(intervals)

    def contains(self, c):
        for c1, c2 in self.intervals:
            if c1 <= c <= c2:
                found = True
                break
        else:
            found = False
        if self.positive:
            return found
        else:
            return not found

    def __hash__(self):
        return hash(unicode(self))

    def __eq__(self, other):
        return unicode(self) == unicode(other)

    def isEmpty(self):
        return len(self.intervals) == 0 and self.positive

    def union(self, other):
        if self.positive and other.positive:
            return CharClass(self.positive, self.intervals + other.intervals)
        else:
            return self.complement().intersection(other.complement()).complement()

    def __or__(self, other):
        return self.union(other)

    def intersection(self, other):
        if self.positive and other.positive:
            return CharClass(self.positive, _intersect(self.intervals, other.intervals))
        elif self.positive and not other.positive:
            return CharClass(self.positive, _mixIntersect(self.intervals, other.intervals))
        elif not self.positive and other.positive:
            return CharClass(other.positive, _mixIntersect(other.intervals, self.intervals))
        else:
            return self.complement().union(other.complement()).complement()

    def __and__(self, other):
        return self.intersection(other)

    def complement(self):
        return CharClass(not self.positive, self.intervals)

    def difference(self, other):
        return self.intersection(other.complement())

    def toCode(self, variable):
        if len(self.intervals) == 0:
            if self.positive:
                return u"False"
            else:
                return u"True"
        if len(self.intervals) == 1 and self.intervals[0][0] == self.intervals[0][1]:
            if self.positive:
                return u"%s == %s" % (variable, repr(self.intervals[0][0]))
            else:
                return u"%s != %s" % (variable, repr(self.intervals[0][0]))
        l = []
        for a, b in self.intervals:
            if a == b:
                l.append(u"%s == %s" % (variable, repr(a)))
            else:
                l.append(u"%s <= %s <= %s" % (repr(a), variable, repr(b)))
        code = u" or ".join(l)
        if not self.positive:
            code = u"not (%s)" % code
        return code

    def toIntervals(self):
        """Returns a list of intervals adequate for code.intervalSearch"""
        if self.positive:
            return self.intervals[:]
        else:
            prev = None
            l = []
            for a,b in self.intervals:
                l.append((prev, unichr(ord(a)-1)))
                prev = unichr(ord(b)+1)
            l.append((prev, None))
            return l

    def __sub__(self, other):
        return self.difference(other)

    def __str__(self):
        if len(self.intervals) == 0:
            if self.positive:
                return u"<empty>"
            else:
                return u"."
        if self.positive and len(self.intervals) == 1 and self.intervals[0][0] == self.intervals[0][1]:
            return _escape(self.intervals[0][0])
        if self.positive:
            r = u"["
        else:
            r = u"[^"
        for a, b in self.intervals:
            if a == u"]" or b == u"]":
                r+= u"]"
                break
        for a, b in self.intervals:
            if a == u"]" or a == u"-":
                a = _next(a)
            if b == u"]" or b == u"-":
                b = _prev(b)
            if a < b:
                if a < _prev(b):
                    r+= u"%s-%s" % (_escape(a), _escape(b))
                else:
                    r+= u"%s%s" % (_escape(a), _escape(b))
            elif a == b:
                r+= u"%s" % _escape(a)
        for a, b in self.intervals:
            if a == u"-" or b == u"-":
                r+= u"-"
                break
        r+= u"]"
        return r

empty = CharClass(True, [])
full = empty.complement()

