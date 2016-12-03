#!/usr/bin/env python
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
##############################################################################
#
# Fichero: gramatica.py
#

from analex import prettyCat
import code

# Funciones auxiliares:

def _gestion_orden(orden, nombre):
    orden[nombre]= orden.get(nombre, 0)+1
    return `orden[nombre]`

def _set_strlista(s):
    return "[ u'%s' ]" % "', '".join(sorted(s))

def _test_set(s):
    if len(s)==1:
        e= s.pop()
        s.add(e)
        return "mc_al.actual.cat == u'%s'" % e
    else:
        return "mc_al.actual.cat in %s" % _set_strlista(s)

def _test_no_set(s):
    if len(s)==1:
        e= s.pop()
        s.add(e)
        return "mc_al.actual.cat != u'%s'" % e
    else:
        return "mc_al.actual.cat not in %s" % _set_strlista(s)


def clausura(eltos, ctos, influye):
    p= set(eltos) # pendientes
    while p:
        e= p.pop()
        ce= ctos[e]
        for f in influye[e]:
            cf= ctos[f]
            l= len(cf)
            cf.update(ce)
            if l!= len(cf):
                p.add(f)

##############################################################################

class Regla:
    "Representación de las reglas"
    def __init__(self, izda, dcha, nl):
        self.nl= nl
        self.izda= izda
        self.dcha= dcha

        self.izda.reglasizda.append(self)

        def escribe_mi_nt(self, mi_nt= self.izda):
            self.mi_nt= mi_nt
        self.dcha.aplica_funcion(escribe_mi_nt)

        self.simbolos= []
        def averigua_simbolos(self, s=self.simbolos):
            if isinstance(self, NoTerminal) or isinstance(self, Terminal):
                s.append(self)
        self.dcha.aplica_funcion(averigua_simbolos)

    def __str__(self):
        return u"%s -> %s ;" % (self.izda, self.dcha)

    def terminales(self):
        return self.dcha.terminales()

    def regla(self):
        return u"%s -> %s ;" % (self.izda.regla(), self.dcha.regla())

    def aplica_funcion(self,f):
        self.izda.aplica_funcion(f)
        self.dcha.aplica_funcion(f)

class Pdcha:
    "Clase genérica para las partes derechas de las reglas"
    def __init__(self, anulable, nl, descendientes):
        self.nl= nl
	self.esanulable= anulable
        self.misprimeros= set()
        self.missiguientes= set()
        self.misaceptables= None
        self.ninventario= None
        self.descendientes= descendientes

    def regla(self):
        "Devuelve la regla como cadena, sin las acciones"
        return str(self)

    def anulable(self):
        """Devuelve True si es anulable, False si no lo es y None si
        no se sabe"""
        return self.esanulable

    def influye_anulable(self, inf):
        """Añade self a cada uno de los elementos de inf que influyen
        para que self sea anulable."""
        for d in self.descendientes:
            inf[d.ninventario].append(self)

    def comprueba_anulable(self):
        """Intenta averiguar si self es ya anulable"""
        pass

    def primeros(self):
        """Devuelve los primeros de parte derecha"""
        return self.misprimeros

    def influye_primeros(self, inf):
        """Añade self.ninventario a los elementos de inf que influyen
        para los primeros de self."""
        for d in self.descendientes:
            inf[d.ninventario].append(self.ninventario)

    def siguientes(self):
        """Devuelve los siguientes de self"""
        return self.missiguientes

    def influye_siguientes(self, inf):
        """Añade a inf las influencias del cálculo de siguientes que
        pueden encontrarse desde self."""
        for d in self.descendientes:
            inf[self.ninventario].append(d.ninventario)

    def propaga_primeros_siguientes(self):
        """Propaga los primeros de un elemento a los siguientes de sus
        precedentes. Se aplica en secuencias y clausuras."""
        pass

    def aceptables(self):
        """Devuelve la unión de los primeros con los siguientes si es anulable"""
        return self.misaceptables

    def prepara_aceptables(self):
        """Calcula los aceptables, definidos como los primeros unidos, si self es
        anulable, con los siguientes"""
        if self.anulable():
            self.misaceptables= self.primeros().union(self.siguientes())
        else:
            self.misaceptables= self.primeros().copy()

    def genera_codigo_interno(self, pizda, orden, siguientesPadre, garantizados, traza, esPuro):
        """Genera la parte del código de esta pdcha.
            pizda: parte izquierda de la regla que se está tratando
            ordenT: diccionarios para controlar la numeración de terminales y
              no terminales.
            siguientesPadre: conjunto de terminales que son siguientes del padre de
              la parte derecha.
            garantizados: conjunto de terminales que pueden llegar a este punto.
              Son siempre aceptables. None si no se sabe.
            traza: formato de la traza ("A" arbol, "t" traza).
            esPuro: cierto si se está generando un analizador sintáctico puro."""
        return code.empty()

    def aplica_funcion(self,f):
        """Aplica la función f sobre sí mismo y sus descendientes"""
        f(self)
        for d in self.descendientes:
            d.aplica_funcion(f)

    def recursividad_izquierda(self, nt):
        """Devuelve True si el nt tiene recursividad a izquierdas, False si no"""
        return True

    def comprueba_conflictos(self, siguientes, salida):
        """Comprueba si hay posibles conflictos cuando los siguientes son siguientes.
        Escribe en salida los conflictos que encuentra."""
        pass

    def terminales(self):
        if isinstance(self, Terminal):
            return set([self.nombre])
        t = set()
        for d in self.descendientes:
            t |= d.terminales()
        return t

