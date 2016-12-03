# -*- coding: utf-8 -*-
import errores
import etiquetas
import Rossi
R=Rossi
import tipos

class NodoFuncion:
  def __init__(self, id, nlinea):
    self.id= id
    self.variables= []
    self.nlinea= nlinea
    self.tipo= tipos.Funcion

  def fijaPerfil(self, parametros, tipo):
    self.parametros= parametros
    self.tipoDevuelto= tipo

  def fijaCodigo(self, codigo):
    self.codigo= codigo

  def listaVariables(self):
    return self.variables

  def compsemanticas(self):
    for par in self.parametros:
      if not par.tipo.elemental():
        errores.semantico("El parametro %s tiene tipo compuesto." % par.id, par.nlinea)
    for var in self.variables:
      if not var.tipo.elemental():
        errores.semantico("La variable %s es local y tiene tipo compuesto." % var.id, var.nlinea)
    if not self.tipoDevuelto.elemental():
      errores.semantico("El tipo devuelto de las funciones debe ser elemental.", self.nlinea)
    self.codigo.compsemanticas()

  def fijaDireccion(self):
    self.etiqueta= etiquetas.nueva()
    self.salida= etiquetas.nueva()

  def generaFuncion(self, c):
    # Registro de activacion:
    #
    # -n: par 1
    # ...
    # -1: par n
    # 0: Retorno      <== FP
    # 1: FP anterior
    # 2: v. local 1
    # ...
    # m+1: v. local m
    for d in range(len(self.parametros)):
      self.parametros[d].fijaDireccion(d-len(self.parametros))
    for d in range(len(self.variables)):
      self.variables[d].fijaDireccion(d+2)

    c.append(R.Comentario("Funcion %s:" % self.id))
    c.append(R.Etiqueta(self.etiqueta))

    c.append(R.sw("ra", 0, "sp", "Guardamos la direccion de retorno"))
    c.append(R.sw("fp", 1, "sp","Guardamos el FP"))
    c.append(R.add("fp", "sp", "zero", "Nuevo FP"))
    c.append(R.addi("sp", "sp", len(self.variables)+2, "Incrementamos el SP"))
    c.append(R.Comentario("Comienzo del codigo de usuario"))
    self.codigo.generaCodigo(c)
    c.append(R.Comentario("Salida de la funcion."))
    c.append(R.Etiqueta(self.salida))
    c.append(R.subi("sp", "sp", len(self.parametros)+len(self.variables)+2, "Restauramos el SP"))
    c.append(R.lw("ra", 0, "fp", "Direccion de retorno"))
    c.append(R.lw("fp", 1, "fp", "Restauramos el FP"))
    c.append(R.jr("ra"))

  def arbol(self):
    pars= []
    for i in self.parametros:
      pars.append(str(i.tipo))
    return '(\n"Funcion"\n"nombre: %s"\n"perfil: %s-> %s"\n%s\n)' % (self.id, " ".join(pars), self.tipoDevuelto, self.codigo)

  def __str__(self):
    pars= []
    for i in self.parametros:
      pars.append(str(i.tipo))
    return "%s (perfil: %s -> %s)" % (self.id, " x ".join(pars), self.tipoDevuelto)
