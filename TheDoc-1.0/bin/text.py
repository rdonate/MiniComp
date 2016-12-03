# -*- coding: latin1 -*-

from string import *
from Rossi import *
try:
  import readline 	# Añade historia de comandos, soporte , etc.
except:
  pass

# Interfaz del emulador en modo texto

class Text:
  def __init__(self, fich, batch=None, clean=None):
    self.rossi = Rossi()
    self.fich = fich
    self.clean = clean
    self.lineas = []
    self.breakpoints = {}
    self.pasos = 0
    self.recargable = 0
    self.reseteable = 0
    self.verboso = 0
    self.ordenes = { "load"      : self.load,
    		     "reload"    : self.reload,
		     "step"      : self.step,
		     "execute"   : self.execute,
		     "breakpoint": self.breakpoint,
		     "program"   : self.program,
		     "memory"    : self.memory,
		     "integers"  : self.integers,
		     "reals"     : self.reals,
		     "spints"    : self.spints,
		     "spreals"   : self.spreals,
		     "verbose"   : self.verbose,
		     "reset"     : self.reset,
		     "help"      : self.help,
		     "exit"      : self.exit
		   }
    self.brkUsado = 0 # Indica si la máquina ya se ha detenido en el BRK actual
    # Añadimos a las órdenes existentes las órdenes abreviadas
    for cmd in self.ordenes.keys():
      for i in range(len(cmd)-1):
        if self.ordenes.has_key(cmd[:i+1]): # Si el prefijo ya está añadido
	  self.ordenes[cmd[:i+1]] = self.prefijoAmbiguo
	else:
	  self.ordenes[cmd[:i+1]] = self.ordenes[cmd]
    # Si tenemos que ejecutarlo en modo batch y no se ha especificado
    # ningún fichero, leemos de la entrada estándar
    if batch and not fich:
      fich = "stdin"
    # Si se ha especificado el fichero, lo cargamos ya
    if fich:
      self.load(fich)
    if batch:
      # Si no hay ningún error de análisis y se ha leído un fichero, lo ejecutamos "de tirón"
      if not self.rossi.err.e and self.lineas:
        self.execute()
    else:
      self.mainloop()

  def prefijoAmbiguo(self):
    print "El prefijo introducido es ambiguo!"

  def mainloop(self):
    print "Bienvenido a TheDoc: un emulador para la máquina virtual ROSSI."
    print "Escribe 'help' para mostrar las órdenes disponibles."
    while 1:
      try:
        c = raw_input(">> ")
        self.ejecutaOrden(c)
      except (KeyboardInterrupt, EOFError):
        print "\nHasta otra!"
	break

  def ejecutaOrden(self, cmd):
    l = split(cmd) # Lista de la forma: [orden, arg1, ..., argn]
    try:
      if l == []:
        pass
      elif len(l) == 1 and self.ordenes.has_key(l[0]): # Orden sin argumentos
        apply(self.ordenes[l[0]], ())
      elif self.ordenes.has_key(l[0]): # Orden con argumentos
        apply(self.ordenes[l[0]], tuple(l[1:]))
      else:
        print "Orden incorrecta: %s." % repr(l[0])
    except TypeError:
      print "Número de argumentos incorrecto."
    except ValueError:
      print "Argumentos con formato incorrecto."

  def load(self, fich):
    self.fich = fich
    self.pasos = 0
    self.breakpoints = {}
    self.brkUsado = 0
    try:
      if fich == "stdin":
        f = sys.stdin
      else:
        f = open(fich, "r")
      self.lineas = f.readlines()
      if f != sys.stdin: # OJO: no puedo cerrar stdin !!!
        f.close()
      self.recargable = 1
      self.rossi.inicializa()
      self.rossi.cargaPrograma(self.lineas)
      if self.rossi.err.e:
        self.muestraErrores(self.rossi.err.e)
	self.reseteable = 0
      else:
        self.reseteable = 1
    except IOError, e:
      print "No puedo cargar el fichero %s: %s." % (repr(fich), str(e))
    except KeyboardInterrupt:
      print "Hasta otra!"
      sys.exit(-1)
    
  def reload(self):
    if not self.recargable:
      print "Imposible recargar fichero: no hay ningún fichero cargado."
    else:
      self.pasos = 0
      self.brkUsado = 0
      self.breakpoints = {}
      try:
        f = open(self.fich, "r")
	self.lineas = f.readlines()
	f.close()
	self.rossi.inicializa()
	self.rossi.cargaPrograma(self.lineas)
	if self.rossi.err.e:
	  self.muestraErrores(self.rossi.err.e)
	  self.reseteable = 0
	else:
	  self.reseteable = 1
      except IOError, e:
        print "No puedo recargar el fichero %s: %s." % (repr(self.fich), str(e))

  def muestraErrores(self, lista):
    print "Se han encontrado los siguientes errores:"
    for error in lista:
      print error

  def step(self):
    if self.rossi.programa:
      if self.rossi.estado == Rossi.FUNCIONANDO:
        self.pasos += 1
      # Si está activado el modo verboso, muestro la instrucción que se va a ejecutar
      if self.verboso:
        self.program(self.rossi.pc, self.rossi.pc)
      self.rossi.ejecutaPaso()
      if self.rossi.NOP == 1:
        self.pasos -= 1 # La ejecución de nop no se tiene en cuenta
      # Si está activado el modo verboso, mostramos qué se ha actualizado
      if self.verboso:
        if self.rossi.re.cambios:
          print self.rossi.re.ultReg + " " * (7 - len(self.rossi.re.ultReg)) + ": " + str(self.rossi.re.ultValor)
        if self.rossi.rr.cambios:
          print self.rossi.rr.ultReg + " " * (8 - len(self.rossi.rr.ultReg)) + ": " + str(self.rossi.rr.ultValor)
        if self.rossi.mem.cambios:
          if not self.rossi.ASCIIZ:
	    print "Memoria [%d] : " % self.rossi.mem.ultDir, self.rossi.mem.ultValor
	  else:
	   for i in range(self.rossi.ASCIIZ_POS, self.rossi.mem.ultDir+1):
	     print "Memoria [%d] : " % i, self.rossi.mem.m[i]
      if self.rossi.estado == Rossi.ERROR: # Ha habido un error de ejecución
        print "MÁQUINA DETENIDA !!!"
        print "ERROR DE EJECUCIÓN: %s" % self.rossi.error_msg
        print "PC: %d" % self.rossi.pc
      elif self.rossi.estado == Rossi.PARADO:
        if not self.clean: # Podemos imprimir estadísticas
	  print "\n[ Ejecución finalizada ]"
	  print "REPG usados: %3d" % (len(self.rossi.re.r.keys()) - 7)
	  print "RRPG usados: %3d" % (len(self.rossi.rr.r.keys()) - 2)
	  print "Pasos: %d" % self.pasos
	else:
	  # Imprimimos información adicional por la salida de error estándar
	  sys.stderr.write("\n[ Ejecución finalizada ]\n")
	  sys.stderr.write("REPG usados: %3d\n" % (len(self.rossi.re.r.keys()) - 7))
	  sys.stderr.write("RRPG usados: %3d\n" % (len(self.rossi.rr.r.keys()) - 2))
	  sys.stderr.write("Pasos: %d\n" % self.pasos)
    else:
      print "No se ha cargado ningún programa correcto."
    
  # Sólo se detiene en un break la primera vez que lo encuentra
  def execute(self):
    if self.rossi.programa:
      while 1:
        if self.breakpoints.has_key(str(self.rossi.pc)):
          if not self.brkUsado:
	    self.brkUsado = 1
            break
	  else:
	    self.brkUsado = 0
        self.step()
        if self.rossi.estado != Rossi.FUNCIONANDO:
          break
    else:
      print "No se ha cargado ningún programa correcto."

  def breakpoint(self, linea=None):
    if linea == None: # Mostramos los breakpoints definidos
      if self.breakpoints:
        keys = self.breakpoints.keys()
	keys.sort()
	print "Se han definido los siguientes breakpoints:"
	for i in keys:
	  self.program(i, i)
    elif long(linea) >= 0 and long(linea) < len(self.lineas):
      if self.breakpoints.has_key(linea): # Si existe, lo eliminamos
        del self.breakpoints[linea]
      else:
        self.breakpoints[linea] = "" # Si no, lo añadimos
    else:
      print "Número de línea fuera de rango."

  def program(self, start=0, end=None):
    if end == None:
      end = len(self.lineas)
    start = long(start)
    end = long(end)
    p = self.lineas[start:end+1] # Líneas que debemos mostrar
    nl = start # Indica el número de línea en el que estamos
    for i in p:
      if i[-1] == "\n":
        i = i[:-1] # Eliminamos el salto de línea
      if nl == self.rossi.pc: # Si es la siguiente instrucción a ejecutar, la marcamos
        print "*",
      else:
        print " ",
      if self.breakpoints.has_key(str(nl)): # Si la línea tiene un brk, lo marcamos
        print " BRK",
      else:
        print "    ",
      print "%4d| %s" % (nl, i)
      nl += 1

  def memory(self, start=0, end=None):
    keys = self.rossi.mem.m.keys()
    keys.sort()
    start = long(start)
    if end:
      end = long(end)
    for i in keys:
      if i >= start:
	if not end or i <= end:
	  print " " * (4 - len(str(i))), i, ":", self.rossi.mem.m[i]

  def integers(self, start=0, end=None):
    start = long(start)
    if end:
      end = long(end)
    keys = self.rossi.re.r.keys() # Todos los registros enteros
    num = []
    for i in keys:
      if i[1] == "r" and i != "$ra":
        num.append(long(i[2:])) # num contiene los números de los reg. de prop. gral.
    num.sort()
    rdo = []
    for i in num:
      if i >= start and (not end or i <= end):
        rdo.append("$r" + str(i))
    for i in rdo:
      print i + " " * (6 - len(i)) + ": " + str(self.rossi.re[i])

  def reals(self, start=0, end=None):
    start = long(start)
    if end:
      end = long(end)
    keys = self.rossi.rr.r.keys() 
    num = []
    for i in keys:
      if i not in ["$fzero", "$fa"]:
        num.append(long(i[2:]))
    num.sort()
    rdo = []
    for i in num:
      if i >= start and (not end or i <= end):
        rdo.append("$f" + str(i))
    for i in rdo:
      print i + " " * (6 - len(i)) + ": " + str(self.rossi.rr[i])

  def spints(self):
    print "$zero : %d" % self.rossi.re["$zero"]
    print "$sp   :",
    try:
      print self.rossi.re["$sp"]
    except errores.RegVacioError:
      print
    print "$fp   :",
    try:
      print self.rossi.re["$fp"]
    except errores.RegVacioError:
      print
    print "$ra   :",
    try:
      print self.rossi.re["$ra"]
    except errores.RegVacioError:
      print
    print "$sc   :",
    try:
      print self.rossi.re["$sc"]
    except errores.RegVacioError:
      print
    print "$a0   :",
    try:
      print self.rossi.re["$a0"]
    except errores.RegVacioError:
      print
    print "$a1   :",
    try:
      print self.rossi.re["$a1"]
    except errores.RegVacioError:
      print

  def spreals(self):
    print "$fzero : %f" % self.rossi.rr["$fzero"]
    print "$fa    :",
    try:
      print self.rossi.rr["$fa"]
    except errores.RegVacioError:
      print

  def reset(self):
   if self.reseteable:
     self.rossi.inicializa()
     self.pasos = 0
     self.brkUsado = 0
     #self.breakpoints = {} # No eliminamos los breakpoints al resetar la máquina

  def verbose(self):
    if self.verboso:
      self.verboso = 0
      print "Modo verboso desactivado."
    else:
      self.verboso = 1
      print "Modo verboso activado."

  def help(self):
    print "load file       : carga el fichero 'file'."
    print "reload          : recarga el último fichero cargado."
    print "step            : avanza un paso en la ejecución del programa."
    print "execute         : ejecuta el programa hasta el final o hasta encontrar un error "
    print "                  o un breakpoint."
    print "breakpoint [n]  : alterna un breakpoint en la línea n o muestra los breakpoints "
    print "                  definidos."
    print "program [n [m]] : muestra el programa desde la línea n hasta m."
    print "memory [n [m]]  : muestra el contenido de la memoria, desde la posición n hasta "
    print "                  la m."
    print "integers [n [m]]: muestra el contenido de los registros enteros de propósito ge-"
    print "                  neral desde el registro $rn hasta el $rm."
    print "reals [n [m]]   : muestra el contenido de los registros reales de propósito ge-"
    print "                  neral desde el registro $fn hasta el $fm."
    print "spints          : muestra el contenido de los registros enteros de propósito es-"
    print "                  pecífico."
    print "spreals         : muestra el contenido de los registros reales de propósito es-"
    print "                  pecífico."
    print "verbose         : alterna la verbosidad."
    print "reset           : inicializa la máquina, manteniendo cargado el programa actual."
    print "help            : muestra este mensaje."
    print "exit            : sale del emulador."
  
  def exit(self):
    print "Hasta otra!"
    sys.exit(0)