class NoTerminal(Pdcha):
    "Representa los no terminales"
    def __init__(self, nombre, nl):
        Pdcha.__init__(self, None, nl, [])
        self.nombre= nombre
        self.reglasizda= [] # reglas en las que este no terminal aparece
        		    # en la parte izquierda
        self.reglasdcha= [] # reglas en las que este no terminal aparece
        		    # en la parte derecha
        self.traterror= None

    def influye_anulable(self, inf):
        for r in self.reglasizda:
            n= r.dcha.ninventario
            inf[n].append(self)

    def comprueba_anulable(self):
        for r in self.reglasizda:
            if r.dcha.anulable():
                self.esanulable= True
                break

    def influye_primeros(self, inf):
        yo= self.ninventario
        for r in self.reglasizda:
            inf[r.dcha.ninventario].append(yo)

    def influye_siguientes(self, inf):
        yo= self.ninventario
        for r in self.reglasizda:
            inf[yo].append(r.dcha.ninventario)

    def __str__(self):
        return u"<%s>" % self.nombre

    def tratamientoError(self,tratamiento):
        self.traterror= tratamiento

    def genera_codigo(self, traza, esPuro= False):
        """ Genera el código de la regla.
            traza: genera código para escribir la traza (arbol: "A" o traza: "t").
            esPuro: si cierto genera un analizador puro (sin acciones semánticas).
        """
        if esPuro:
            c = code.sentence("def mc_analiza_%s(self):" % self.nombre)
        else:
            c = code.sentence("def mc_analiza_%s(self, %s):" % (self.nombre,self.nombre))
        # La traza:
        if traza=="t":
            ( c
              // (u"mc_traza('> %s %%s\\n' %% self.mc_al.actual)" % self)
              /  "mc_dentro_traza()"
              )
        elif traza=="A":
            ( c
              // (u"mc_traza(u'(\"%s\" \"línea: %%d\"\\n' %% self.mc_al.actual.nlinea)" % self)
              /  "mc_dentro_traza()"
              )
        # Hacemos accesible el analizador léxico:
        c // "mc_al = self.mc_al"

        # Cuerpo del analizador
        cuerpo = code.sentence("if not %s:" % _test_set(self.misaceptables))
        if traza:
          cuerpo // (u'mc_traza(u"Error, no se encuentra ningún elemento aceptable para %s.\\n")' % self)
        cuerpo // ("mc_error('%s', %s)" % (self, _set_strlista(self.misaceptables)))

        cadif= "if"
        for n, regla in enumerate(self.reglasizda):
            aceptables= regla.dcha.primeros()
            if regla.dcha.anulable():
                aceptables|= self.siguientes()
            # Cuerpo de la regla
            cuerpoRegla = code.empty()
            if traza=="t": # Si hay traza
                cuerpoRegla / ("mc_traza('Aplico regla: '+" + `regla.regla()` + "+'\\n')")
            if not esPuro:
                # Generamos los atributos y los alias:
                orden= {}
                for s in regla.simbolos:
                    _gestion_orden(orden, s.nombre)
                    if isinstance(s, NoTerminal):
                        nto= s.nombre+`orden[s.nombre]`
                        if orden[s.nombre]== 1 and s!= self:
                            cuerpoRegla / ("%s = %s = Atributos()" % (s.nombre, nto))
                        else:
                            cuerpoRegla / ("%s = Atributos()" % nto)
            # Generamos el código de la regla:
            cuerpoRegla / regla.dcha.genera_codigo_interno(self, {}, self.siguientes(), aceptables, traza, esPuro)

            if len(self.reglasizda)> 1: # Si hay más de una posibilidad, hay que poner una guarda
                if n == len(self.reglasizda)-1:
                    cuerpo / "else:"
                else:
                    cuerpo / (cadif+ " %s:" % _test_set(aceptables))
                cadif="elif"
                cuerpo // cuerpoRegla
            else:
                cuerpo / cuerpoRegla # No sangramos si sólo hay una posibilidad

        # Más traza, para avisar de que nos vamos
        if traza=="t":
            ( cuerpo
              /  "mc_fuera_traza()"
              /  (u"mc_traza('< %s\\n')" % self)
              )
        elif traza=="A":
            ( cuerpo
              /  "mc_fuera_traza()"
              /  "mc_traza(')\\n')"
              )

        # Comprobamos el tratamiento de errores:
        if self.traterror and not esPuro:
            ( c
              // "self.mc_reintento.append(True)"
              /  "mc_reintentar= self.mc_reintentar"
              /  "while self.mc_reintento[-1]:"
              //   "self.mc_reintento[-1]= False"
              /    "try:"
              //      cuerpo
              %    "except mc_error_sintaxis, (mc_nt, mc_t):"
              //      self.traterror
              % None % "self.mc_reintento.pop()"
              )
        else:
            c // cuerpo
        return c

    def genera_codigo_interno(self, pizda, orden, siguientesPadre, garantizados, traza, esPuro):
        if not esPuro:
            atr= self.nombre+_gestion_orden(orden, self.nombre)
            c= code.sentence("self.mc_analiza_%s(%s)" % (self.nombre,atr))
            c / ("%s_ = %s" % (self.nombre, atr))
        else:
            c= code.sentence("self.mc_analiza_%s()" % self.nombre)
        return c

    def recursividad_izquierda(self, nt):
        return self==nt

    def comprueba_conflictos_globales(self, salida):
        vistos={}
        for r in self.reglasizda:
            aceptables= r.dcha.primeros()
            if r.dcha.anulable():
                aceptables= aceptables|self.missiguientes
            for t in aceptables:
                if vistos.has_key(t):
                    salida.write((
u"""Aviso: hay un conflicto entre las reglas de la línea %d:
    %s
  y la de la línea %d
    %s
  al ver el símbolo %s. Se tomará la primera.\n"""
% (vistos[t].nl, vistos[t].regla(), r.nl, r.regla(), prettyCat(t))).encode("utf-8"))
                else:
                    vistos[t]= r
            r.dcha.comprueba_conflictos(self.missiguientes, salida)

    def comprueba_conflictos(self, siguientes, salida):
        pass

