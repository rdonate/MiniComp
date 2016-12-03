# -*- coding: utf-8 -*-

_dirLibre= 0

def asignaDir(l):
  global _dirLibre
  for v in l:
    v.fijaDireccion(_dirLibre)
    _dirLibre+= v.talla()
