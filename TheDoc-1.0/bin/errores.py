# -*- coding: latin1 -*- (excepciones)

# Representa los errores que surgen durante el an�lisis; no los errores
# en tiempo de ejecuci�n
class Errores:
  def __init__(self):
    self.inicializa()

  def inicializa(self):
    self.e = []

  def dataRep(self, nl):
    self.e.append("Error l�nea %4d: s�lo puede aparecer una directiva '.data'." % nl)

  def dataDespuesText(self, nl):
    self.e.append("Error l�nea %4d: la directiva '.data' debe aparecer antes de la directiva '.text'." % nl)

  def dataSinAsciiz(self, nl):
    self.e.append("Error l�nea %4d: la zona de definici�n de datos est� vac�a." % nl)

  def textRep(self, nl):
    self.e.append("Error l�nea %4d: s�lo puede aparecer una directiva '.text'." % nl)

  def asciizError(self, nl):
    self.e.append("Error l�nea %4d: la directiva '.asciiz' s�lo puede aparecer en la zona de definici�n de datos." % nl)

  def instrAntesText(self, nl):
    self.e.append("Error l�nea %4d: instrucci�n antes de la directiva '.text'." % nl)

  def finError(self, nl):
    self.e.append("Error l�nea %4d: fin de fichero inesperado." % nl)
    
  def instrError(self, nl):
    self.e.append("Error l�nea %4d: instrucci�n no v�lida." % nl)

  def lineaError(self, nl):
    self.e.append("Error l�nea %4d: l�nea incorrecta." % nl)

  def numArgsError(self, nl):
    self.e.append("Error l�nea %4d: n�mero de campos incorrecto." % nl)

  def formatoArgsError(self, nl, ins, arg, tipo):
    self.e.append("Error l�nea %4d: El %sargumento de la instrucci�n '%s' debe ser %s." % \
                   (nl, argumentos[arg], ins, tipos[tipo]))

  def etiqNoDefError(self, et, nl):
    self.e.append("Error l�nea %4d: etiqueta '%s' no definida." % (nl,et))

  def etiqRedefError(self, et, nl):
    self.e.append("Error l�nea %4d: etiqueta '%s' redefinida." % (nl, et))

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
# Errores en tiempo de ejecuci�n (EXCEPCIONES) #
################################################

class SysNoCodError(Exception):
  pass
SysNoCodErrorMsg = "El registro $sc no contiene el c�digo de la llamada al sistema."

class SysCodError(Exception):
  pass
SysCodErrorMsg = "C�digo de llamada al sistema no v�lido (%d)."

class SysCharError(Exception):
  pass
SysCharErrorMsg = "Car�cter no v�lido (%d)."

class SysEnteroError(Exception):
  pass
SysEnteroErrorMsg = "El valor introducido no es un entero v�lido (%s)"

class SysRealError(Exception):
  pass
SysRealErrorMsg = "El valor introducido no es un real v�lido (%s)."

class RegVacioError(Exception):
  pass
RegVacioErrorMsg = "El registro %s no contiene ning�n valor."

class MemEnteroError(Exception):
  pass
MemEnteroErrorMsg = "La posici�n de memoria %d no contiene un entero."

class MemRealError(Exception):
  pass
MemRealErrorMsg = "La posici�n de memoria %d no contiene un real."

class MemAccesoError(Exception):
  pass
MemAccesoErrorMsg = "La posici�n de memoria %d no est� inicializada."

class MemDirNegError(Exception):
  pass
MemDirNegErrorMsg = "Acceso a una posici�n de memoria negativa (%d)"

class DivZeroError(Exception):
  pass
DivZeroErrorMsg = "Divisi�n por cero."

class ModZeroError(Exception):
  pass
ModZeroErrorMsg = "M�dulo con divisor cero."

class JDestError(Exception):
  pass
JDestErrorMsg = "El destino del salto (l�nea %d) no es la instrucci�n posterior\n" + \
             "a ninguna instrucci�n jal ni jalr, ni est� etiquetado."
