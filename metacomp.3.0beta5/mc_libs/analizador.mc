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
# Fichero: analizador.mc
#

# No hay analizador léxico, se especificará en la entrada

%

#
# Módulos:
#

import generador
import REParser
import code

from gramatica import *
from tabla import Tabla
from errores import errores, avisos

#
# Variables globales:
#

T= Tabla()           # Tabla de símbolos
directos= set()      # Terminales directos encontrados
enparentesis= False  # Cierto si estamos dentro de paréntesis

_nombre={
    "abre" : u"un paréntesis abierto",
    "accion" : u"una acción semántica",
    "asterisco" : "un asterisco",
    "barra" : "una barra",
    "cierra" : u"un paréntesis cerrado",
    "codigo" : u"un segmento de código",
    "cruz" : "una cruz",
    "errordos" : "un tratamiento de error",
    "especificacion_lexica" : u"una especificación léxica",
    "flecha" : "una flecha",
    "interrogante" : "un interrogante",
    "mc_EOF" : "el fin de fichero",
    "noterminal" : u"un símbolo no terminal",
    "pyc" : "un punto y coma",
    "terminal" : u"un símbolo terminal",
    "tokenerror" : 'una palabra reservada "error"'
  }

%

#
# Producción global:
#

<Compilador> ->
         @Compilador.abandonar = True@
       especificacion_lexica
         $import analex$
         $codigo=analex.ComponenteLexico("codigo", mc_al.linea())$
         $codigo.cod= code.empty()$
       codigo
         @Lineas.codusuario= codigo.cod@
         @tratEOF.codigo= None@
       <tratEOF>
         @Lineas.l= []@
       <Lineas>
         @Compilador.abandonar = False@
         @lexica= [ (td, None, REParser.stringAsRE(td[1:])) for td in directos ]@
	 @lexica+= especificacion_lexica.esp@
	 @Compilador.lexica= lexica@
	 @if Lineas.inicial is None:@
	 @  Compilador.G = None@
	 @else:@
	 @  Compilador.G= Gramatica(T.listanoterminales(), Lineas.inicial, Lineas.l, tratEOF.codigo)@
	 @codusuario= Lineas.codusuario@
	 @Compilador.codusuario= codusuario@
       ;

#
# Tratamiento del fin de fichero ausente:
#

<tratEOF> -> @c = None@
             ( errordos
	        @if c is None: c = code.empty()@
                @c.addBrother(errordos_.codigo)@
             )*
             @tratEOF.codigo= c@
	 ;

<tratEOF> -> error
	@errores.append(mc_al.linea(), u"Al código inicial no le sigue el comienzo de una regla ni un tratamiento de error. Voy a saltar entrada hasta que encuentre algo.")@
	@mc_al.sincroniza(mc_primeros["<Lineas>"]+["errordos"], mc_abandonar)@
	@if mc_al.actual.cat=="errordos":@
	@  mc_reintentar()@
        ;

#
# Líneas de la gramática:
#

<Lineas> ->
        @inicial= None@
	(
          noterminal
	    @nt= T.noterminal(noterminal.id, noterminal.nlinea)@
            @if inicial== None:@
            @  inicial= nt@
	    $errores.append(mc_al.linea(), u"Después del no terminal, debería venir una flecha")$
	  flecha
            @global enparentesis@
	    @enparentesis= False@
	  <ParteDerecha>
            $errores.append(mc_al.linea(), "Falta un punto y coma.")$
	    $if mc_al.actual.cat=="flecha":$
            $  errores.append(mc_al.linea(), "Creo que he juntado dos reglas.")$
            $  mc_al.avanza()$
	    $else:$
	    $  mc_al.sincroniza(mc_aceptables["<Lineas>"], mc_abandonar)$
	  pyc
            @if ParteDerecha.pd:@
            @  Lineas.l.append(Regla(nt, ParteDerecha.pd, noterminal.nlinea))@
            @if ParteDerecha.error:@
            @  nt.tratamientoError(ParteDerecha.error)@
        |
	  codigo
	    @Lineas.codusuario / codigo.cod@
        )*
	@Lineas.inicial= inicial@
	;

<Lineas> -> error
        @errores.append(mc_al.linea(), u"Has comenzado una producción de manera extraña, buscaré algún comienzo mejor")@
	@mc_al.sincroniza(mc_aceptables["<Lineas>"], mc_abandonar)@
	@mc_reintentar()@
        ;

#
# Parte derecha:
#

<ParteDerecha> ->
          @ParteDerecha.error= None@
        <Alternativa>
          @if Alternativa.pd:@
          @  l= [Alternativa.pd]@
          @else:@
          @  l= []@
	  @  ParteDerecha.error= Alternativa.error@
        (
          barra <Alternativa>
            @if Alternativa2.pd:@
            @  l.append(Alternativa2.pd)@
            @else:@
	    @  if ParteDerecha.error!= None:@
	    @    avisos.append(mc_al.linea(), u"Ya tenía un tratamiento de error; pasaré de este de aquí.")@
	    @  else:@
            @    ParteDerecha.error= Alternativa2.error@
        )*
          @if len(l)== 0:@
          @  ParteDerecha.pd= None@
          @elif len(l)== 1 and ParteDerecha.error== None:@
          @  ParteDerecha.pd= l[0]@
	  @else:@
	  @  ParteDerecha.pd= Disyuncion(l, l[0].nl, ParteDerecha.error)@
        ;