class Terminal(Pdcha):
    "Representa los terminales que no son la cadena vacía"
    def __init__(self, nombre, directo, error, nl):
        Pdcha.__init__(self, False, nl, [])
        self.nombre= nombre
        self.directo= directo
        self.error= error
        self.misprimeros.add(self.nombre)

    def __str__(self):
        return prettyCat(self.nombre)

    def genera_codigo_interno(self, pizda, orden, siguientesPadre, garantizados, traza, esPuro ):
        cuerpo = code.empty()
        if traza == "t":
            cuerpo / ("""mc_traza('Reconocido el terminal "%s"\\n')""" % self.nombre)
        elif traza == "A":
            ( cuerpo
              / (u"""mc_traza('("%s"\\n')""" % repr(self.nombre.replace('"','""'))[2:-1])
              / u"""mc_traza(' "lexema: %s"\\n' % mc_al.actual.lexema.replace('"','""'))"""
              / u"""mc_traza(u' "línea: %d"\\n' % mc_al.actual.nlinea)"""
              / """mc_traza(')\\n')"""
            ) #'<- para el font-lock
        if not esPuro and not self.directo:
            n= self.nombre+_gestion_orden(orden, self.nombre)
            if orden[self.nombre]== 1 and pizda.nombre!= self.nombre:
                cuerpo / ("%s = %s = %s_ = mc_al.actual" % (self.nombre, n, self.nombre))
            else:
                cuerpo / ("%s = %s_ = mc_al.actual" % (n, self.nombre))
        cuerpo / "mc_al.avanza()"
        if traza=="t":
            cuerpo / u"""mc_traza(u'Leído el terminal "%s"\\n' % self.mc_al.actual)"""

        if garantizados and len(garantizados)==1 and self.nombre in garantizados:
            c = cuerpo
        else:
            c = ( code.sentence("if mc_al.actual.cat == u'%s':" % self.nombre)
                  // cuerpo
                  % "else:"
                  ).code() # Si no, tenemos un _CodeControl y los siguientes van mal
            if traza:
                c // ("""mc_traza('Error no es un "%s"\\n')""" % self.nombre)
            if not self.error:
                c // ("mc_error('%s', [u'%s'])" % (pizda, self.nombre))
            else:
                c // self.error
        return c

    def recursividad_izquierda(self, nt):
        return False

    def comprueba_conflictos(self, siguientes, salida):
        pass

