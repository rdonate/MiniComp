# -*- coding: utf-8 -*-
import os

errores=[]

def lexico(texto, nl):
  errores.append((nl,"Error lexico en linea %d: %s\n" % (nl, texto)))

def sintactico(texto, nl):
  errores.append((nl,"Error sintactico en linea %d: %s\n" % (nl, texto)))

def semantico(texto, nl):
  errores.append((nl,"Error semantico en linea %d: %s\n" % (nl, texto)))

def escribeErrores(f):
  errores.sort()
  for nl,i in errores:
    _escribe_error(f, i)

try:
  _ancho_linea= int(os.getenv("COLUMNS"))
except:
  _ancho_linea= None

if not _ancho_linea:
  _ancho_linea=80

_sangria= 5

def _escribe_error(f, mensaje):
  l= mensaje.split()
  pos= 0
  for i in range(len(l)):
    p= l[i]
    if i and pos< _ancho_linea:
      f.write(' ')
      pos= pos+1
    if pos+len(p)> _ancho_linea:
      f.write('\n'+' '*_sangria)
      pos= _sangria
    f.write(p)
    pos= pos+len(p)
  f.write('\n')
