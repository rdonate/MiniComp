#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Este código ha sido generado por metacomp, versión 3.0beta5
import sys
class mc_error_sintaxis(Exception): pass
class mc_error_noEOF(Exception): pass
class mc_error_abandonar(Exception): pass
def mc_error(nt, esp):
    raise mc_error_sintaxis, (nt, esp)
def mc_abandonar():
    raise mc_error_abandonar
from analex import AnalizadorLexico
# Código de usuario
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
def main():
  sys.stderr.write("Este módulo no está preparado para ejecutarse independientemente")
  sys.exit(1)
mc_primeros = {
    '<Alternativa>' : [u'errordos', u'accion', u'noterminal', u'terminal', u'tokenerror', u'abre'],
    '<Compilador>' : [u'especificacion_lexica'],
    '<Elemental>' : [u'terminal', u'errordos', u'abre', u'accion', u'noterminal'],
    '<Lineas>' : [u'codigo', u'noterminal'],
    '<ParteDerecha>' : [u'errordos', u'accion', u'barra', u'noterminal', u'terminal', u'tokenerror', u'abre'],
    '<tratEOF>' : [u'errordos'],
}
mc_siguientes = {
    '<Alternativa>' : [u'barra', u'cierra', u'pyc'],
    '<Compilador>' : ['mc_EOF'],
    '<Elemental>' : [u'terminal', u'accion', u'cierra', u'noterminal', u'errordos', u'barra', u'abre', u'pyc'],
    '<Lineas>' : ['mc_EOF'],
    '<ParteDerecha>' : [u'cierra', u'pyc'],
    '<tratEOF>' : ['mc_EOF', u'codigo', u'noterminal'],
}
mc_aceptables = {
    '<Alternativa>' : [u'errordos', u'terminal', u'abre', u'pyc', u'accion', u'tokenerror', u'cierra', u'noterminal', u'barra'],
    '<Compilador>' : [u'especificacion_lexica'],
    '<Elemental>' : [u'terminal', u'errordos', u'abre', u'noterminal', u'accion'],
    '<Lineas>' : ['mc_EOF', u'codigo', u'noterminal'],
    '<ParteDerecha>' : [u'errordos', u'barra', u'abre', u'pyc', u'accion', u'terminal', u'cierra', u'noterminal', u'tokenerror'],
    '<tratEOF>' : [u'errordos', 'mc_EOF', u'codigo', u'noterminal'],
}
mc_anulables = {
    '<Alternativa>' : True,
    '<Compilador>' : False,
    '<Elemental>' : False,
    '<Lineas>' : True,
    '<ParteDerecha>' : True,
    '<tratEOF>' : True,
}
class Atributos: pass
class AnalizadorSintactico:
    def __init__(self, entrada, entorno = None):
        self.mc_entorno = entorno
        self.mc_al = AnalizadorLexico(entrada)
        self.mc_al.avanza()
        self.mc_reintento = [True]
        mc_reintentar = self.mc_reintentar
        while self.mc_reintento[-1]:
            self.mc_reintento[-1] = False
            self.Compilador = Atributos()
            try:
                self.mc_analiza_Compilador(self.Compilador)
                if self.mc_al.actual.cat != 'mc_EOF':
                    raise mc_error_noEOF
            except mc_error_sintaxis, (nt, esp):
                sys.stderr.write('Error no tratado en línea %d:\n' % self.mc_al.actual.nlinea)
                sys.stderr.write((u'Estaba analizando la expansión del no terminal %s y he encontrado\n el terminal %s.\n' % (nt, self.mc_al.actual)).encode('utf-8'))
                if len(esp)==1:
                    sys.stderr.write((u'Sólo valía un %s.\n' % mc_pretty_cat(esp[0])).encode('utf-8'))
                else:
                    sys.stderr.write((u'Tendría que haber sido uno de los siguientes: %s.\n' % ','.join(map(mc_pretty_cat,esp))).encode('utf-8'))
                sys.exit(1)
            except mc_error_noEOF:
                sys.stderr.write((u'Error no tratado en línea %d:\n' % self.mc_al.actual.nlinea).encode('utf-8'))
                sys.stderr.write('He encontrado entrada donde esperaba ver el final del fichero\n')
                sys.exit(1)
            except mc_error_abandonar:
                pass
    def mc_reintentar(self):
        self.mc_reintento[-1] = True
    def mc_analiza_Alternativa(self, Alternativa):
        mc_al = self.mc_al
        self.mc_reintento.append(True)
        mc_reintentar= self.mc_reintentar
        while self.mc_reintento[-1]:
            self.mc_reintento[-1]= False
            try:
                if not mc_al.actual.cat in [ u'abre', 'accion', 'barra', 'cierra', 'errordos', 'noterminal', 'pyc', 'terminal', 'tokenerror' ]:
                    mc_error('<Alternativa>', [ u'abre', 'accion', 'barra', 'cierra', 'errordos', 'noterminal', 'pyc', 'terminal', 'tokenerror' ])
                if mc_al.actual.cat == u'tokenerror':
                    tokenerror = tokenerror1 = tokenerror_ = mc_al.actual
                    mc_al.avanza()
                    if mc_al.actual.cat == u'accion':
                        accion = accion1 = accion_ = mc_al.actual
                        mc_al.avanza()
                    else:
                        errores.append(mc_al.linea(),u"Después del error debes indicar el tratamiento")
                        mc_al.sincroniza(mc_siguientes["<Alternativa>"]+["accion"], mc_abandonar)
                        if mc_al.actual.cat=="accion":
                          accion= mc_al.actual
                          mc_al.avanza()
                        else:
                          accion= None
                    Alternativa.pd= None
                    if accion!= None:
                      Alternativa.error= accion.codigo
                    else:
                      Alternativa.error= None
                    while mc_al.actual.cat == u'accion':
                        accion2 = accion_ = mc_al.actual
                        mc_al.avanza()
                        Alternativa.error.addBrother(accion2.codigo)
                    if not mc_al.actual.cat in [ u'barra', 'cierra', 'pyc' ]:
                        mc_error('<Alternativa>',[ u'accion', 'barra', 'cierra', 'pyc' ])
                elif mc_al.actual.cat in [ u'abre', 'accion', 'errordos', 'noterminal', 'terminal' ]:
                    Elemental = Elemental1 = Atributos()
                    Elemental2 = Atributos()
                    self.mc_analiza_Elemental(Elemental1)
                    Elemental_ = Elemental1
                    Alternativa.error= None
                    if Elemental.pd!= None:
                      l= [Elemental.pd]
                    else:
                      l= []
                    while mc_al.actual.cat in [ u'abre', 'accion', 'errordos', 'noterminal', 'terminal' ]:
                        self.mc_analiza_Elemental(Elemental2)
                        Elemental_ = Elemental2
                        if Elemental2.pd!= None:
                          l.append(Elemental2.pd)
                    if not mc_al.actual.cat in [ u'barra', 'cierra', 'pyc' ]:
                        mc_error('<Alternativa>',[ u'abre', 'accion', 'barra', 'cierra', 'errordos', 'noterminal', 'pyc', 'terminal' ])
                    if len(l)== 0:
                      Alternativa.pd= None
                    elif len(l)== 1:
                      Alternativa.pd= Elemental.pd
                    else:
                      Alternativa.pd= Secuencia(l, l[0].nl)
                else:
                    Alternativa.pd= Vacia(mc_al.linea())
                    Alternativa.error= None
            except mc_error_sintaxis, (mc_nt, mc_t):
                Alternativa.pd= None
                Alternativa.error= None
                if mc_al.actual.cat=="flecha":
                  errores.append(mc_al.linea(), "He encontrado una flecha en un lugar incorrecto, es posible que te falte un punto y coma previo.")
                  mc_al.sincroniza(mc_aceptables["<Alternativa>"], mc_abandonar)
                  if mc_al.actual.cat in mc_primeros["<Alternativa>"]:
                    mc_reintentar()
                else:
                  mc_error(mc_nt, mc_t)
        self.mc_reintento.pop()
    def mc_analiza_Compilador(self, Compilador):
        mc_al = self.mc_al
        if not mc_al.actual.cat == u'especificacion_lexica':
            mc_error('<Compilador>', [ u'especificacion_lexica' ])
        tratEOF = tratEOF1 = Atributos()
        Lineas = Lineas1 = Atributos()
        Compilador.abandonar = True
        especificacion_lexica = especificacion_lexica1 = especificacion_lexica_ = mc_al.actual
        mc_al.avanza()
        if mc_al.actual.cat == u'codigo':
            codigo = codigo1 = codigo_ = mc_al.actual
            mc_al.avanza()
        else:
            import analex
            codigo=analex.ComponenteLexico("codigo", mc_al.linea())
            codigo.cod= code.empty()
        Lineas.codusuario= codigo.cod
        tratEOF.codigo= None
        self.mc_analiza_tratEOF(tratEOF1)
        tratEOF_ = tratEOF1
        Lineas.l= []
        self.mc_analiza_Lineas(Lineas1)
        Lineas_ = Lineas1
        Compilador.abandonar = False
        lexica= [ (td, None, REParser.stringAsRE(td[1:])) for td in directos ]
        lexica+= especificacion_lexica.esp
        Compilador.lexica= lexica
        if Lineas.inicial is None:
          Compilador.G = None
        else:
          Compilador.G= Gramatica(T.listanoterminales(), Lineas.inicial, Lineas.l, tratEOF.codigo)
        codusuario= Lineas.codusuario
        Compilador.codusuario= codusuario
    def mc_analiza_Elemental(self, Elemental):
        mc_al = self.mc_al
        if not mc_al.actual.cat in [ u'abre', 'accion', 'errordos', 'noterminal', 'terminal' ]:
            mc_error('<Elemental>', [ u'abre', 'accion', 'errordos', 'noterminal', 'terminal' ])
        if mc_al.actual.cat == u'noterminal':
            noterminal = noterminal1 = noterminal_ = mc_al.actual
            mc_al.avanza()
            Elemental.pd= T.noterminal(noterminal.id, noterminal.nlinea)
        elif mc_al.actual.cat in [ u'errordos', 'terminal' ]:
            error= None
            while mc_al.actual.cat == u'errordos':
                errordos = errordos1 = errordos_ = mc_al.actual
                mc_al.avanza()
                if error == None: error = code.empty()
                error.addBrother(errordos.codigo)
            if not mc_al.actual.cat == u'terminal':
                mc_error('<Elemental>',[ u'errordos', 'terminal' ])
            if mc_al.actual.cat == u'terminal':
                terminal = terminal1 = terminal_ = mc_al.actual
                mc_al.avanza()
            else:
                mc_error('<Elemental>', [u'terminal'])
            global directos
            if terminal.directo and terminal.id not in directos:
              directos.update((terminal.id,))
            Elemental.pd= Terminal(terminal.id, terminal.directo, error, terminal.nlinea)
        elif mc_al.actual.cat == u'accion':
            accion = accion1 = accion_ = mc_al.actual
            mc_al.avanza()
            Elemental.pd= Accion(accion.codigo, accion.nlinea)
        else:
            ParteDerecha = ParteDerecha1 = Atributos()
            abre = abre1 = abre_ = mc_al.actual
            mc_al.avanza()
            global enparentesis
            par= enparentesis
            enparentesis= True
            self.mc_analiza_ParteDerecha(ParteDerecha1)
            ParteDerecha_ = ParteDerecha1
            Elemental.pd= ParteDerecha.pd
            if mc_al.actual.cat == u'cierra':
                cierra = cierra1 = cierra_ = mc_al.actual
                mc_al.avanza()
            else:
                mc_error('<Elemental>', [u'cierra'])
            enparentesis= par
            if mc_al.actual.cat in [ u'asterisco', 'cruz', 'interrogante' ]:
                if mc_al.actual.cat == u'asterisco':
                    asterisco = asterisco1 = asterisco_ = mc_al.actual
                    mc_al.avanza()
                    if ParteDerecha.pd:
                      Elemental.pd= Iteracion(ParteDerecha.pd, abre.nlinea)
                elif mc_al.actual.cat == u'cruz':
                    cruz = cruz1 = cruz_ = mc_al.actual
                    mc_al.avanza()
                    if ParteDerecha.pd:
                      Elemental.pd= Repeticion(ParteDerecha.pd, abre.nlinea)
                else:
                    interrogante = interrogante1 = interrogante_ = mc_al.actual
                    mc_al.avanza()
                    if ParteDerecha.pd:
                      Elemental.pd= Opcional(ParteDerecha.pd, abre.nlinea)
    def mc_analiza_Lineas(self, Lineas):
        mc_al = self.mc_al
        self.mc_reintento.append(True)
        mc_reintentar= self.mc_reintentar
        while self.mc_reintento[-1]:
            self.mc_reintento[-1]= False
            try:
                if not mc_al.actual.cat in [ u'codigo', 'mc_EOF', 'noterminal' ]:
                    mc_error('<Lineas>', [ u'codigo', 'mc_EOF', 'noterminal' ])
                ParteDerecha = ParteDerecha1 = Atributos()
                inicial= None
                while mc_al.actual.cat in [ u'codigo', 'noterminal' ]:
                    if mc_al.actual.cat == u'noterminal':
                        noterminal = noterminal1 = noterminal_ = mc_al.actual
                        mc_al.avanza()
                        nt= T.noterminal(noterminal.id, noterminal.nlinea)
                        if inicial== None:
                          inicial= nt
                        if mc_al.actual.cat == u'flecha':
                            flecha = flecha1 = flecha_ = mc_al.actual
                            mc_al.avanza()
                        else:
                            errores.append(mc_al.linea(), u"Después del no terminal, debería venir una flecha")
                        global enparentesis
                        enparentesis= False
                        self.mc_analiza_ParteDerecha(ParteDerecha1)
                        ParteDerecha_ = ParteDerecha1
                        if mc_al.actual.cat == u'pyc':
                            pyc = pyc1 = pyc_ = mc_al.actual
                            mc_al.avanza()
                        else:
                            errores.append(mc_al.linea(), "Falta un punto y coma.")
                            if mc_al.actual.cat=="flecha":
                              errores.append(mc_al.linea(), "Creo que he juntado dos reglas.")
                              mc_al.avanza()
                            else:
                              mc_al.sincroniza(mc_aceptables["<Lineas>"], mc_abandonar)
                        if ParteDerecha.pd:
                          Lineas.l.append(Regla(nt, ParteDerecha.pd, noterminal.nlinea))
                        if ParteDerecha.error:
                          nt.tratamientoError(ParteDerecha.error)
                    else:
                        codigo = codigo1 = codigo_ = mc_al.actual
                        mc_al.avanza()
                        Lineas.codusuario / codigo.cod
                if not mc_al.actual.cat == u'mc_EOF':
                    mc_error('<Lineas>',[ u'codigo', 'mc_EOF', 'noterminal' ])
                Lineas.inicial= inicial
            except mc_error_sintaxis, (mc_nt, mc_t):
                errores.append(mc_al.linea(), u"Has comenzado una producción de manera extraña, buscaré algún comienzo mejor")
                mc_al.sincroniza(mc_aceptables["<Lineas>"], mc_abandonar)
                mc_reintentar()
        self.mc_reintento.pop()
    def mc_analiza_ParteDerecha(self, ParteDerecha):
        mc_al = self.mc_al
        self.mc_reintento.append(True)
        mc_reintentar= self.mc_reintentar
        while self.mc_reintento[-1]:
            self.mc_reintento[-1]= False
            try:
                if not mc_al.actual.cat in [ u'abre', 'accion', 'barra', 'cierra', 'errordos', 'noterminal', 'pyc', 'terminal', 'tokenerror' ]:
                    mc_error('<ParteDerecha>', [ u'abre', 'accion', 'barra', 'cierra', 'errordos', 'noterminal', 'pyc', 'terminal', 'tokenerror' ])
                Alternativa = Alternativa1 = Atributos()
                Alternativa2 = Atributos()
                ParteDerecha.error= None
                self.mc_analiza_Alternativa(Alternativa1)
                Alternativa_ = Alternativa1
                if Alternativa.pd:
                  l= [Alternativa.pd]
                else:
                  l= []
                  ParteDerecha.error= Alternativa.error
                while mc_al.actual.cat == u'barra':
                    barra = barra1 = barra_ = mc_al.actual
                    mc_al.avanza()
                    self.mc_analiza_Alternativa(Alternativa2)
                    Alternativa_ = Alternativa2
                    if Alternativa2.pd:
                      l.append(Alternativa2.pd)
                    else:
                      if ParteDerecha.error!= None:
                        avisos.append(mc_al.linea(), u"Ya tenía un tratamiento de error; pasaré de este de aquí.")
                      else:
                        ParteDerecha.error= Alternativa2.error
                if not mc_al.actual.cat in [ u'cierra', 'pyc' ]:
                    mc_error('<ParteDerecha>',[ u'barra', 'cierra', 'pyc' ])
                if len(l)== 0:
                  ParteDerecha.pd= None
                elif len(l)== 1 and ParteDerecha.error== None:
                  ParteDerecha.pd= l[0]
                else:
                  ParteDerecha.pd= Disyuncion(l, l[0].nl, ParteDerecha.error)
            except mc_error_sintaxis, (mc_nt, mc_t):
                if mc_al.actual.cat=="codigo":
                  mensaje= u"Parte derecha de la regla incorrecta: ¿te has olvidado del punto y coma? "
                else:
                  mensaje= u"Parte derecha de la regla incorrecta: esperaba ver "
                  if len(mc_t)> 1:
                    if not enparentesis:
                      try:
                        mc_t.remove("cierra")
                      except ValueError:
                        pass
                    mensaje+= u", ".join([_nombre[t] for t in mc_t[:-1]])
                    mensaje+= u" o "+_nombre[mc_t[-1]]
                  else:
                    mensaje+= _nombre[mc_t[0]]
                  mensaje+= u" y he visto "+_nombre[mc_al.actual.cat]
                errores.append(mc_al.linea(), mensaje)
                mc_al.sincroniza(mc_siguientes["<ParteDerecha>"], mc_abandonar)
                ParteDerecha.pd= None
                ParteDerecha.error= None
        self.mc_reintento.pop()
    def mc_analiza_tratEOF(self, tratEOF):
        mc_al = self.mc_al
        self.mc_reintento.append(True)
        mc_reintentar= self.mc_reintentar
        while self.mc_reintento[-1]:
            self.mc_reintento[-1]= False
            try:
                if not mc_al.actual.cat in [ u'codigo', 'errordos', 'mc_EOF', 'noterminal' ]:
                    mc_error('<tratEOF>', [ u'codigo', 'errordos', 'mc_EOF', 'noterminal' ])
                c = None
                while mc_al.actual.cat == u'errordos':
                    errordos = errordos1 = errordos_ = mc_al.actual
                    mc_al.avanza()
                    if c is None: c = code.empty()
                    c.addBrother(errordos_.codigo)
                if not mc_al.actual.cat in [ u'codigo', 'mc_EOF', 'noterminal' ]:
                    mc_error('<tratEOF>',[ u'codigo', 'errordos', 'mc_EOF', 'noterminal' ])
                tratEOF.codigo= c
            except mc_error_sintaxis, (mc_nt, mc_t):
                errores.append(mc_al.linea(), u"Al código inicial no le sigue el comienzo de una regla ni un tratamiento de error. Voy a saltar entrada hasta que encuentre algo.")
                mc_al.sincroniza(mc_primeros["<Lineas>"]+["errordos"], mc_abandonar)
                if mc_al.actual.cat=="errordos":
                  mc_reintentar()
        self.mc_reintento.pop()
if __name__ == '__main__':
    try:
        mc_main = main
    except NameError:
        def mc_main():
            AnalizadorSintactico(sys.stdin)
    mc_main()