# -*- coding: latin1 -*-

from Tkinter import *
import Pmw
from FileDialog import *
from Rossi import *
from string import expandtabs
import types

# Interfaz del emulador en modo gráfico

release = "1.0"

class Menu:
  def __init__(self, parent):
    self.wgt = Pmw.MenuBar(parent, hull_relief=RAISED, hull_borderwidth=1, hotkeys=1)
    self.wgt.pack(fill=X, side=TOP)
    self.wgt.addmenu("File", None, side=LEFT)
    self.wgt.addmenuitem("File", "command", command=parent.open, label="Load program")
    self.wgt.addmenuitem("File", "command", command=parent.reload, label="Reload program", state=DISABLED)
    self.wgt.addmenuitem("File", "separator")
    self.wgt.addmenuitem("File", "command", command=sys.exit, label="Exit")
    self.wgt.addmenu("About", None, side=RIGHT)
    self.wgt.addmenuitem("About", "command", command=parent.about, label="About TheDoc")
    self.file = self.wgt.component("File-menu")	  # Menú File
    self.about = self.wgt.component("About-menu") # Menú About
   
class Program:
  def __init__(self, parent):
    self.br = {} # Los breakpoints definidos: se eliminan al cargar, recargar y resetear
    self.wgt = Pmw.ScrolledText(parent)
    self.wgt._vertScrollbar.configure(width=10)
    self.wgt._horizScrollbar.configure(width=10)
    self.wgt.pack(expand=YES, fill=BOTH)
    self.text = self.wgt._textbox
    self.pcBgColor = "#fff135"
    self.bgColor = "#10106b"
    self.numFgColor = "yellow"
    self.linFgColor = "grey"
    self.brkBgColor = "orange"
    self.brkFgColor = "black"
    self.selectCursor = "hand2"
    self.noSelectCursor = "left_ptr"
    self.font = "Courier -12"
    self.text.configure(state=DISABLED, bg=self.bgColor, wrap=NONE,
                        cursor=self.noSelectCursor, font=self.font)
  
  def breakpoints(self, t, n):
    if self.br.has_key(n):  # Si ya existe, lo eliminamos
      del self.br[n]
      self.text.tag_configure(t, foreground=self.numFgColor, background=self.bgColor)
    else:
      self.br[n] = t
      self.text.tag_configure(t, foreground=self.brkFgColor, background=self.brkBgColor)

  def delBreaks(self):
    for i in self.br.keys():
      self.breakpoints(self.br[i], i)
  
  def loadCode(self, lineas):
    # Borramos los posibles breakpoints definidos
    self.delBreaks()
    self.text.configure(state=NORMAL)
    self.text.delete("0.0", END)
    nl = 0
    for l in lineas:
      if l[-1] == "\n":
        l = l[:-1]  # Eliminamos el salto de línea
      l = expandtabs(l)
      breakP = lambda e, s=self, tag="num%d" % nl, n=nl: Program.breakpoints(s, tag, n)
      self.text.tag_configure("num%d" % nl, foreground=self.numFgColor, background=self.bgColor)
      self.text.tag_configure("lin%d" % nl, foreground=self.linFgColor, background=self.bgColor)
      self.text.insert(AtInsert(), "%4d " % nl, "num%d" % nl)
      self.text.tag_bind("num%d" % nl, "<1>", breakP)
      self.text.insert(AtInsert(), (l + " " * 80)[:80], "lin%d" % nl) # Para que todas las lineas tengan el mismo tamaño
      nl += 1
      if nl != len(lineas):
        self.text.insert(AtInsert(), "\n")
    self.text.configure(state=DISABLED, cursor=self.selectCursor)

  # Desmarca la línea correspondiente al viejo PC y marca la nueva
  def setPc(self, oldPc, newPc):
    self.text.tag_configure("lin%d" % oldPc, background=self.bgColor, foreground=self.linFgColor)
    self.text.tag_configure("lin%d" % newPc, background=self.pcBgColor, foreground="black")
    self.text.yview("%d.0" % (newPc + 1))

