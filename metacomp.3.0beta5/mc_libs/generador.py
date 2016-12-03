#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
##############################################################################
#
# metacomp 3.0beta5: a metacompiler for RLL(1) grammars
# Copyright (C) 2011 Juan Miguel Vilar and Andrés Marzal
#                    Universitat Jaume I, Castelló (Spain)
#
#  This program is free software; you can redistribute it and/or
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
# Fichero: generador.py
#

import code
from erNodes import Category, Concatenation, OrNode
import re2a

class CategoryInfo:
  """La información que se guarda para representar las categorías léxicas"""
  def __init__(self, n, cat, ff):
    """n: prioridad (menos es más prioritario)
       cat: categoria
       ff: función de tratamiento"""
    self.n = n
    self.cat = cat
    self.ff = ff

  def __cmp__(self, other):
    if other is None:
      return -1
    return cmp(self.n, other.n)

  def __str__(self):
    """Escribimos lo que nos interesa para su uso en metacomp"""
    return "(%s, %s)" % (repr(self.cat), self.ff)

def genera_analex(esplex, codificacion):
  """Genera un analizador léxico a partir de la especificación léxica. Esta es una
  lista de tuplas con categoría, función de tratamiento y expresión regular."""

  c = code.empty()

  #
  # Función auxiliar para escribir las categorías inmediatas
  #

  ( c
    / "def mc_pretty_cat(cat):"
    //   "if cat is None or cat[0]!='!':"
    //      "return cat"
    %    "else:"
    //      "return '\"%s\"' % cat[1:]"
    )

  #
  # Clase ComponenteLexico
  #
  ( c
    / "class ComponenteLexico:"
    //  "def __init__(self, cat, lexema, nlinea):"
    //    "self.cat = cat"
    /    "self.lexema = lexema"
    /    "self.nlinea = nlinea"
    %   "def __str__(self):"
    //    "s = ['%s: %s' % (repr(k), repr(v)) for k, v in self.__dict__.items() if k != 'cat']"
    /     "if s:"
    //       "return '%s (%s)' % (mc_pretty_cat(self.cat), ', '.join(s))"
    %     "else:"
    //       "return mc_pretty_cat(self.cat)"
    )
  #
  # Clase AnalizadorLexico:
  #
  ( c
    / "class AnalizadorLexico:"
    //  "def __init__(self, entrada):"
    //    "if isinstance(entrada, basestring):"
    //       "if isinstance(entrada, unicode):"
    //          "self.l = entrada"
    %        "else:"
    //          ( "self.l = entrada.decode('%s')" % codificacion )
    % None % "else:"
    //      "try:"
    //        "ll = entrada.readlines()"
    %       "except:"
    //        u"sys.stderr.write('Error: no he podido leer la entrada ¿es un fichero?\\n')"
    /         "sys.exit(1)"
    %       ( "ll = [ l.decode('%s') for l in ll]" % codificacion )
    /       "self.l = ''.join(ll)"
    /       "entrada.close()"
    %     "self.nlactual = 1"
    /     "self.actual = ComponenteLexico(None, None, 0)"
    /     "try:"
    //      "self.error_lexico = error_lexico"
    %     "except NameError:"
    //      "self.error_lexico = self._error_lexico"
    %     "self.i = 0"
    )

  # Tratamiento por defecto del error léxico:
  ( c
    // "def _error_lexico(self, linea_error, cars):"
    //   (u"sys.stderr.write((u'Error léxico no tratado en línea %%d: No esperaba %%s.\\n' %% (linea_error, repr(cars))).encode('%s'))" % codificacion )
    /    "sys.exit(1)"
  )
  # Método línea:
  ( c
    // "def linea(self):"
    //    "return self.actual.nlinea"
  )
  # Método sincroniza:
  ( c
    //"def sincroniza(self, sincr, enEOF = mc_abandonar):"
    //   "while self.actual.cat not in sincr and self.actual.cat != 'mc_EOF':"
    //     "self.avanza()"
    %    "if self.actual.cat =='mc_EOF' and not 'mc_EOF' in sincr:"
    //     "enEOF()"
    )

  # Método avanza:

  ( c
    // "def avanza(self):"
    //    "if self.i >= len(self.l):"
    //       "self.actual = ComponenteLexico('mc_EOF', '', self.nlactual)"
    /        "return self.actual"
    %    "carsError, lineaError = [], 0"
    /    "while 1:"
    //      "(info, ni) = self.analiza(self.i, self.l)"
    /       "if not info is None:"
    //          "nl = self.nlactual"
    /           "if carsError:"
    //             "self.error_lexico(lineaError, ''.join(carsError))"
    /              "self.nlactual += carsError.count('\\n')"
    /              "carsError, lineaError = [], 0"
    %          "cat, ff = info"
    /          "lexema = self.l[self.i:ni]"
    /          "self.i = ni"
    /          "self.nlactual += lexema.count('\\n')"
    /          "componente = ComponenteLexico(cat, lexema, nl)"
    /          "if ff:"
    //            "ff(componente)"
    %          "if not componente.cat is None:"
    //            "self.actual = componente"
    /             "return componente"
    %          "continue"
    %       "else:"
    //         "if self.i >= len(self.l):"
    //           "if carsError:"
    //              "self.error_lexico(lineaError, ''.join(carsError))"
    /               "self.nlactual += carsError.count('\\n')"
    %            "self.actual = ComponenteLexico('mc_EOF', '', self.nlactual)"
    /            "return self.actual"
    %          "if lineaError == 0: lineaError = self.nlactual"
    /          "carsError.append(self.l[self.i])"
    /          "self.i += 1"
    % None % "return self.actual"
  )

  allEr = OrNode ([ Concatenation(er, Category(CategoryInfo(n, cat, ff))) for n, (cat, ff, er) in enumerate(esplex) ])
  c // re2a.re2a(allEr).toCode("analiza", True)
  return c