class Vacia(Pdcha):
    "Representa el terminal cadena vacía"
    def __init__(self, nl):
        Pdcha.__init__(self, True, nl, [])

    def __str__(self):
        return ""

    def genera_codigo_interno(self, pizda, orden, siguientesPadre, garantizado, traza, esPuro):
        c= code.empty()
        if traza=="t":
            c / u"mc_traza('Reconocida una cadena vacía\\n')"
        elif traza=="A":
            c / """mc_traza('("")\\n')"""
        return c

    def aplica_funcion(self,f):
        f(self)

    def recursividad_izquierda(self,nt):
        return False

    def comprueba_conflictos(self, siguientes, salida):
        pass

class Accion(Vacia):
    "Acción en una regla"
    def __init__(self, cod, nl):
        Pdcha.__init__(self, True, nl, [])
        self.cod= cod

    def __str__(self):
        return u"@%s@" % self.cod

    def regla(self):
        return ""

    def genera_codigo_interno(self, pizda, orden, siguientesPadre, garantizado, traza, esPuro):
        if esPuro:
            return code.empty()
        else:
            return self.cod

class Secuencia(Pdcha):
    "Parte derecha consistente en una secuencia de elementos"
    def __init__(self, l, nl):
        Pdcha.__init__(self, None, nl, l)
        self.l= l

    def comprueba_anulable(self):
        self.esanulable= True
        for pd in self.l:
            if pd.anulable()== False:
                self.esanulable= False
                break

    def influye_primeros(self, inf):
        yo= self.ninventario
        for pd in self.l:
            inf[pd.ninventario].append(yo)
            if not pd.anulable():
                break

    def influye_siguientes(self, inf):
        yo= self.ninventario
        if self.l:
            for pd in reversed(self.l):
                inf[yo].append(pd.ninventario)
                if not pd.anulable():
                    break

    def propaga_primeros_siguientes(self):
        ac=set()
        if self.l:
            for pd in reversed(self.l):
                pd.missiguientes.update(ac)
                if pd.anulable():
                    ac.update(pd.primeros())
                else:
                    ac= pd.primeros().copy()

    def __str__(self):
        return u" ".join([unicode(i) for i in self.l])

    def regla(self):
        return " ".join([i for i in [j.regla() for j in self.l] if i])

    def genera_codigo_interno(self, pizda, orden, siguientesPadre, garantizados, traza, esPuro):
        c=code.empty()
        g= garantizados
        if traza=="t":
            ( c
              / ("mc_traza('> Analizando %s\\n')" % self.regla())
              /  "mc_dentro_traza()")
        for i in self.l:
            c / i.genera_codigo_interno(pizda, orden, i.siguientes(), g, traza, esPuro)
            if not isinstance(i,Vacia):
                g= None
        if traza=="t":
            ( c
              / "mc_fuera_traza()"
              / ("mc_traza('< Fin de %s\\n')" % self.regla())
              )
        return c

    def recursividad_izquierda(self,nt):
        for i in self.l:
            if i.recursividad_izquierda(nt):
                return True
            if not i.anulable():
                return False
        return False

    def comprueba_conflictos(self, siguientes, salida):
        sig=set(siguientes)
        for pd in reversed(self.l):
            pd.comprueba_conflictos(sig, salida)
            if pd.anulable():
                sig.update(pd.primeros())
            else:
                sig= set(pd.primeros())

