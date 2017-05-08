# -*- coding: utf-8 -*- (excepciones)

# Representa los errores que surgen durante el análisis; no los errores
# en tiempo de ejecución
class Errores:
  def __init__(self):
    self.inicializa()

  def inicializa(self):
    self.e = []

  def dataRep(self, nl):
    self.e.append("Error línea %4d: sólo puede aparecer una directiva '.data'." % nl)

  def dataDespuesText(self, nl):
    self.e.append("Error línea %4d: la directiva '.data' debe aparecer antes de la directiva '.text'." % nl)

  def dataSinAsciiz(self, nl):
    self.e.append("Error línea %4d: la zona de definición de datos está vacía." % nl)

  def textRep(self, nl):
    self.e.append("Error línea %4d: sólo puede aparecer una directiva '.text'." % nl)

  def asciizError(self, nl):
    self.e.append("Error línea %4d: la directiva '.asciiz' sólo puede aparecer en la zona de definición de datos." % nl)

  def instrAntesText(self, nl):
    self.e.append("Error línea %4d: instrucción antes de la directiva '.text'." % nl)

  def finError(self, nl):
    self.e.append("Error línea %4d: fin de fichero inesperado." % nl)
    
  def instrError(self, nl):
    self.e.append("Error línea %4d: instrucción no válida." % nl)

  def lineaError(self, nl):
    self.e.append("Error línea %4d: línea incorrecta." % nl)

  def numArgsError(self, nl):
    self.e.append("Error línea %4d: número de campos incorrecto." % nl)

  def formatoArgsError(self, nl, ins, arg, tipo):
    self.e.append("Error línea %4d: El %sargumento de la instrucción '%s' debe ser %s." % \
                   (nl, argumentos[arg], ins, tipos[tipo]))

  def etiqNoDefError(self, et, nl):
    self.e.append("Error línea %4d: etiqueta '%s' no definida." % (nl,et))

  def etiqRedefError(self, et, nl):
    self.e.append("Error línea %4d: etiqueta '%s' redefinida." % (nl, et))

# Los siguientes diccionarios ayudan a emitir los mensajes de error

argumentos = { 0: "",
               1: "primer ",
	       2: "segundo ",
	       3: "tercer "
	     }

tipos = { "r": "un registro entero",
          "f": "un registro real",
	  "R": "un inmediato entero",
	  "F": "un inmediato real",
	  "e": "una etiqueta",
	  "n": "un indirecto a registro"
	}

################################################
# Errores en tiempo de ejecución (EXCEPCIONES) #
################################################

class SysNoCodError(Exception):
  pass
SysNoCodErrorMsg = "El registro $sc no contiene el código de la llamada al sistema."

class SysCodError(Exception):
  pass
SysCodErrorMsg = "Código de llamada al sistema no válido (%d)."

class SysCharError(Exception):
  pass
SysCharErrorMsg = "Carácter no válido (%d)."

class SysEnteroError(Exception):
  pass
SysEnteroErrorMsg = "El valor introducido no es un entero válido (%s)"

class SysRealError(Exception):
  pass
SysRealErrorMsg = "El valor introducido no es un real válido (%s)."

class RegVacioError(Exception):
  pass
RegVacioErrorMsg = "El registro %s no contiene ningún valor."

class MemEnteroError(Exception):
  pass
MemEnteroErrorMsg = "La posición de memoria %d no contiene un entero."

class MemRealError(Exception):
  pass
MemRealErrorMsg = "La posición de memoria %d no contiene un real."

class MemAccesoError(Exception):
  pass
MemAccesoErrorMsg = "La posición de memoria %d no está inicializada."

class MemDirNegError(Exception):
  pass
MemDirNegErrorMsg = "Acceso a una posición de memoria negativa (%d)"

class DivZeroError(Exception):
  pass
DivZeroErrorMsg = "División por cero."

class ModZeroError(Exception):
  pass
ModZeroErrorMsg = "Módulo con divisor cero."

class JDestError(Exception):
  pass
JDestErrorMsg = "El destino del salto (línea %d) no es la instrucción posterior\n" + \
             "a ninguna instrucción jal ni jalr, ni está etiquetado."