def diccionarios(gramatica):
  # Diccionarios de primeros, siguientes, aceptables y anulables:
  c = code.empty()
  c / "mc_primeros = {"
  for nt in gramatica.noterminales:
    pr = ", ".join([ repr(p) for p in nt.primeros()])
    c // ("'%s' : [%s]," % (nt, pr) )
  c/ "}"

  c / "mc_siguientes = {"
  for nt in gramatica.noterminales:
    pr = ", ".join([ repr(p) for p in nt.siguientes()])
    c // ("'%s' : [%s]," % (nt, pr) )
  c/ "}"

  c / "mc_aceptables = {"
  for nt in gramatica.noterminales:
    pr = ", ".join([ repr(p) for p in nt.aceptables()])
    c // ("'%s' : [%s]," % (nt, pr) )
  c/ "}"

  c / "mc_anulables = {"
  for nt in gramatica.noterminales:
    c // ("'%s' : %s," % (nt, nt.anulable()) )
  c/ "}"

  return c

def genera_excepciones():
  # Las excepciones y algunas funciones auxiliares:
  return ( code.empty()
           / "class mc_error_sintaxis(Exception): pass"
           / "class mc_error_noEOF(Exception): pass"
           / "class mc_error_abandonar(Exception): pass"
           / "def mc_error(nt, esp):"
           //   "raise mc_error_sintaxis, (nt, esp)"
           %  "def mc_abandonar():"
           //   "raise mc_error_abandonar"
           )

def genera_sintactico(gram, traza, codificacion):
  c = code.empty()
  # La clase para los atributos:
  c / "class Atributos: pass"

  # Preparamos el tratamiento del error cuando hay entrada tras EOF
  if gram.noEOF: # Si se trata el error noEOF
    tratEOF = code.sentence("mc_al = self.mc_al") / gram.noEOF
  else:
    tratEOF = (
      code.sentence(u"sys.stderr.write((u'Error no tratado en línea %%d:\\n' %% self.mc_al.actual.nlinea).encode('%s'))" % codificacion)
      /  "sys.stderr.write('He encontrado entrada donde esperaba ver el final del fichero\\n')"
      /  "sys.exit(1)"
      )



  # El analizador sintáctico:
  ( c
    / "class AnalizadorSintactico:"
    //   "def __init__(self, entrada, entorno = None):"
    //      "self.mc_entorno = entorno"
    /      "self.mc_al = AnalizadorLexico(entrada)"
    /      "self.mc_al.avanza()"
    /      "self.mc_reintento = [True]"
    /      "mc_reintentar = self.mc_reintentar"
    /      "while self.mc_reintento[-1]:"
    //        "self.mc_reintento[-1] = False"
    /        ("self.%s = Atributos()""" % gram.inicial.nombre)
    /         "try:"
    //           ("self.mc_analiza_%s(self.%s)""" % (gram.inicial.nombre,gram.inicial.nombre))
    /             "if self.mc_al.actual.cat != 'mc_EOF':"
    //               "raise mc_error_noEOF"
    % None %  "except mc_error_sintaxis, (nt, esp):"
    //            u"sys.stderr.write('Error no tratado en línea %d:\\n' % self.mc_al.actual.nlinea)"
    /             (u"sys.stderr.write((u'Estaba analizando la expansión del no terminal %%s y he encontrado\\n el terminal %%s.\\n' %% (nt, self.mc_al.actual)).encode('%s'))" % codificacion)
    /             "if len(esp)==1:"
    //               (u"sys.stderr.write((u'Sólo valía un %%s.\\n' %% mc_pretty_cat(esp[0])).encode('%s'))" % codificacion)
    %             "else:"
    //               (u"sys.stderr.write((u'Tendría que haber sido uno de los siguientes: %%s.\\n' %% ','.join(map(mc_pretty_cat,esp))).encode('%s'))" % codificacion )
    %             "sys.exit(1)"
    %      "except mc_error_noEOF:"
    //         tratEOF
    %      "except mc_error_abandonar:"
    //         "pass"
    % None % None
    %  "def mc_reintentar(self):"
    //   "self.mc_reintento[-1] = True"
    )
  # Código de los no terminales:
  for nt in gram.noterminales:
    c // nt.genera_codigo(traza)
  return c