class Opcional(Pdcha):
    "Parte derecha representando la aparición o no de una parte"

    def __init__(self, pd, nl):
        Pdcha.__init__(self, True, nl, [pd])
        self.pd= pd

    def __str__(self):
        return u"( %s )?" % self.pd

    def regla(self):
        return u"( %s )?" % self.pd.regla()

    def genera_codigo_interno(self, pizda, orden, siguientesPadre, garantizados, traza, esPuro):
        c = code.empty()
        primeros= self.pd.primeros()
        if traza=="t":
            c / ("mc_traza('> Analizando %s\\n')" % self.regla())
        ( c
          / ("if %s:" % _test_set(primeros))
          //  self.pd.genera_codigo_interno(pizda, orden, siguientesPadre, primeros, traza, esPuro)
          )
        if garantizados == None or garantizados < siguientesPadre | primeros:
            celif = code.sentence("elif %s:" % _test_no_set(siguientesPadre))
            if traza:
                celif / u"mc_traza(u'Error, no podemos asumir que esté vacía.\\n')"
            celif / ("mc_error('%s', %s)" % (pizda, _set_strlista(primeros|siguientesPadre)))
        if traza=="t":
            ( c
              / "else:"
              //  u"mc_traza(u'Se supone que ha generado la cadena vacía\\n')"
              )
        return c

    def recursividad_izquierda(self,nt):
        return self.pd.recursividad_izquierda(nt)

    def comprueba_conflictos(self, siguientes, salida):
        if self.pd.anulable():
            for t in siguientes:
                if not t in self.primeros():
                    salida.write((
u"""Aviso: hay un conflicto en la parte opcional de la línea %d:
   %s
  con el símbolo %s. En ese caso, no entraré.\n"""
% (self.nl, self.regla(), prettyCat(t))).encode("utf-8"))
        for t in self.primeros():
            if t in siguientes:
                salida.write((
u"""Aviso: hay un conflicto en la parte opcional de la línea %d:
   %s
  con el símbolo %s. En ese caso, desplazaré.\n"""
% (self.nl, self.regla(), prettyCat(t))).encode("utf-8"))
        self.pd.comprueba_conflictos(siguientes, salida)