class Registers:
  def __init__(self, parent):
    self.wgt = Pmw.ScrolledText(parent)
    self.wgt._vertScrollbar.configure(width=10)
    self.wgt._horizScrollbar.configure(width=10)
    self.wgt.pack(expand=YES, fill=BOTH)
    self.text = self.wgt._textbox
    self.text.configure(state=DISABLED, bg="white", wrap=NONE, cursor="left_ptr")
    self.text.tag_configure("reg", foreground="#4337cc")

  def reset(self):
    self.local = []
    self.text.configure(state=NORMAL)
    self.text.delete("0.0", END)
    self.text.configure(state=DISABLED)

  def update(self, entero):
    self.text.configure(state=NORMAL)
    if entero:
      reg = self.re.ultReg
      new = self.local.count(reg) == 0 # Indica si el registro modificado es nuevo
      keys = self.re.r.keys()
      pref = "$r"
      value = "%7s: %15d" % (reg, self.re.ultValor)
    else:
      reg = self.rr.ultReg
      new = self.local.count(reg) == 0
      keys = self.rr.r.keys()
      pref = "$f"
      value = "%7s: %15f" % (reg, self.rr.ultValor)
    # Obtenemos el índice del registro: primero los ordenamos numéricamente
    keynum = []
    for key in keys:
      if key not in ["$zero", "$sp", "$fp", "$ra", "$sc", "$a0", "$a1", "$fzero", "$fa"]:
        keynum.append(long(key[2:]))
    keynum.sort()
    self.local = []
    for key in keynum:
      self.local.append(pref + str(key))
    ind = self.local.index(reg) + 1
    if new: # Añadimos la línea nueva
      self.text.insert("%d.0" % ind, value + "\n")
    else:	 # Borramos la línea y la añadimos modificada
      self.text.delete("%d.0" % ind, "%d.0 lineend" % ind)
      self.text.insert("%d.0" % ind, value) 
    self.text.tag_add("reg", "%d.0" % ind, "%d.0 linestart + 8 char" % ind)
    self.text.configure(state=DISABLED)
    self.text.yview("%d.0" % ind)

class Integers(Registers):
  def __init__(self, parent, maq):
    self.re = maq.re
    self.local = [] # Contiene el nombre de los registros que estamos mostrando
    Registers.__init__(self, parent)

  def update(self):
    Registers.update(self, 1)

class Reals(Registers):
  def __init__(self, parent, maq):
    self.rr = maq.rr
    self.local = []
    Registers.__init__(self, parent)

  def update(self):
    Registers.update(self, 0)

class Specific(Registers):
  def __init__(self, parent, maq):
    self.re = maq.re
    self.rr = maq.rr
    Registers.__init__(self, parent)
    self.spf = ["$zero", "$sp","$fp", "$ra", "$sc", "$a0",  "$a1", "*", "$fzero", "$fa"]

  def reset(self):
    self.text.configure(state=NORMAL)
    self.text.delete("0.0", END)
    for reg in self.spf:
      ind = self.spf.index(reg) + 1 # Le sumamos 1 porque la primera línea es la 0
      if reg == "*": # Indica que tenemos que dejar un espacio
        lin = "\n"
      elif reg == "$zero":
        lin = "%7s: %15d\n" % ("$zero", 0)
      elif reg == "$fzero":
        lin = "%7s: %15f\n" % ("$fzero", 0)
      else:
        lin = "%7s:\n" % reg
      self.text.insert(AtInsert(), lin)
      self.text.tag_add("reg", "%d.0" % ind, "%d.8" % ind)
    self.text.configure(state=DISABLED)

  def update(self):
    self.text.configure(state=NORMAL)
    # Obtenemos el índice del registro que ha cambiado
    if self.re.cambios:
      reg = self.re.ultReg
      val = self.re.ultValor
    else:
      reg = self.rr.ultReg
      val = self.rr.ultValor
    ind = self.spf.index(reg) + 1
    self.text.delete("%d.0" % ind, "%d.0 lineend" % ind)
    if self.re.cambios:
      self.text.insert("%d.0" % ind, "%7s: %15d" % (reg, val))
    else:
      self.text.insert("%d.0" % ind, "%7s: %13f" % (reg, val))
    self.text.tag_add("reg", "%d.0 linestart" % ind, "%d.0 linestart + 8 char" % ind)
    self.text.configure(state=DISABLED)

  def delete(self):
    self.text.configure(state=NORMAL)
    self.text.delete("0.0", END)
    self.text.configure(state=DISABLED)