def genera_puro(gram, traza):
  c = code.empty()
  # El analizador sintáctico:
  ( c
    /"class AnalizadorSintactico:"
    // "def __init__(self, entrada, entorno = None):"
    //    "self.mc_al = AnalizadorLexico(entrada)"
    /     "self.mc_al.avanza()"
    /     "try:"
    //      ("self.mc_analiza_%s()" % gram.inicial.nombre)
    /       "if self.mc_al.actual.cat != 'mc_EOF':"
    //         "raise mc_error_noEOF"
    % None %
    "except mc_error_sintaxis, (nt,esp):"
    //       "self.mc_error = True"
    /        "self.mc_lineaError = self.mc_al.actual.nlinea"
    /        "self.mc_ntError = nt"
    /        "self.mc_tError = self.mc_al.actual"
    /        "self.mc_esperado = esp"
    %     "except mc_error_noEOF:"
    //       "self.mc_error = True"
    /        "self.mc_lineaError = self.mc_al.actual.nlinea"
    /        "self.mc_ntError = None"
    /        "self.mc_tError = self.mc_al.actual"
    /        "self.mc_esperado = ['mc_EOF']"
    %     "else:"
    //       "self.mc_error = False"
    )
  # Código de los no terminales:
  for nt in gram.noterminales:
    c // nt.genera_codigo(traza, True)
  return c

def genera_analizador(gram, elexica, codusuario, traza, salida, codificacion, analex, tipoAnalizador):
  c = code.empty()
  # Preámbulo
  ( c
    / "#!/usr/bin/env python"
    / ("# -*- coding: %s -*-" % codificacion )
    / u"# Este código ha sido generado por metacomp, versión 3.0beta5"
    / "import sys")
  if traza =="t" or traza =="A":
    ( c
      / "sangrado_traza = 0"
      / "def mc_traza(l):"
      //  ("sys.stderr.write((sangrado_traza*' '+l).encode('%s'))" % codificacion)
      % "def mc_dentro_traza():"
      //  "global sangrado_traza"
      /   "sangrado_traza += 2"
      % "def mc_fuera_traza():"
      //  "global sangrado_traza"
      /   "sangrado_traza -= 2"
      )
  c / genera_excepciones()
  # Analizador léxico:
  if not analex:
    c / genera_analex(elexica, codificacion)
  else:
    c / ("from %s import AnalizadorLexico" % analex)

  # El código del usuario:
  c / u"# Código de usuario"
  c / codusuario

  if tipoAnalizador == "normal":
    # Los primeros y siguientes:
    c / diccionarios(gram)

    # El sintáctico:
    c / genera_sintactico(gram, traza, codificacion)

    # La llamada a main:
    ( c
      /  "if __name__ == '__main__':"
      //   "try:"
      //      "mc_main = main"
      %    "except NameError:"
      //      "def mc_main():"
      //        "AnalizadorSintactico(sys.stdin)"
      % None %
         "mc_main()"
      )
  elif tipoAnalizador =="puro":
    # Los primeros y siguientes:
    c / diccionarios(gram)

    # El sintáctico:
    c / genera_puro(gram, traza)

    # La llamada a main:
    ( c
      / "if __name__=='__main__':"
      //  "try:"
      //     "mc_main = main"
      %   "except NameError:"
      //      "def mc_main():"
      //        "A = AnalizadorSintactico(sys.stdin)"
      /         "if not A.mc_error:"
      //          u"print 'La entrada no tiene errores sintácticos.'"
      %         "else:"
      //           u"print 'Hay un error de sintaxis en la línea %d, provocado por el componente\\n\\t%s' % ( A.mc_lineaError, A.mc_tError)"
      /            "if A.mc_ntError != None:"
      //             "print 'y detectado al intentar analizar en no terminal %s.' % A.mc_ntError"
      %           "else:"
      //             "print 'y detectado cuando se esperaba el fin de la entrada.'"
      % None % None % None %
      "mc_main()"
      )
  elif tipoAnalizador =="lexico": # Si sólo generamos el léxico:
    ( c
      / "if __name__=='__main__':"
      //  "try:"
      //     "mc_main = main"
      %   "except NameError:"
      //      "def mc_main():"
      //        "A = AnalizadorLexico(sys.stdin)"
      /         "comp = A.avanza()"
      /         "while comp.cat != 'mc_EOF':"
      //           "print A.actual"
      /            "comp = A.avanza()"
      % None % None %
      "mc_main()"
      )
  else:
    sys.stderr.write("Error interno.\n")
    sys.stderr.write("Se ha especificado un tipo de analizador distinto de normal, puro y léxico.\n")
    sys.exit(1)
  salida.write(unicode(c).encode(codificacion))

def _main():
  import REParser
  l = []
  for cat, ff, er in [("id", "procesaID", "[a-zA-Z][a-zA-Z0-9]*"),
                      (None, None, "[ \\t\\n]")
                      ]:
    exp = REParser.reParse(er)
    l.append((cat, ff, exp))
  c = genera_analex(l, "utf-8")
  print c

if __name__=="__main__":
  _main()