class Disyuncion(Pdcha):
    "Parte derecha para representar multiples opciones"
    def __init__(self, l, nl, traterror= None):
        Pdcha.__init__(self, None, nl, l)
        self.l= l
        self.traterror= traterror

    def comprueba_anulable(self):
        for pd in self.l:
            if pd.anulable():
                self.esanulable= True
                break

    def __str__(self):
        r=[]
        for i in self.l:
            r.append(i)
        return u"( %s )" % u" | ".join(map(unicode, r))

    def regla(self):
        r=[]
        for i in self.l:
            r.append(i.regla())
        return u"( %s )" % u" | ".join(r)

    def genera_codigo_interno(self, pizda, orden, siguientesPadre, garantizados, traza, esPuro ):
        cuerpo = code.empty()
        if traza=="t":
            ( cuerpo
              / ("mc_traza('> Analizando %s\\n')" % self.regla())
              / "mc_dentro_traza()"
              )
        # No podemos hacer caso de las garantías si hay tratamiento de error;
        # no sabemos dónde se puede haber sincronizado.
        if garantizados and (esPuro or not self.traterror):
            g= garantizados.copy()
        else:
            g= None
        el = ""
        for opcion in self.l:
            aceptables= opcion.primeros()
            if opcion.anulable():
                aceptables= aceptables|siguientesPadre
            if g!= None:
                r= aceptables.intersection(g)
            else:
                r= aceptables
            interno = opcion.genera_codigo_interno(pizda, orden, siguientesPadre, r, traza, esPuro)
            if r:
                if g== None or len(r)< len(g): # Caso normal: los aceptables son menos que los garantizados
                    ( cuerpo
                      / (el+"if %s:" % _test_set(r))
                      // interno
                      )
                    el="el"
                elif len(r)== len(g):
                    if el== "": # Esta alternativa se lo lleva todo y no hemos visto ninguna otra
                        cuerpo / interno
                    else: # Estamos en la última alternativa
                        ( cuerpo
                          / "else:"
                          // interno
                          )
            if g:
                g.difference_update(r)
        if g== None: # Puede que haya un error en la entrada
            cuerpo / "else:"
            if traza:
                cuerpo // "mc_traza('Error, no hay ninguna alternativa aceptable.\\n')"
            cuerpo // ("mc_error('%s', %s)" % (pizda, _set_strlista(self.misaceptables)))
        if traza=="t":
            ( cuerpo
              / "mc_fuera_traza()"
              /("mc_traza('< Fin de %s\\n')" % self.regla())
              )
        if self.traterror and not esPuro:
            c = ( code.sentence("self.mc_reintento.append(True)")
                  /  "mc_reintentar= self.mc_reintentar"
                  /  "while self.mc_reintento[-1]:"
                  //   "self.mc_reintento[-1]= False"
                  /   "try:"
                  //     cuerpo
                  %   "except mc_error_sintaxis, (mc_nt, mc_t):"
                  //     self.traterror
                )
            c / "self.mc_reintento.pop()"
        else:
            c= cuerpo
        return c

    def recursividad_izquierda(self,nt):
        for i in self.l:
            if i.recursividad_izquierda(nt):
                return True
        return False

    def comprueba_conflictos(self, siguientes, salida):
        vistos={}
        for r in self.l:
            aceptables= r.primeros()
            if r.anulable():
                aceptables= aceptables|siguientes
            for t in aceptables:
                if vistos.has_key(t):
                    salida.write((
u"""Aviso: hay un conflicto entre las opciones:
    %s
  y
    %s
  de la disyunción de la línea %d:
    %s
  con el símbolo %s. Se tomará la primera.\n"""
  % (vistos[t].regla(), r.regla(), self.nl, self.regla(), prettyCat(t))).encode("utf-8"))
                else:
                    vistos[t]= r
            r.comprueba_conflictos(siguientes, salida)

