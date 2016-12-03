##############################################################################
#
# verArbol 0.6: a simple tree visualizer
# Copyright (C) 2010 Juan Miguel Vilar
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
# Fichero: vAnalizador.mc
#
# Analizador de verArbol.py
#

cadena	trataCadena	"([^"\n]|"")*"
fondo	None		fondo
tinta	None		tinta
None	None		[ \t\n]+
corchete None		\]
#"
%

class Info:
  def __init__(self):
    self.fondo= None
    self.tinta= None
    self.raiz= []
    self.hijos= []

_nombres= {
  "mc_EOF": "fin de la entrada",
  "cadena": "literal de cadena",
  "corchete": "corchete cerrado",
  "fondo": "color de fondo",
  "tinta": "color de tinta",
  "!(": "paréntesis abierto",
  "!)": "paréntesis cerrado"
}

def trataCadena (cad):
  cad.cad= string.replace(cad.lexema[1:-1], '""', '"')

def error_lexico(linea, cadena):
  if len(cadena)==1:
    error("Carácter %s inesperado en línea %d." % (repr(cadena), linea))
  else:
    error("Caracteres %s inesperados en línea %d." % (repr(cadena[:10]), linea))

class vAExcepcion(Exception):
  def __init__(self, mensaje):
    self.mensaje= mensaje

  def __str__(self):
    return self.mensaje

def error(mensaje):
  raise vAExcepcion(mensaje)

def error_sintactico(encontrado, esperado, linea):
  n1= _nombres[encontrado.cat]
  n2= " o un ".join([ _nombres[t] for t in esperado])
  error("En la línea %d, he encontrado un %s donde esperaba un %s"%
        (linea, n1, n2))
%

<Entrada> -> @Arbol.nivel= 0@
             <Arbol> @Entrada.arboles=[Arbol.arbol]@
             ( @Arbol2.nivel=0@
               <Arbol> @Entrada.arboles.append(Arbol2.arbol)@)* ;

<Entrada> -> error
              @error_sintactico(mc_al.actual, mc_t, mc_al.linea())@
	    ;

<Arbol> -> "(" @info=Info()@
               (
                 <Fondo> @info.fondo= Fondo_.color@ (<Tinta> @info.tinta= Tinta_.color@)?
               | <Tinta> @info.tinta= Tinta_.color@ (<Fondo> @info.fondo= Fondo_.color@)?
               )?
	       cadena @info.raiz= [cadena.cad]@
              (cadena @info.raiz.append(cadena_.cad)@)*
              ( @Arbol1.nivel= Arbol.nivel+1@
                <Arbol> @info.hijos.append(Arbol1.arbol)@ )*
              @Arbol.arbol= info@
           ")" ;

<Arbol> -> error
            @if mc_al.actual.cat=="corchete": @
            @  if Arbol.nivel:                @
            @    return                       @
            @  else:                          @
            @    mc_al.avanza()               @
	    @else:                            @
            @  error_sintactico(mc_al.actual, mc_t, mc_al.linea())@
           ;

<Fondo> -> fondo "(" cadena ")" @Fondo.color= cadena.cad@;

<Tinta> -> tinta "(" cadena ")" @Tinta.color= cadena.cad@;
