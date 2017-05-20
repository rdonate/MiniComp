import memoria
import Rossi
R=Rossi
import sys

def inicializaRegistros(c):
  c.append(R.addi("sp", "zero", memoria._dirLibre))
  c.append(R.add("fp", "zero", "zero"))
  c.append(R.fadd("fa", "fzero", "fzero"))

def gencodigo(principal, funciones, cadenas, variables):
  memoria.asignaDir(variables)
  memoria.asignaDir(cadenas)

  codigo= []
  codigo.append(R.Directiva(".data"))
  for cad in cadenas:
    cad.inicializacion(codigo)
  for f in funciones:
    f.fijaDireccion()
  codigo.append(R.Comentario("Comienzo del programa"))
  codigo.append(R.Directiva(".text"))
  inicializaRegistros(codigo)
  principal.generaCodigo(codigo)
  codigo.append(R.Comentario("Fin del programa"))
  codigo.append(R.addi("sc", "zero", 6, "exit"))
  codigo.append(R.syscall())
  for f in funciones:
    f.generaFuncion(codigo)
  try:
    fsalida= open("a.rossi", "w")
  except:
    sys.stderr.write("No he podido abrir a.rossi para escritura.\n")
    sys.exit(1)
  for s in codigo:
    fsalida.write("%s\n" % s)
  fsalida.close()