class Iteracion(Pdcha):
    "Parte derecha representando cero o más iteraciones"
    def __init__(self, pd, nl):
        Pdcha.__init__(self, True, nl, [pd])
        self.pd= pd

    def __str__(self):
        return u"( %s )*" % self.pd

    def regla(self):
        return u"( %s )*" % self.pd.regla()

    def propaga_primeros_siguientes(self):
        self.pd.missiguientes.update(self.pd.primeros())

    def genera_codigo_interno(self, pizda, orden, siguientesPadre, garantizados, traza, esPuro):
        c = code.empty()
        if traza=="t":
            ( c
              / ("mc_traza('> Analizando %s\\n')" % self.regla())
              / "mc_dentro_traza()"
              )
        ( c
          / ("while %s:" % _test_set(self.pd.primeros()))
          //  self.pd.genera_codigo_interno(pizda, orden, siguientesPadre, self.pd.primeros(), traza, esPuro)
          )
        if traza=="t":
            ( c
              / "mc_fuera_traza()"
              / ( "mc_traza('< Fin de %s\\n')" % self.regla())
              )
        c / ("if not %s:" % _test_set(self.missiguientes))
        if traza:
            c // "mc_traza('Error, no encontramos ninguno de los siguientes\\n')"
        c // ("mc_error('%s',%s)" % (self.mi_nt, _set_strlista(self.misaceptables)))
        return c

    def recursividad_izquierda(self,nt):
        return self.pd.recursividad_izquierda(nt)

    def comprueba_conflictos(self, siguientes, salida):
        if self.pd.anulable() and len(self.pd.primeros())== 0:
            if len(siguientes)== 1:
                salida.write((
u"""Aviso: hay un conflicto en la clausura de la línea %d
   %s
  con el símbolo %s. No se entrará en la clausura.\n"""
% (self.nl, self.regla(), prettyCat(siguientes[0]))).encode("utf-8"))
            else:
                salida.write((
u"""Aviso: hay un conflicto en la clausura de la línea %d
   %s
  con los símbolos {%s}. No se entrará en la clausura.\n"""
% (self.nl, self.regla(), ", ".join([prettyCat(s) for s in siguientes]))).encode("utf-8"))

        l= [ prettyCat(t) for t in self.primeros() if t in siguientes]
        if l:
            if len(l)== 1:
                salida.write((
u"""Aviso: hay un conflicto en la clausura de la línea %d:
   %s
  con el símbolo %s. En ese caso, desplazaré.\n"""
% (self.nl, self.regla(), l[0])).encode("utf-8"))
            else:
                salida.write((
u"""Aviso: hay conflictos en la clausura de la línea %d:
   %s
  con los símbolos {%s}. En caso de encontrarlos, los desplazaré.\n"""
    % (self.nl, self.regla(), ", ".join(l))).encode("utf-8"))
        self.pd.comprueba_conflictos(siguientes|self.pd.primeros(), salida)

class Repeticion(Pdcha):
    "Parte derecha representando una o más iteraciones"
    def __init__(self, pd, nl):
        Pdcha.__init__(self, None, nl, [pd])
        self.pd= pd

    def __str__(self):
        return u"( %s )+" % self.pd

    def regla(self):
        return u"( %s )+" % self.pd.regla()

    def comprueba_anulable(self):
        self.esanulable= pd.anulable()

    def propaga_primeros_siguientes(self):
        self.pd.missiguientes.update(self.pd.primeros())

    def genera_codigo_interno(self, pizda, orden, siguientesPadre, garantizados, traza, esPuro):
        c = code.empty()
        if traza=="t":
            ( c
              / ("mc_traza('> Analizando %s\\n')" % self.regla())
              / "mc_dentro_traza()"
              )
        if garantizados== self.primeros(): # Sólo tenemos garantías si
            g= garantizados                # coinciden al principio y
        else:                              # en cada vuelta
            g= None
        ( c
          / "while True:"
          //   self.pd.genera_codigo_interno(pizda, orden, siguientesPadre, g, traza, esPuro)
          /    ("if %s: break" % _test_no_set(self.primeros()))
          )
        if traza=="t":
            ( c
              / "mc_fuera_traza()"
              / ("""mc_traza('< Fin de %s\\n')""" % self.regla())
              )
        c / ("if not %s:" % _test_set(self.missiguientes))
        if traza:
            c // "mc_traza('Error, no encontramos ninguno de los siguientes\\n')"
        c // ("mc_error('%s',%s)" % (self.mi_nt, _set_strlista(self.misaceptables)))
        return c

    def recursividad_izquierda(self,nt):
        return self.pd.recursividad_izquierda(nt)

    def comprueba_conflictos(self, siguientes, salida):
        for t in self.primeros():
            if t in siguientes:
                salida.write((
u"""Aviso: hay un conflicto en la clausura positiva de la línea %d:
   %s
  con el símbolo %s. En ese caso, desplazaré.\n"""
                             % (self.nl, self.regla(), prettyCat(t))).encode("utf-8"))
        self.pd.comprueba_conflictos(siguientes|self.pd.primeros(), salida)