<ParteDerecha> ->
	error
          @if mc_al.actual.cat=="codigo":@
          @  mensaje= u"Parte derecha de la regla incorrecta: ¿te has olvidado del punto y coma? "@
          @else:@
          @  mensaje= u"Parte derecha de la regla incorrecta: esperaba ver "@
          @  if len(mc_t)> 1:@
          @    if not enparentesis:@
	  @      try:@
          @        mc_t.remove("cierra")@
          @      except ValueError:@
          @        pass@
          @    mensaje+= u", ".join([_nombre[t] for t in mc_t[:-1]])@
          @    mensaje+= u" o "+_nombre[mc_t[-1]]@
          @  else:@
          @    mensaje+= _nombre[mc_t[0]]@
          @  mensaje+= u" y he visto "+_nombre[mc_al.actual.cat]@
	  @errores.append(mc_al.linea(), mensaje)@
	  @mc_al.sincroniza(mc_siguientes["<ParteDerecha>"], mc_abandonar)@
	  @ParteDerecha.pd= None@
	  @ParteDerecha.error= None@
	;

#
# Alternativas:
#

<Alternativa> ->
        tokenerror
	  $errores.append(mc_al.linea(),u"Después del error debes indicar el tratamiento")$
	  $mc_al.sincroniza(mc_siguientes["<Alternativa>"]+["accion"], mc_abandonar)$
	  $if mc_al.actual.cat=="accion":$
          $  accion= mc_al.actual$
          $  mc_al.avanza()$
          $else:$
	  $  accion= None$
        accion
          @Alternativa.pd= None@
          @if accion!= None:@
          @  Alternativa.error= accion.codigo@
	  @else:@
	  @  Alternativa.error= None@
        (
          accion
            @Alternativa.error.addBrother(accion2.codigo)@
        )*
	;

<Alternativa> -> <Elemental>
          @Alternativa.error= None@
          @if Elemental.pd!= None:@
          @  l= [Elemental.pd]@
          @else:@
          @  l= []@
         (
           <Elemental>
	   @if Elemental2.pd!= None:@
           @  l.append(Elemental2.pd)@
         )*
          @if len(l)== 0:@
          @  Alternativa.pd= None@
          @elif len(l)== 1:@
          @  Alternativa.pd= Elemental.pd@
	  @else:@
          @  Alternativa.pd= Secuencia(l, l[0].nl)@
	;

<Alternativa> ->
          @Alternativa.pd= Vacia(mc_al.linea())@
          @Alternativa.error= None@
          ;

<Alternativa> -> error
          @Alternativa.pd= None@
	  @Alternativa.error= None@
          @if mc_al.actual.cat=="flecha":@
	  @  errores.append(mc_al.linea(), "He encontrado una flecha en un lugar incorrecto, es posible que te falte un punto y coma previo.")@
	  @  mc_al.sincroniza(mc_aceptables["<Alternativa>"], mc_abandonar)@
          @  if mc_al.actual.cat in mc_primeros["<Alternativa>"]:@
	  @    mc_reintentar()@
	  @else:@
          @  mc_error(mc_nt, mc_t)@
          ;
#
# Elementales:
#

<Elemental> -> noterminal
          @Elemental.pd= T.noterminal(noterminal.id, noterminal.nlinea)@
	;

<Elemental> -> @error= None@
        ( errordos
	  @if error == None: error = code.empty()@
          @error.addBrother(errordos.codigo)@
        )*
        terminal
          @global directos@
	  @if terminal.directo and terminal.id not in directos:@
	  @  directos.update((terminal.id,))@
          @Elemental.pd= Terminal(terminal.id, terminal.directo, error, terminal.nlinea)@
	;

<Elemental> -> accion
 	  @Elemental.pd= Accion(accion.codigo, accion.nlinea)@
	;

<Elemental> -> abre
        @global enparentesis@
        @par= enparentesis@
        @enparentesis= True@
	<ParteDerecha>
          @Elemental.pd= ParteDerecha.pd@
	cierra
        @enparentesis= par@
          (
            asterisco
              @if ParteDerecha.pd:@
              @  Elemental.pd= Iteracion(ParteDerecha.pd, abre.nlinea)@
            |
            cruz
              @if ParteDerecha.pd:@
              @  Elemental.pd= Repeticion(ParteDerecha.pd, abre.nlinea)@
            |
            interrogante
              @if ParteDerecha.pd:@
              @  Elemental.pd= Opcional(ParteDerecha.pd, abre.nlinea)@
          )?
	;

%

def main():
  sys.stderr.write("Este módulo no está preparado para ejecutarse independientemente")
  sys.exit(1)
