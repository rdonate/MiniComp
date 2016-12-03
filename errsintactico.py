# -*- coding: utf-8 -*-

import errores

_emitir= 1

_terminales= {
  "!;": "un punto y coma",
  "!,": "una coma",
  "!:": "dos puntos",
  "![": "un corchete abierto",
  "!]": "un corchete cerrado",
  "!(": "un parentesis abierto",
  "!)": "un parentesis cerrado",
  "!:=": "un simbolo de asignacion",
  "cad": "un literal de cadena",
  "id": "un identificador",
  "num": "un numero entero",
  "opcom": "un operador de comparacion",
  "opad": "un operador aditivo",
  "opmul": "un operador multiplicativo"
  }

_noTerminales= {
  "<AccesoVariable>": "un acceso a variable",
  "<Comparado>": "un operador",
  "<Compuesta>": "una sentencia compuesta",
  "<Definicion>": "una definicion de variables",
  "<Expresion>": "una expresion",
  "<Funcion>": "una funcion",
  "<Globales>": "la definicion de variables globales",
  "<Llamada>": "una llamada a subrutina",
  "<Perfil>": "el perfil de una subrutina",
  "<Producto>": "una expresion",
  "<Programa>": "el programa",
  "<Sentencia>": "una sentencia",
  "<Termino>": "una expresion",
  "<Tipo>": "una definicion de tipo"
  }

def _trataEOF():
  global _emitir
  _emitir= 0

def trataError(mc_al, mc_nt, t):
  if _emitir:
    if _terminales.has_key(mc_al.actual.cat):
      term= _terminales[mc_al.actual.cat]
    else:
      term= "la palabra reservada %s" % mc_al.actual.cat
    errores.sintactico ("Estaba analizando %s y me he encontrado con %s donde no tocaba." %
                        (_noTerminales[mc_nt], term), mc_al.linea())
  mc_al.sincroniza(_primeros[t]+_siguientes[t], _trataEOF)
  return mc_al.actual.cat in _primeros[t]

def inicializa(pr, sig):
  global _primeros, _siguientes
  _primeros= pr
  _siguientes= sig