#
#  Clase para las gramáticas:
#


class Gramatica:
    def __init__(self, noterminales, inicial, reglas, noEOF):
        self.noEOF = noEOF
        self.noterminales = noterminales
	self.inicial = inicial
        self.reglas = reglas
        self.terminales = set()
        for r in self.reglas:
            self.terminales |= r.terminales()

        self.inventario= [] # Cada elemento de la gramática tiene asociada su posición
                            # en esta lista

        def actualiza_inventario(elto, inv = self.inventario):
            """Actualiza el inventario con el elemento elto si no está"""
            if elto.ninventario == None:
                elto.ninventario = len(inv)
                inv.append(elto)
        for r in reglas:
            r.aplica_funcion(actualiza_inventario)
        self.calcula_anulables()
        self.calcula_primeros()
        self.calcula_siguientes()
        self.prepara_aceptables()

    def __str__(self):
        s= []
        for r in self.inicial.reglasizda:
            s.append(r)
        for nt in self.noterminales:
            if nt!= self.inicial:
                for r in nt.reglasizda:
                    s.append(r)
        return u"\n".join(map(unicode, s))

    def lista_reglas(self):
        l=[]
        for r in self.reglas:
            l.append(r.regla())
        return u"\n".join(l)

    def calcula_anulables(self):
        influye= [ [] for i in xrange(len(self.inventario)) ]
        pendientes= set()
        for e in self.inventario:
            e.influye_anulable(influye)
            if e.anulable():
                pendientes.add(e.ninventario)
            else:
                e.esanulable= False # Cambiamos None por False
        while pendientes:
            n= pendientes.pop()
            for e in influye[n]:
                if not e.anulable():
                    e.comprueba_anulable()
                    if e.anulable():
                        pendientes.add(e.ninventario)

    def calcula_primeros(self):
        influye= [ [] for i in xrange(len(self.inventario)) ]
        inicial= [ e.misprimeros for e in self.inventario ]
        for e in self.inventario:
            e.influye_primeros(influye)
        clausura(range(len(self.inventario)), inicial, influye)

    def calcula_siguientes(self):
        influye= [ [] for i in xrange(len(self.inventario)) ]
        inicial= [ e.missiguientes for e in self.inventario ]
        for e in self.inventario:
            e.influye_siguientes(influye)
        for e in self.inventario:
            e.propaga_primeros_siguientes()
        self.inicial.missiguientes.add("mc_EOF")
        clausura(range(len(self.inventario)), inicial, influye)

    def prepara_aceptables(self):
        for e in self.inventario:
            e.prepara_aceptables()

    def aplica_funcion(self,f):
        for r in self.reglas:
            r.aplica_funcion(f)

    def recursividad_izquierda(self):
        l= set()
        for nt in self.noterminales:
            for r in nt.reglasizda:
                if r.dcha.recursividad_izquierda(nt):
                    l.add(nt)
        return l

    def comprueba_conflictos(self, salida):
        for nt in self.noterminales:
            nt.comprueba_conflictos_globales(salida)