class Memory:
  def __init__(self, parent, maq):
    self.rossi = maq
    self.local = [] # Contiene las posiciones de memoria que estamos mostrando actualmente
    self.wgt = Pmw.ScrolledText(parent)
    self.wgt._vertScrollbar.configure(width=10)
    self.wgt._horizScrollbar.configure(width=10)
    self.wgt.pack(expand=YES, fill=BOTH)
    self.text = self.wgt._textbox
    self.text.configure(state=DISABLED, bg="white", wrap=NONE, cursor="left_ptr")
    self.text.tag_configure("pos", foreground="red")

  def reset(self):
    self.local = []
    self.text.configure(state=NORMAL)
    self.text.delete("0.0", END)
    self.text.configure(state=DISABLED)

  def update(self):
    self.text.configure(state=NORMAL)
    new = self.local.count(self.rossi.mem.ultDir) == 0 # Indica si se trata de una posición nueva
    self.local = self.rossi.mem.m.keys()
    self.local.sort()
    ind = self.local.index(self.rossi.mem.ultDir) + 1
    if type(self.rossi.mem.ultValor) == types.FloatType:
      format = "%5d: %15f"
    else:
      format = "%5d: %15d"
    if new:
      if not self.rossi.ASCIIZ:
        self.text.insert("%d.0" % ind, format % (self.rossi.mem.ultDir, self.rossi.mem.ultValor) + "\n")
        self.text.tag_add("pos", "%d.0 linestart" % ind, "%d.0 linestart + 6 char" % ind)
      else:
        ind = self.local.index(self.rossi.ASCIIZ_POS) + 1
	inddesp = 0 # Desplazamiento respecto al índice
        for pos in range(self.rossi.ASCIIZ_POS, self.rossi.mem.ultDir + 1):
	  self.text.insert("%d.0" % (ind + inddesp), format % (pos, self.rossi.mem.m[pos]) + "\n")
          self.text.tag_add("pos", "%d.0 linestart" % (ind + inddesp), "%d.0 linestart + 6 char" % (ind + inddesp))
	  inddesp += 1
    else:
      if not self.rossi.ASCIIZ:
        self.text.delete("%d.0" % ind, "%d.0 lineend" % ind)
        self.text.insert("%d.0" % ind, format % (self.rossi.mem.ultDir, self.rossi.mem.ultValor))
        self.text.tag_add("pos", "%d.0 linestart" % ind, "%d.0 linestart + 6 char" % ind)
      else:
        ind = self.local.index(self.rossi.ASCIIZ_POS) + 1
	inddesp = 0
        for pos in range(self.rossi.ASCIIZ_POS, self.rossi.mem.ultDir + 1):
	  self.text.insert("%d.0" % (ind + inddesp), format % (pos, self.rossi.mem.m[pos]))
          self.text.tag_add("pos", "%d.0 linestart" % (ind+ inddesp), "%d.0 linestart + 6 char" % (ind + inddesp))
	  inddesp += 1
    self.text.configure(state=DISABLED)
    ind = self.local.index(self.rossi.mem.ultDir) + 1
    self.text.yview("%d.0" % ind)

class Terminal:
  def __init__(self, parent):
    self.entry = ""	# Aquí iremos almacenando los caracteres introducidos en una lectura
    self.wgt = Pmw.ScrolledText(parent)
    self.wgt._vertScrollbar.configure(width=10)
    self.wgt._horizScrollbar.configure(width=10)
    self.wgt.pack(expand=YES, fill=BOTH)
    self.text = self.wgt._textbox
    self.color="#fffce5"
    self.text.configure(state=DISABLED, bg=self.color, wrap=NONE, cursor="left_ptr")
    self.text.tag_configure("normal", foreground="black")
    self.text.tag_configure("error", foreground="red")
    self.text.tag_configure("sys", foreground="#2f7a16")
    self.text.bind("<KeyPress>", self.addEntry)
    self.text.bind("<Return>", self.endEntry)

  def addEntry(self, e):
   if e.keysym in ["BackSpace", "Delete"]:
     self.entry = self.entry[:-1]
   else:
     self.entry += e.char

  def endEntry(self, e):
    self.text.setvar(name="end", value="1")  # Cambia el valor de la variable de espera
    
  def read(self):
    self.entry = ""
    self.text.focus_set()
    self.text.configure(state=NORMAL)
    self.text.setvar(name="end", value="0")
    self.text.wait_variable(name="end") # Espera hasta que la variable "end" cambie de valor
    self.text.configure(state=DISABLED)
    return self.entry

  def write(self, str):
    self.text.configure(state=NORMAL)
    self.text.insert(AtInsert(), str, "normal")
    self.text.configure(state=DISABLED)
    self.text.yview(END)
  
  def reset(self):
    self.text.configure(state=NORMAL)
    self.text.delete("0.0", END)
    self.text.insert(AtInsert(), "Bienvenido a TheDoc: un emulador para la máquina virtual ROSSI.\n\n", "sys")
    self.text.configure(state=DISABLED)

  def showErrors(self, lista):
    self.text.configure(state=NORMAL)
    self.text.delete("0.0", END)
    for error in lista:
      self.text.insert(AtInsert(), error, "error")
      self.text.insert(AtInsert(), "\n")
    self.text.configure(state=DISABLED)
    self.text.yview(END)

  def showEnd(self, ren, rrn):
    self.text.configure(state=NORMAL)
    self.text.insert(AtInsert(), "\nREPG usados: %2d\n" % ren+ \
		     		 "RRPG usados: %2d\n" %  rrn, "sys")
    self.text.configure(state=DISABLED)
    self.text.yview(END)

