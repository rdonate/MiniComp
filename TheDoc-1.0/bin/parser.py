# -*- coding: utf-8 -*-

import re

# Patrones: todos los grupos son anónimos !!!
p_rege = "\$(?:zero|sp|fp|ra|sc|a0|a1|r[0-9]|r[1-9][0-9]*)"	# Registro entero
p_regr = "\$(?:fa|fzero|f(?:[0-9]|[1-9][0-9]*))"		# Registro real
p_ent = "[+-]?[0-9]+"						# Número entero
p_real = "[+-]?[0-9]+\\.[0-9]+(?:[eE][+-]?[0-9]+)?"		# Número real
p_arg = "[-+)($a-zE0-9.]+"					# Cualquier posible argumento

# Expresiones regulares: se marcan los grupos que interesan
txt = re.compile(r"[ \t]*\.text[ \t]*(?:#.*)?$")
dat = re.compile(r"[ \t]*\.data[ \t]*(?:#.*)?$")

# g1: posición; g2: cadena
asc = re.compile(r"[ \t]*\.asciiz(?:[ \t]+([0-9]+))?" + \
                 r"(?:[ \t]+\"((?:[^\"\t\n\\]|\\[\"tn\\])*)\")" + \
		 r"[ \t]*(?:#.*)?$")

# et? (ins (a1 (,a2 (,a3)? )? )? )? com?
# g1: etiqueta; g2: instrucción; g3: arg1; g4: arg2; g5: arg3
ins = re.compile(r"[ \t]*(?:([a-zA-Z][a-zA-Z0-9]*):[ \t]*)?" + \
                 r"(?:([a-z]+)" + \
		 r"(?:[ \t]*("+p_arg+")" + \
		 r"(?:[ \t]*,[ \t]*("+p_arg+")" + \
		 r"(?:[ \t]*,[ \t]*("+p_arg+"))?)?)?)?" + \
		 r"[ \t]*(?:#.*)?$")

et = re.compile("([a-zA-Z][a-zA-Z0-9]*)$")
rege = re.compile("("+p_rege+")$")
regr = re.compile("("+p_regr+")$")
ent = re.compile("("+p_ent+")$")
real = re.compile("("+p_real+")$")

# g1: desplazamiento; g2: registro entero
ind = re.compile("("+p_ent+")\(("+p_rege+")\)$")

