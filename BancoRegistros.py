class BancoRegistros:
  def __init__(self):
    self.libres= []  # Registros ya liberados
    self.ractivos= [] # Registros activos
    self.rlibre= 0   # Primer registro no utilizado nunca

  def reserva(self):
    if self.libres==[]:
      r= self.rlibre
      self.rlibre+= 1
    else:
      r= self.libres.pop()
    self.ractivos.append(r)
    return r

  def libera(self, r):
    self.ractivos.remove(r)
    self.libres.append(r)

  def activos(self):
    return self.ractivos[:]

