import Rossi
R= Rossi

class Cadena:
  def __init__(self, valor):
    self.valor= valor

  def talla(self):
    return len(self.valor)+1

  def fijaDireccion(self, dir):
    self.dir= dir

  def inicializacion(self, c):
    c.append(R.asciiz(self.valor, self.dir))

  def __str__(self):
    return repr(self.valor)

