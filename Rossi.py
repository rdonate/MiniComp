# -*- coding: utf-8 -*-

class Operando:
  def __init__(self):
    pass

class Inmediato(Operando):
  def __init__(self,v):
    self.v= v

  def __str__(self):
    return `self.v`

class RegEntero(Operando):
  def __init__(self,r):
    if type(r)== type(1):
      self.r="$r%d" % r
    else:
      self.r="$%s" % r

  def __str__(self):
    return self.r

class RegFlotante(Operando):
  def __init__(self,r):
    if type(r)== type(1):
      self.r="$f%d" % r
    else:
      self.r="$%s" % r

  def __str__(self):
    return self.r

class Ind(Operando):
  def __init__(self,desp,reg):
    r=str(RegEntero(reg))
    self.r= "%d(%s)" % (desp, r)

  def __str__(self):
    return self.r

class Et(Operando):
  def __init__(self,e):
    self.e=e

  def __str__(self):
    return "%s" % self.e

class ROSSI:
  def __init__(self,cod,op1,op2,op3,et,coment):
    self.cod= cod
    self.op1= op1
    self.op2= op2
    self.op3= op3
    self.et= et
    self.coment= coment

  def __str__(self):
    if self.et:
      s="%s:" % self.et
    else:
      s=""
    if self.cod:
      s=s+"\t"+self.cod
      if self.op1:
        s=s+" %s" % self.op1
      if self.op2:
        s=s+", %s" % self.op2
      if self.op3:
        s=s+", %s" % self.op3
    if self.coment:
      if s:
        s= s+"\t# %s" % self.coment
      else:
        s= "# %s" % self.coment
    return s

def Comentario(cadena):
  return ROSSI(None,None,None,None,None,cadena)

def Etiqueta(et, coment=None):
  return ROSSI(None,None,None,None,et,coment)

# Directivas
class Directiva:
  def __init__(self, dir, coment= None):
    self.dir= dir
    self.coment= coment

  def __str__(self):
    s= self.dir
    if self.coment!= None:
      s+= "\t# %s" % self.coment
    return s

# Cadenas:
class asciiz:
  escape= { "\\": "\\\\", "\n": "\\n", "\t": "\\t" }
  def __init__(self, cad, dir= None):
    self.cad= cad
    self.dir= dir

  def __str__(self):
    r= '"%s"' % "".join([asciiz.escape.get(c, c) for c in self.cad])
    if self.dir== None:
      return ".asciiz %s" % r
    else:
      return ".asciiz %d %s" % (self.dir, r)

# Aritmetica entera:

def add(rd, rs, rt, coment=None,et=None):
  return ROSSI("add", RegEntero(rd), RegEntero(rs), RegEntero(rt), et, coment)

def addi(rd, rs, v, coment=None,et=None):
  return ROSSI("addi", RegEntero(rd), RegEntero(rs), Inmediato(v), et, coment)

def sub(rd, rs, rt, coment=None,et=None):
  return ROSSI("sub", RegEntero(rd), RegEntero(rs), RegEntero(rt), et, coment)

def subi(rd, rs, v, coment=None,et=None):
  return ROSSI("subi", RegEntero(rd), RegEntero(rs), Inmediato(v), et, coment)

def mult(rd, rs, rt, coment=None,et=None):
  return ROSSI("mult", RegEntero(rd), RegEntero(rs), RegEntero(rt), et, coment)

def multi(rd, rs, v, coment=None,et=None):
  return ROSSI("multi", RegEntero(rd), RegEntero(rs), Inmediato(v), et, coment)

def div(rd, rs, rt, coment=None,et=None):
  return ROSSI("div", RegEntero(rd), RegEntero(rs), RegEntero(rt), et, coment)

def divi(rd, rs, v, coment=None,et=None):
  return ROSSI("divi", RegEntero(rd), RegEntero(rs), Inmediato(v), et, coment)

def mod(rd, rs, rt, coment=None,et=None):
  return ROSSI("mod", RegEntero(rd), RegEntero(rs), RegEntero(rt), et, coment)

def modi(rd, rs, v, coment=None,et=None):
  return ROSSI("modi", RegEntero(rd), RegEntero(rs), Inmediato(v), et, coment)

def nnot(rd, rs, coment=None,et=None):
  return ROSSI("not", RegEntero(rd), RegEntero(rs), None, et, coment)

# Aritmetica real:

def fadd(rd, rs, rt, coment=None,et=None):
  return ROSSI("fadd", RegFlotante(rd), RegFlotante(rs), RegFlotante(rt), et, coment)

def faddi(rd, rs, v, coment=None,et=None):
  return ROSSI("faddi", RegFlotante(rd), RegFlotante(rs), Inmediato(v), et, coment)

def fsub(rd, rs, rt, coment=None,et=None):
  return ROSSI("fsub", RegFlotante(rd), RegFlotante(rs), RegFlotante(rt), et, coment)

def fsubi(rd, rs, v, coment=None,et=None):
  return ROSSI("fsubi", RegFlotante(rd), RegFlotante(rs), Inmediato(v), et, coment)

