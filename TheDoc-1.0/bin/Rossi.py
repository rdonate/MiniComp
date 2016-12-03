# -*- coding: latin1 -*-

from registros import *
from memoria import *
import errores
import parser
import sys

class Rossi:
  [PARADO, FUNCIONANDO, ERROR] = range(3)  # Estados en los que puede encontrarse la máquina
  
  def __init__(self):
    self.re = RegEnteros() 	 # Banco de registros enteros
    self.rr = RegReales() 	 # Banco de registros reales
    self.mem = Memoria() 	 # Memoria
    self.err = errores.Errores() # Gestiona los errores de análisis
    self.etiq = {}		 # Almacena las etiquetas definidas etiq["etiqueta"] = num_linea
    self.refet = {}		 # Para cada et a la que se referencia, se almacena un lista con las líneas en que se referencia
    self.sigsub = []		 # Almacena las líneas que son la siguiente a una llamada a subrutina (jal)
    self.programa = []		 # Contiene tuplas de la forma (instrucción, (argumentos))
    self.pc = 0			 # Contador de programa: apunta siempre a la SIGUIENTE instrucción a ejecutar
    self.error_msg = None	 # El error que ha llevado al estado ERROR
    self.estado = Rossi.PARADO   # Estado en el cual se encuentra la máquina
    self.NOP = 0		 # Indica si la última instrucción ejecutada ha sido nop
    self.ASCIIZ = 0		 # Indica si la última instrucción ejecutada ha sido un asciiz
    self.ASCIIZ_POS = None       # Indica la posición de comienzo de la cadena del asciiz
    self.entrada = None		 # Determina la función externa que le proporciona la entrada a la máquina
    self.salida = None		 # Determina la función externa a la que la máquina le proporciona la salida

    # Asocia la función a ejecutar para cada instrucción válida del lenguaje e indica el formato de cada
    # uno de sus operandos:
    # r : registro entero
    # f : registro real
    # R : inmediato entero
    # F : inmediato real
    # e : etiqueta
    # n : indirecto a registro
    self.instrucciones = { "add"    : (self.add, ("r", "r", "r")),
  		           "addi"   : (self.addi, ("r", "r", "R")),
		           "sub"    : (self.sub, ("r", "r", "r")),
		           "subi"   : (self.subi, ("r", "r", "R")),
		           "mult"   : (self.mult, ("r", "r", "r")),
		           "multi"  : (self.multi, ("r", "r", "R")),
		           "div"    : (self.div, ("r", "r", "r")),
		           "divi"   : (self.divi, ("r", "r", "R")),
		           "mod"    : (self.mod, ("r", "r", "r")),
		           "modi"   : (self.modi, ("r", "r", "R")),
		           "not"    : (self.xnot, ("r", "r")),
			   "la"     : (self.la, ("r", "e")),
		           "lw"     : (self.lw, ("r", "n")),
		           "sw"     : (self.sw, ("r", "n")),
			   "save"   : (self.save, ("r", "n")),
			   "rest"   : (self.rest, ("r", "n")),
		           "beq"    : (self.beq, ("r", "r", "e")),
		           "bne"    : (self.bne, ("r", "r", "e")),
		           "bge"    : (self.bge, ("r", "r", "e")),
		           "bgt"    : (self.bgt, ("r", "r", "e")),
		           "ble"    : (self.ble, ("r", "r", "e")),
		           "blt"    : (self.blt, ("r", "r", "e")),
		           "j"      : (self.j, ("e")),
		           "jal"    : (self.jal, ("e")),
		           "jr"     : (self.jr, ("r")),
			   "jalr"   : (self.jalr, ("r")),
		           "fadd"   : (self.fadd, ("f", "f", "f")),
		           "faddi"  : (self.faddi, ("f", "f", "F")),
		           "fsub"   : (self.fsub, ("f", "f", "f")),
		           "fsubi"  : (self.fsubi, ("f", "f", "F")),
		           "fmult"  : (self.fmult, ("f", "f", "f")),
		           "fmulti" : (self.fmulti, ("f", "f", "F")),
		           "fdiv"   : (self.fdiv, ("f", "f", "f")),
		           "fdivi"  : (self.fdivi, ("f", "f", "F")),
		           "flw"    : (self.flw, ("f", "n")),
		           "fsw"    : (self.fsw, ("f", "n")),
			   "fsave"  : (self.fsave, ("f", "n")),
			   "frest"  : (self.frest, ("f", "n")),
		           "fbeq"   : (self.fbeq, ("f", "f", "e")),
		           "fbne"   : (self.fbne, ("f", "f", "e")),
		           "fbge"   : (self.fbge, ("f", "f", "e")),
		           "fbgt"   : (self.fbgt, ("f", "f", "e")),
		           "fble"   : (self.fble, ("f", "f", "e")),
		           "fblt"   : (self.fblt, ("f", "f", "e")),
		           "syscall": (self.syscall, ()),
			   "toint"  : (self.toint, ("r", "f")),
			   "tofloat": (self.tofloat, ("f", "r"))
 		        }

  # Inicializa el contenido de los registros, la memoria y los errores y hace que el
  # PC apunte a la primera instrucción. Si existe algún programa cargado, éste se mantiene.
  def inicializa(self):
    self.re.inicializa()
    self.rr.inicializa()
    self.mem.inicializa()
    self.err.inicializa()
    self.pc = 0
    self.error_msg = None
    self.estado = Rossi.FUNCIONANDO
    self.NOP = 0
    self.ASCIIZ = 0
    self.ASCIIZ_POS = None
   
  def declaraEtiqueta(self, et, nl):
    if self.etiq.has_key(et):
      self.err.etiqRedefError(et, nl)
    else:
      self.etiq[et] = nl

  def anyadeInstruccion(self, instruccion):
    self.programa.append(instruccion)
   
  def cargaPrograma(self, lineas):
    self.programa = []
    self.etiq = {}
    self.refet = {}
    self.sigsub = []
    p = parser.Parser(self, lineas)
    p.parsea()
    # Comprobamos que las etiquetas a las que se referencia están definidas
    for e in self.refet.keys():
      if not self.etiq.has_key(e):
        for l in self.refet[e]:
	  self.err.etiqNoDefError(e, l)
    if self.err.e:
      self.programa = []
      self.err.e.sort()
    else:
      self.estado = Rossi.FUNCIONANDO
  
  def ejecutaPaso(self):
    if self.estado == Rossi.FUNCIONANDO:
      self.pc += 1
      try:
	self.mem.cambios, self.re.cambios, self.rr.cambios = 0, 0, 0
	self.NOP, self.ASCIIZ = 0, 0
        apply(self.programa[self.pc-1][0], self.programa[self.pc-1][1])
      except errores.SysNoCodError        : self.hSysNoCodError()
      except errores.SysCodError, c       : self.hSysCodError(c)
      except errores.SysEnteroError, v    : self.hSysEnteroError(v)
      except errores.SysRealError, v      : self.hSysRealError(v)
      except errores.SysCharError, v      : self.hSysCharError(v)
      except errores.RegVacioError, r     : self.hRegVacioError(r)
      except errores.MemEnteroError, d    : self.hMemEnteroError(d)
      except errores.MemRealError, d      : self.hMemRealError(d)
      except errores.MemAccesoError, d    : self.hMemAccesoError(d)
      except errores.MemDirNegError, d    : self.hMemDirNegError(d)
      except errores.DivZeroError         : self.hDivZeroError()
      except errores.ModZeroError         : self.hModZeroError()
      except errores.JDestError,d         : self.hJDestError(d)
      except IndexError                   : self.hPCRangoError()

  #################
  # INSTRUCCIONES #
  #################

  # El parser asegura que las etiquetas que aparecen están definidas.

  def add(self, rd, rs, rt):
    self.re[rd] = self.re[rs] + self.re[rt]
  
  def addi(self, rd, rs, entero):
    self.re[rd] = self.re[rs] + entero
  
  def sub(self, rd, rs, rt):
    self.re[rd] = self.re[rs] - self.re[rt]
  
  def subi(self, rd, rs, entero):
    self.re[rd] = self.re[rs] - entero
  
  def mult(self, rd, rs, rt):
    self.re[rd] = self.re[rs] * self.re[rt]

  def multi(self, rd, rs, entero):
    self.re[rd] = self.re[rs] * entero

  def div(self, rd, rs, rt):
    try:
      self.re[rd] = self.re[rs] / self.re[rt]
    except ZeroDivisionError:
      raise errores.DivZeroError

  def divi(self, rd, rs, entero):
    try:
      self.re[rd] = self.re[rs] / entero
    except ZeroDivisionError:
      raise errores.DivZeroError

  def mod(self, rd, rs, rt):
    try:
      self.re[rd] = self.re[rs] % self.re[rt]
    except ZeroDivisionError:
      raise errores.ModZeroError

  def modi(self, rd, rs, entero):
    try:
      self.re[rd] = self.re[rs] % entero
    except ZeroDivisionError:
      raise errores.ModZeroError
  
  def xnot(self, rd, rs):
    if self.re[rs] == 0:
      self.re[rd] = 1
    else:
      self.re[rd] = 0

  def la(self, rd, et):
    self.re[rd] = self.etiq[et]
  
  def lw(self, rd, desp, rs):
    dir = self.re[rs] + desp
    self.re[rd] = self.mem.getEntero(dir)

  def sw(self, rd, desp, rs):
    dir = self.re[rs] + desp
    self.mem[dir] = self.re[rd]

  def save(self, rd, desp, rs):
    dir = self.re[rs] + desp
    try:
      self.mem[dir] = self.re[rd]
    except errores.RegVacioError:
      pass

  def rest(self, rd, desp, rs):
    dir = self.re[rs] + desp
    try:
      self.re[rd] = self.mem.getEntero(dir)
    except errores.MemAccesoError:
      pass
  
  def beq(self, rd, rs, et):
    if self.re[rd] == self.re[rs]:
      self.pc = self.etiq[et]

  def bne(self, rd, rs, et):
    if self.re[rd] != self.re[rs]:
      self.pc = self.etiq[et]

  def bge(self, rd, rs, et):
    if self.re[rd] >= self.re[rs]:
      self.pc = self.etiq[et]
  
  def bgt(self, rd, rs, et):
    if self.re[rd] > self.re[rs]:
      self.pc = self.etiq[et]
      
  def ble(self, rd, rs, et):
    if self.re[rd] <= self.re[rs]:
      self.pc = self.etiq[et]
      
  def blt(self, rd, rs, et):
    if self.re[rd] < self.re[rs]:
      self.pc = self.etiq[et]

  def j(self, et):
    self.pc = self.etiq[et]

  def jal(self, et):
    self.sigsub.append(self.pc)
    self.re["$ra"] = self.pc
    self.pc = self.etiq[et]

  def jr(self, rd):
    dir = self.re[rd]
    if dir not in self.sigsub and dir not in self.etiq.values():
      raise errores.JDestError, dir
    else:
      self.pc = dir

  def jalr(self, rd):
    self.sigsub.append(self.pc)
    self.re["$ra"] = self.pc
    self.pc = self.re[rd]

  def fadd(self, rd, rs, rt):
    self.rr[rd] = self.rr[rs] + self.rr[rt]
  
  def faddi(self, rd, rs, real):
    self.rr[rd] = self.rr[rs] + real
  
  def fsub(self, rd, rs, rt):
    self.rr[rd] = self.rr[rs] - self.rr[rt]
  
  def fsubi(self, rd, rs, real):
    self.rr[rd] = self.rr[rs] - real
  
  def fmult(self, rd, rs, rt):
    self.rr[rd] = self.rr[rs] * self.rr[rt]

  def fmulti(self, rd, rs, real):
    self.rr[rd] = self.rr[rs] * real

  def fdiv(self, rd, rs, rt):
    try:
      self.rr[rd] = self.rr[rs] / self.rr[rt]
    except ZeroDivisionError:
      raise errores.DivZeroError

  def fdivi(self, rd, rs, real):
    try:
      self.rr[rd] = self.rr[rs] / real
    except ZeroDivisonError:
      raise errores.DivZeroError

  def flw(self, rd, desp, rs):
    dir = self.re[rs] + desp
    self.rr[rd] = self.mem.getReal(dir)

  def fsw(self, rd, desp, rs):
    dir = self.re[rs] + desp
    self.mem[dir] = self.rr[rd]
 
  def fsave(self, rd, desp, rs):
    dir = self.re[rs] + desp
    try:
      self.mem[dir] = self.rr[rd]
    except errores.RegVacioError:
      pass

  def frest(self, rd, desp, rs):
    dir = self.re[rs] + desp
    try:
      self.rr[rd] = self.mem.getReal(dir)
    except errores.MemAccesoError:
      pass

  def fbeq(self, rd, rs, et):
    if self.rr[rd] == self.rr[rs]:
      self.pc = self.etiq[et]

  def fbne(self, rd, rs, et):
    if self.rr[rd] != self.rr[rs]:
      self.pc = self.etiq[et]

  def fbge(self, rd, rs, et):
    if self.rr[rd] >= self.rr[rs]:
      self.pc = self.etiq[et]
  
  def fbgt(self, rd, rs, et):
    if self.rr[rd] > self.rr[rs]:
      self.pc = self.etiq[et]
      
  def fble(self, rd, rs, et):
    if self.rr[rd] <= self.rr[rs]:
      self.pc = self.etiq[et]
      
  def fblt(self, rd, rs, et):
    if self.rr[rd] < self.rr[rs]:
      self.pc = self.etiq[et]

  def syscall(self):
    if self.re["$sc"] == None:
      raise errores.SysNoCodError
    else:
      cod = self.re["$sc"]
    if cod == 0:   # Imprimir entero: entero en $a0
      if not self.salida:
        sys.stdout.write(str(self.re["$a0"]))
      else:
        self.salida(str(self.re["$a0"]))
    elif cod == 1: # Imprimir real: real en $fa
      if not self.salida:
        sys.stdout.write(str(self.rr["$fa"]))
      else:
        self.salida(str(self.rr["$fa"]))
    elif cod == 2: # Imprimir cadena: dir cadena en $a0
      try:
        dir = self.re["$a0"]
        v = chr(self.mem.getEntero(dir))
        while v != "\0":	# "\0" es el carácter cuyo ascii es 0
          if not self.salida:
            sys.stdout.write(v)
	  else:
	    self.salida(v)
	  dir += 1
	  v = chr(self.mem.getEntero(dir))
      except ValueError:
        raise errores.SysCharError, self.mem.getEntero(dir)
    elif cod == 3: # Leer entero: entero en $a0
      if not self.entrada:
        ent = raw_input()
      else:
        ent = self.entrada()
      try:
        self.re["$a0"] = long(ent)
      except ValueError:
	raise errores.SysEnteroError, ent
    elif cod == 4: # Leer real: real en $fa
      if not self.entrada:
        real = raw_input()
      else:
        real = self.entrada()
      try:
        self.rr["$fa"] = float(real)
      except ValueError:
        raise errores.SysRealError, real
    elif cod == 5: # Leer cadena: dir en $a0, long a leer en $a1
      dir = self.re["$a0"]
      longitud = self.re["$a1"]
      if not self.entrada:
        cad = raw_input()
      else:
        cad = self.entrada()
      if longitud > len(cad):
        long_cad = len(cad)
      else:
        long_cad = longitud
      for i in range(long_cad):
	self.mem[dir+i] = ord(cad[i])
      self.mem[dir+long_cad] = 0 # todas las cadenas finalizan con 0
    elif cod == 6: # exit
      self.estado = Rossi.PARADO
    else:
      raise errores.SysCodError, cod

  def toint(self, rd, rs):
    self.re[rd] = long(self.rr[rs])

  def tofloat(self, rd, rs):
    self.rr[rd] = float(self.re[rs])

  def asciiz(self, pos, lit):
    cad = ""		# Cadena con los caracteres de escape interpretados
    i = 0
    while i < len(lit):
      if lit[i] <> "\\":
        cad += lit[i]	# Si no es una secuencia de escape, se añade sin más
      else:
        # Estamos ante una secuencia de escape
	# Miramos el siguiente carácter y averiguamos de cuál se trata
	i += 1
	if lit[i] == "n":
	  cad += "\n"
	elif lit[i] == "t":
	  cad += "\t"
	elif lit[i] == "\"":
	  cad += "\""
	elif lit[i] == "\\":
	  cad += "\\"
      i += 1
    long_cad = len(cad)
    if not pos:	# No se ha especificado la posición
      pos = self.mem.ultDir + 1
    for i in range(long_cad):
      self.mem[pos+i] = ord(cad[i])
    self.mem[pos+long_cad] = 0	# Finalizamos la cadena con el carácter \0
    self.ASCIIZ = 1
    self.ASCIIZ_POS = pos
  
  def nop(self, directiva=None):
    self.NOP = 1

  ########################################
  # Handlers de los errores de ejecución #
  ########################################
  
  def hSysNoCodError(self):
    self.error_msg = errores.SysNoCodErrorMsg
    self.estado = Rossi.ERROR
    self.pc -= 1	# Si se produce una excepción, no avanza el PC

  def hSysCodError(self, cod):
    self.error_msg = errores.SysCodErrorMsg % cod
    self.estado = Rossi.ERROR
    self.pc -= 1

  def hSysEnteroError(self, valor):
    self.error_msg = errores.SysEnteroErrorMsg % valor
    self.estado = Rossi.ERROR
    self.pc -= 1

  def hSysRealError(self, valor):
    self.error_msg = errores.SysRealErrorMsg % valor
    self.estado = Rossi.ERROR
    self.pc -= 1

  def hSysCharError(self, valor):
    self.error_msg = errores.SysCharErrorMsg % valor
    self.estado = Rossi.ERROR
    self.pc -= 1
  
  def hRegVacioError(self, reg):
    self.error_msg = errores.RegVacioErrorMsg % reg
    self.estado = Rossi.ERROR
    self.pc -= 1

  def hMemEnteroError(self, d):
    self.error_msg = errores.MemEnteroErrorMsg % d
    self.estado = Rossi.ERROR
    self.pc -= 1

  def hMemRealError(self, d):
    self.error_msg = errores.MemRealErrorMsg % d
    self.estado = Rossi.ERROR
    self.pc -= 1

  def hMemAccesoError(self, d):
    self.error_msg = errores.MemAccesoErrorMsg % d
    self.estado = Rossi.ERROR
    self.pc -= 1

  def hMemDirNegError(self, d):
    self.error_msg = errores.MemDirNegErrorMsg % d
    self.estado = Rossi.ERROR
    self.pc -= 1

  def hDivZeroError(self):
    self.error_msg = errores.DivZeroErrorMsg
    self.estado = Rossi.ERROR
    self.pc -= 1

  def hModZeroError(self):
    self.error_msg = errores.ModZeroErrorMsg
    self.estado = Rossi.ERROR
    self.pc -= 1

  def hJDestError(self, dir):
    self.error_msg = errores.JDestErrorMsg % dir
    self.estado = Rossi.ERROR
    self.pc -= 1
  
  def hPCRangoError(self):
    self.error_msg = "PC fuera de rango." 
    self.estado = Rossi.ERROR
    self.pc -= 1