class Parser:
  def __init__(self, maquina, codigo):
    self.m = maquina
    self.c = codigo
  	  
  def parsea(self):
    nl, dentroData, dentroText, hayAsciiz, hayInstr = 0, 0, 0, 0, 0
    for linea in self.c:
      mo_data = dat.match(linea)
      if mo_data:
        if dentroText:
	  self.m.err.dataDespuesText(nl)
	elif dentroData:
	  self.m.err.dataRep(nl)
	else:
	  dentroData = 1
          self.m.anyadeInstruccion((self.m.nop,()))
      else:
        mo_text = txt.match(linea)
	if mo_text:
	  if dentroText:
	    self.m.err.textRep(nl)
	  elif dentroData and not hayAsciiz:
	    dentroText = 1
	    self.m.err.dataSinAsciiz(nl)
	  else:
	    dentroText = 1; dentroData = 0
	    self.m.anyadeInstruccion((self.m.nop,()))
	else:
	  mo_ascii = asc.match(linea)
	  if mo_ascii:
	    if not dentroData:
	      self.m.err.asciizError(nl)
	    else:
	      hayAsciiz = 1
	      pos = mo_ascii.group(1)
	      if pos:
		try:
		  pos = int(pos)
		except ValueError:
	          pos = long(pos)
	      cad = mo_ascii.group(2)
	      self.m.anyadeInstruccion((self.m.asciiz, (pos, cad)))
	  else:
	    mo_instr = ins.match(linea)
	    if mo_instr:
	      if not dentroText and (mo_instr.group(1) or mo_instr.group(2)):
	        self.m.err.instrAntesText(nl)
	      if mo_instr.group(1): # Def. etiqueta
		self.m.declaraEtiqueta(mo_instr.group(1), nl)
	      if mo_instr.group(2): # Instrucción
		hayInstr = 1
	        codop = mo_instr.group(2)
		if not self.m.instrucciones.has_key(codop):
		  self.m.err.instrError(nl)
		else:
		  instruccion = self.m.instrucciones[codop][0]
		  formato = self.m.instrucciones[codop][1] # Tupla con el formato de sus argumentos
		  nargs = len(formato)
		  if nargs == 0:
		    if mo_instr.group(3) == None:
		      self.m.anyadeInstruccion((instruccion, ()))
                    else:
		      self.m.err.numArgsError(nl)
		  elif nargs == 1:
		    if mo_instr.group(3) == None or mo_instr.group(4) != None:
		      self.m.err.numArgsError(nl)
		    else:
		      if formato[0] == "e":
		        mo_arg1 = et.match(mo_instr.group(3))
		      else: # es un registro entero
		        mo_arg1 = rege.match(mo_instr.group(3))
		      if mo_arg1:
			arg1 = mo_arg1.group(1)
			self.m.anyadeInstruccion((instruccion, (arg1,)))
			if formato[0] == "e": # Añadimos la referencia de la etiqueta a refet
			  if not self.m.refet.has_key(arg1):
			    self.m.refet[arg1] = [nl]
			  else:
			    self.m.refet[arg1].append(nl)
		      else: # el argumento no ha hecho matching con los tipos que acepta
			self.m.err.formatoArgsError(nl, codop, 0, formato[0])
		  elif nargs == 2:
		    if mo_instr.group(4) == None or mo_instr.group(5) != None:
		      self.m.err.numArgsError(nl)
		    else:
		      # El primer argumento siempre es un registro: entero o real
		      if formato[0] == "r":
		        mo_arg1 = rege.match(mo_instr.group(3))
		      elif formato[0] == "f":
		        mo_arg1 = regr.match(mo_instr.group(3))
		      if not mo_arg1:
			self.m.err.formatoArgsError(nl, codop, 1, formato[0])
		      else:
		        arg1 = mo_arg1.group(1)
			# Intento hacer matching con el formato del segundo argumento
			if formato[1] == "r":
			  mo_arg2 = rege.match(mo_instr.group(4))
			elif formato[1] == "f":
			  mo_arg2 = regr.match(mo_instr.group(4))
			elif formato[1] == "R":
			  mo_arg2 = ent.match(mo_instr.group(4))
			elif formato[1] == "F":
			  mo_arg2 = real.match(mo_instr.group(4))
			elif formato[1] == "e":
			  mo_arg2 = et.match(mo_instr.group(4))
			elif formato[1] == "n":
			  mo_arg2 = ind.match(mo_instr.group(4))
			if not mo_arg2:
			  self.m.err.formatoArgsError(nl, codop, 2, formato[1])
			# Si he hecho matching...
                        elif formato[1] == "R": # Convertir el string a entero
			  arg2 = long(mo_arg2.group(1))
			  self.m.anyadeInstruccion((instruccion, (arg1, arg2)))
			elif formato[1] == "F": # Convertir el string a real
			  arg2 = float(mo_arg2.group(1))
			  self.m.anyadeInstruccion((instruccion, (arg1, arg2)))
			elif formato[1] == "n": # Obtener el registro y el desplazamiento
			  r = mo_arg2.group(2)
			  desp = long(mo_arg2.group(1))
			  self.m.anyadeInstruccion((instruccion, (arg1, desp, r)))
			else:
			  arg2 = mo_arg2.group(1)
			  self.m.anyadeInstruccion((instruccion, (arg1, arg2)))
			  if formato[1] == "e": # Referencia en refet
			    if not self.m.refet.has_key(arg2):
			      self.m.refet[arg2] = [nl]
			    else:
			      self.m.refet[arg2].append(nl)
		  else: # 3 argumentos
                    if mo_instr.group(5) == None:
		      self.m.err.numArgsError(nl)
	            else: # Tiene 3 argumentos
		      # Los dos primeros args tienen que ser registros: reales o enteros
		      if formato[0] == "r":
		        mo_arg1 = rege.match(mo_instr.group(3))
		      elif formato[0] == "f":
		        mo_arg1 = regr.match(mo_instr.group(3))
		      if not mo_arg1:
		        self.m.err.formatoArgsError(nl, codop, 1, formato[0])
		      else:
			if formato[1] == "r":
		          mo_arg2 = rege.match(mo_instr.group(4))
			elif formato[1] == "f":
			  mo_arg2 = regr.match(mo_instr.group(4))
			if not mo_arg2:
			  self.m.err.formatoArgsError(nl, codop, 2, formato[1])
			else:
			  arg1 = mo_arg1.group(1)
			  arg2 = mo_arg2.group(1)
                          # El tercer argumento será un registro (entero o real), un inmediato
			  # (entero o real) o una etiqueta
			  if formato[2] == "r":
			    mo_arg3 = rege.match(mo_instr.group(5))
			  elif formato[2] == "f":
			    mo_arg3 = regr.match(mo_instr.group(5))
			  elif formato[2] == "R":
			    mo_arg3 = ent.match(mo_instr.group(5))
			  elif formato[2] == "F":
			    mo_arg3 = real.match(mo_instr.group(5))
			  elif formato[2] == "e":
			    mo_arg3 = et.match(mo_instr.group(5))
			  if not mo_arg3:
			    self.m.err.formatoArgsError(nl, codop, 3, formato[2])
                          elif formato[2] == "R": # Convertir el string a entero
			    arg3 = long(mo_arg3.group(1))
			    self.m.anyadeInstruccion((instruccion, (arg1, arg2, arg3)))
			  elif formato[2] == "F": # Convertir el string a real
			    arg3 = float(mo_arg3.group(1))
			    self.m.anyadeInstruccion((instruccion, (arg1, arg2, arg3)))
			  else:
			    arg3 = mo_arg3.group(1)
			    if formato[2] == "e": # Añadimos la referencia a refet
			      if not self.m.refet.has_key(arg3):
			        self.m.refet[arg3] = [nl]
			      else:
			        self.m.refet[arg3].append(nl)
			    self.m.anyadeInstruccion((instruccion, (arg1, arg2, arg3)))
	      # Si se trata de una línea en blanco, de un comentario, o de la definición
	      # de una etiqueta que no va seguida de ninguna instrucción
	      if not mo_instr.group(2):
	        self.m.anyadeInstruccion((self.m.nop,()))
	    else: # La línea no hace matching
              self.m.err.lineaError(nl)
      nl += 1 # Fin del for
    # Si no aparece .text o no hay ninguna instrucción
    if not dentroText or dentroText and not hayInstr:
      self.m.err.finError(nl)