def fmult(rd, rs, rt, coment=None,et=None):
  return ROSSI("fmult", RegFlotante(rd), RegFlotante(rs), RegFlotante(rt), et, coment)

def fmulti(rd, rs, v, coment=None,et=None):
  return ROSSI("fmulti", RegFlotante(rd), RegFlotante(rs), Inmediato(v), et, coment)

def fdiv(rd, rs, rt, coment=None,et=None):
  return ROSSI("fdiv", RegFlotante(rd), RegFlotante(rs), RegFlotante(rt), et, coment)

def fdivi(rd, rs, v, coment=None,et=None):
  return ROSSI("fdivi", RegFlotante(rd), RegFlotante(rs), Inmediato(v), et, coment)

# Carga y almacenamiento entero:

def la(rd, etiq, coment=None, et=None):
  return ROSSI("la", RegEntero(rd), Et(etiq), None, et, coment)

def sw(rd, desp, reg, coment=None, et=None):
  return ROSSI("sw", RegEntero(rd), Ind(desp,reg), None, et, coment)

def save(rd, desp, reg, coment=None, et=None):
  return ROSSI("save", RegEntero(rd), Ind(desp,reg), None, et, coment)

def lw(rd, desp, reg, coment=None, et=None):
  return ROSSI("lw", RegEntero(rd), Ind(desp,reg), None, et, coment)

def rest(rd, desp, reg, coment=None, et=None):
  return ROSSI("rest", RegEntero(rd), Ind(desp,reg), None, et, coment)

# Carga y almacenamiento real:

def fsw(rd, desp, reg, coment=None, et=None):
  return ROSSI("fsw", RegFlotante(rd), Ind(desp,reg), None, et, coment)

def fsave(rd, desp, reg, coment=None, et=None):
  return ROSSI("fsave", RegFlotante(rd), Ind(desp,reg), None, et, coment)

def flw(rd, desp, reg, coment=None, et=None):
  return ROSSI("flw", RegFlotante(rd), Ind(desp,reg), None, et, coment)

def frest(rd, desp, reg, coment=None, et=None):
  return ROSSI("frest", RegFlotante(rd), Ind(desp,reg), None, et, coment)

# Salto condicional entero:

def beq(rd, rs, etiq, coment=None,et=None):
  return ROSSI("beq", RegEntero(rd), RegEntero(rs), Et(etiq), et, coment)

def bne(rd, rs, etiq, coment=None,et=None):
  return ROSSI("bne", RegEntero(rd), RegEntero(rs), Et(etiq), et, coment)

def bge(rd, rs, etiq, coment=None,et=None):
  return ROSSI("bge", RegEntero(rd), RegEntero(rs), Et(etiq), et, coment)

def bgt(rd, rs, etiq, coment=None,et=None):
  return ROSSI("bgt", RegEntero(rd), RegEntero(rs), Et(etiq), et, coment)

def ble(rd, rs, etiq, coment=None,et=None):
  return ROSSI("ble", RegEntero(rd), RegEntero(rs), Et(etiq), et, coment)

def blt(rd, rs, etiq, coment=None,et=None):
  return ROSSI("blt", RegEntero(rd), RegEntero(rs), Et(etiq), et, coment)

# Salto condicional real:

def fbeq(rd, rs, etiq, coment=None,et=None):
  return ROSSI("fbeq", RegFlotante(rd), RegFlotante(rs), Et(etiq), et, coment)

def fbne(rd, rs, etiq, coment=None,et=None):
  return ROSSI("fbne", RegFlotante(rd), RegFlotante(rs), Et(etiq), et, coment)

def fbge(rd, rs, etiq, coment=None,et=None):
  return ROSSI("fbge", RegFlotante(rd), RegFlotante(rs), Et(etiq), et, coment)

def fbgt(rd, rs, etiq, coment=None,et=None):
  return ROSSI("fbgt", RegFlotante(rd), RegFlotante(rs), Et(etiq), et, coment)

def fble(rd, rs, etiq, coment=None,et=None):
  return ROSSI("fble", RegFlotante(rd), RegFlotante(rs), Et(etiq), et, coment)

def fblt(rd, rs, etiq, coment=None,et=None):
  return ROSSI("fblt", RegFlotante(rd), RegFlotante(rs), Et(etiq), et, coment)

# Salto incondicional:

def j(etiq, coment=None,et=None):
  return ROSSI("j", Et(etiq), None, None, et, coment)

def jal(etiq, coment=None,et=None):
  return ROSSI("jal", Et(etiq), None, None, et, coment)

def jr(rd, coment=None,et=None):
  return ROSSI("jr", RegEntero(rd), None, None, et, coment)

# Conversiones:

def toint(rd, rs, coment=None,et=None):
  return ROSSI("toint", RegEntero(rd), RegFlotante(rs), None, et, coment)

def tofloat(rd, rs, coment=None,et=None):
  return ROSSI("tofloat", RegFlotante(rd), RegEntero(rs), None, et, coment)

# Llamada al sistema:

def syscall(coment=None,et=None):
  return ROSSI("syscall", None, None, None, et, coment)