class StepCounter:
  def __init__(self, parent, steps=0):
    self.wgt = Label(parent, text="Steps: %d" % steps, width=20, bg="white", fg="black",
		     relief=SUNKEN, borderwidth=2)
    self.wgt.pack(expand=YES, fill=BOTH, side=LEFT)

  def set(self, steps):
    self.wgt.configure(text="Steps: %d" % steps)
 
class GUI(Frame):
  def __init__(self, fich=None):
    Frame.__init__(self)
    self.pack(expand=YES, fill=BOTH)
    self.master.title("TheDoc " + release)
    self.master.minsize(780, 540)
    self.fich = fich
    self.rossi = Rossi()
    self.rossi.entrada = self.fin
    self.rossi.salida = self.fout
    self.pasos = 0
    self.menu = Menu(self)
    pane = Pmw.PanedWidget(self, hull_width=780, hull_height=480, orient="vertical")
    pane.pack(expand=YES, fill=BOTH)
    upane = pane.add("Up", min=400)
    dpane = pane.add("Down", min=70, size=70)
    pane = Pmw.PanedWidget(upane, orient="horizontal")
    pane.pack(expand=YES, fill=BOTH)
    lpane = pane.add("Left", min=300)
    cpane = pane.add("Center", min=200, size=200)
    rpane = pane.add("Right", min=200, size=200)
    pane = Pmw.PanedWidget(cpane, orient="vertical")
    pane.pack(expand=YES, fill=BOTH)
    cupane = pane.add("CenterUp", min=200)
    cdpane = pane.add("CenterDown", min=200)
    pane = Pmw.PanedWidget(rpane, orient="vertical")
    pane.pack(expand=YES, fill=BOTH)
    rupane = pane.add("RightUp", min=100, size=100, max=150)
    rdpane = pane.add("RightDown")
    self.programa = Program(lpane)
    self.re = Integers(cupane, self.rossi)
    self.rr = Reals(cdpane, self.rossi)
    self.spec = Specific(rupane, self.rossi)
    self.mem = Memory(rdpane, self.rossi)
    self.terminal = Terminal(dpane)
    buttons = Frame(self)
    buttons.pack(fill=X, side=BOTTOM)
    self.bStep = Button(buttons, text="Step", width=20, command=self.step, state=DISABLED)
    self.bExecute = Button(buttons, text="Execute", width=20, command=self.execute, state=DISABLED)
    self.bReset = Button(buttons, text="Reset", width=20, command=self.reset, state=DISABLED)
    self.bStep.pack(expand=YES, fill=BOTH, side=LEFT)
    self.bExecute.pack(expand=YES, fill=BOTH, side=LEFT)
    self.bReset.pack(expand=YES, fill=BOTH, side=LEFT)
    self.counter = StepCounter(buttons)

    if fich:	# Si se ha especificado un fichero, intentamos cargarlo
      self.load(fich)
    try:
      self.mainloop()
    except KeyboardInterrupt:
      print "Hasta otra!"
    
  def enableButtons(self):
    self.bStep.configure(state=NORMAL)
    self.bExecute.configure(state=NORMAL)
    self.bReset.configure(state=NORMAL)
    self.focus_set()
    self.bind("<Return>", self.step) # Al pulsar Return se ejecuta un paso

  def disableButtons(self):
    self.bStep.configure(state=DISABLED)
    self.bExecute.configure(state=DISABLED)
    self.bReset.configure(state=DISABLED)
    self.unbind("<Return>")

  def onlyReset(self):
    self.bStep.configure(state=DISABLED)
    self.bExecute.configure(state=DISABLED)
    self.bReset.configure(state=NORMAL)
    self.unbind("<Return>")

  def onlyStop(self):
    self.bStep.configure(state=DISABLED)
    self.bExecute.configure(state=NORMAL)
    self.bReset.configure(state=DISABLED)
    self.unbind("<Return>")
  
  def enableReload(self):
    self.menu.file.entryconfig(1, state=NORMAL)

  def fin(self):
    self.disableButtons()
    value = self.terminal.read()
    self.enableButtons()
    return value

  def fout(self, value):
    self.terminal.write(value)
  
  def open(self):
    dialog = LoadFileDialog(self.master)
    fich = dialog.go(pattern="*.rossi", key="rossi")
    if fich:
      self.load(fich)
      
  def load(self, fich):
    try:
      f = open(fich, "r")
      lineas = f.readlines()
      f.close()
    except IOError, e:
      print "No puedo cargar el fichero %s: %s." % (repr(fich), str(e))
      sys.exit(-1)
    self.fich = fich
    self.rossi.inicializa()
    self.rossi.cargaPrograma(lineas)  # La máquina carga y parsea el programa
    self.programa.loadCode(lineas) # Mostramos el programa en el ScrolledText
    self.spec.delete()
    self.enableReload()
    if self.rossi.err.e:
      self.disableButtons()
      self.terminal.showErrors(self.rossi.err.e)
    else:
      self.reset()
    
  def reload(self):
    self.load(self.fich)
    
  def about(self):
    root = Toplevel() 
    root.configure(background="white")
    root.title("About TheDoc")
    root.minsize(280, 300)
    root.maxsize(280, 300)
    Label(root, text="\nTheDoc", background="white").pack(side=TOP)
    Label(root, text="Un emulador para la máquina virtual ROSSI\n", background="white").pack(side=TOP)
    self.foto = PhotoImage(file="sun.gif", master=root)
    Label(root, image=self.foto, borderwidth=0).pack(side=TOP)
    Label(root, text="\nVersión 1.0\n", background="white").pack(side=TOP)
    Label(root, text="Antonio Vilar Sánchez", background="white").pack(side=TOP)
    Label(root, text="2004", background="white").pack(side=TOP)
    root.grab_set()
    
  def step(self, e=None):
    if self.rossi.estado == Rossi.FUNCIONANDO:
      self.pasos += 1
    oldPc = self.rossi.pc	# El PC que teníamos antes de ejecutar un paso en Rossi
    self.rossi.ejecutaPaso()
    self.programa.setPc(oldPc, self.rossi.pc) # Marcamos el nuevo PC
    if self.rossi.NOP == 1:
      self.pasos -= 1
    self.counter.set(self.pasos) # Mostramos el número de pasos
    if self.rossi.re.cambios:
      if self.rossi.re.ultReg in ["$zero", "$sp", "$fp", "$ra", "$sc", "$a0", "$a1"]:
        self.spec.update() 
      else:
        self.re.update()
    if self.rossi.rr.cambios:
      if self.rossi.rr.ultReg in ["$fzero", "$fa"]:
        self.spec.update()
      else:
        self.rr.update()
    if self.rossi.mem.cambios:
      self.mem.update()
    if self.rossi.estado == Rossi.ERROR:
      self.parado = 1
      self.onlyReset()
      dialog = Pmw.MessageDialog(self, title="Execution error. PC: %d" % self.rossi.pc, defaultbutton=0,
                                 message_text=self.rossi.error_msg +" "*(50-len(self.rossi.error_msg)),
				 buttons=("Ok",), iconpos = "w", icon_bitmap="warning")
      dialog.resizable(0, 0)
      dialog.activate()
    elif self.rossi.estado == Rossi.PARADO:
      self.parado = 1
      self.onlyReset()
      self.counter.wgt.configure(background="green")
      ren = len(self.rossi.re.r.keys()) - 7
      rrn = len(self.rossi.rr.r.keys()) - 2
      self.terminal.showEnd(ren, rrn)
    
  def execute(self):
    self.menu.wgt.disableall()
    self.bExecute.configure(state=NORMAL, text="Stop execution", command=self.stop)
    self.parado = 0
    while 1:
      self.onlyStop()
      self.bind("<Return>", self.stop)
      self.step()
      self.update()  # Redibuja todos los widgets que estén pendientes
      if self.programa.br.has_key(self.rossi.pc):
        break
      if self.parado:
        break
    self.bExecute.configure(text="Execute", command=self.execute)
    self.unbind("<Return>")
    self.menu.wgt.enableall()
    if self.rossi.estado == Rossi.FUNCIONANDO:
      self.enableButtons()

  def stop(self, e=None):
    self.parado = 1
    
  def reset(self):
    oldPc = self.rossi.pc	# El PC que teníamos antes de pulsar reset
    self.rossi.inicializa()
    self.pasos = 0
    self.counter.set(self.pasos)
    self.counter.wgt.configure(background="white")
    self.re.reset()
    self.rr.reset()
    self.spec.reset()
    self.mem.reset()
    self.terminal.reset()
    #self.programa.delBreaks()		# No eliminamos los breakpoints al resetear la máquina
    self.programa.setPc(oldPc, self.rossi.pc)
    self.enableButtons()
    self.menu.wgt.enableall()
