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
# File: REParser.mc
#
# Parser for re2a
#

# Uncomment next line for using <empty> or ø as empty set
# emptySet	None	<empty>|\ø
emptyString	None	\(\)
emptyString	None	\λ
set	processSet	\[(\^?(-|\]))?((\\[^\n\t]|[^-\]\n\t\\])(-(\\[^\n\t]|[^-\]\n\t\\]))?)+-?\]
set     processSet	\[\^?(-|\])\]
set	processDot	\.
# Uncomment next line for using <..> symbols:
# sym	processSym	<[a-zA-Z0-9]+>
sym	processEscape	\\[^\n]
sym	processSym	[^\[\]\n\\]
None	None	\n

%

import erNodes
import charClass

def processCount(c):
  l = c.lexema[1:-1].split(",")
  if len(l) == 2:
    c.min = int(l[0])
    c.max = int(l[1])
  else:
    c.min = int(l[0])
    c.max = c.min

def processEscape(c):
  if c.lexema not in [r"\n", r"\t"]:
    c.value= c.lexema[1:]
  elif c.lexema== r"\n":
    c.value = "\n"
  elif c.lexema== r"\t":
    c.value = "\t"

def processSym(c):
  c.value= c.lexema

def processDot(cl):
  cl.charClass = charClass.full

def processSet(cl):
  s= cl.lexema[1:-1]
  if s[0]== u"^":
    i= 1
  else:
    i= 0
  l= []
  while i< len(s):
    if s[i] == u"\\":
      if s[i+1] == u"n":
        l.append((u"\n", u"\n"))
      elif s[i+1] == "t":
        l.append((u"\t", u"\t"))
      else:
        l.append((s[i+1], s[i+1]))
      i+= 2
    elif i< len(s)-2 and s[i+1]== u'-':
      l.append((s[i], s[i+2]))
      i+= 3
    else:
      l.append((s[i], s[i]))
      i+= 1
  cl.charClass = charClass.CharClass(s[0]!= u"^", l)
##  print cl.charClass

def error_lexico(nlinea, c):
  mc_abandonar()

def reParse(s):
  return AnalizadorSintactico(s).RE.exp

__needEscape = set(["\\", "(", ")", "[", "]", "+", "*", "|", "?", ".", "λ"])

def escapeChar(c):
  if c in __needEscape:
    return "\\" + c
  else:
    return c

def stringAsRE(s):
  if s == "":
    return erNodes.EmptyString("λ")
  else:
    ers = [ erNodes.SymbolSet(charClass.CharClass(True, [(c,c)]), escapeChar(c)) for c in s ]
    return reduce(lambda x, y: erNodes.Concatenation(x,y), ers)


%
$self.RE.exp= None$

<RE> -> @RE.exp= None@ <E> @RE.exp= E.exp@ ;

<RE> -> error @RE.exp= None@
              @mc_abandonar()@
        ;

<E> -> <T> @l= [T.exp]@
       ( "|" <T> @l.append(T2.exp)@
       )*
       @if len(l)== 1:@
       @  E.exp= l[0]@
       @else:@
       @  E.exp= erNodes.OrNode(l)@
       ;
<T> -> <F> @exp= F.exp@
       ( <F> @exp= erNodes.Concatenation(exp, F2.exp)@
       )*
       @T.exp= exp@
       ;
<F> -> <B> @exp= B.exp@
       ( "*" @exp= erNodes.Closure(exp, False)@
       | "+" @exp= erNodes.Closure(exp, True)@
       | "?" @exp= erNodes.Optional(exp)@
       )*
       @F.exp= exp@
       ;
<B> -> "(" <E> ")" @B.exp= E.exp@
       | sym @B.exp= erNodes.SymbolSet(charClass.CharClass(True, [(sym.value, sym.value)]), sym.lexema)@
       | set @B.exp= erNodes.SymbolSet(set.charClass, set.lexema)@
       | emptyString @B.exp= erNodes.EmptyString(emptyString.lexema)@
       | emptySet @B.exp= erNodes.EmptySet(emptySet.lexema)@
       ;
