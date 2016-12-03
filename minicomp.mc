None	None         [ \t\n]+
None	None         //[^\n]*\n
cad	trataCad     "[^"\n]*"
id	trataId	     [a-zA-Z][a-zA-Z0-9_]*
num	trataEntero  [0-9]+
opcom   None         [<>]=?|!?=
opad	None	     [-+]
opmul	None	     [*/%]

%

import AST
import cadenas
import errores
import errsintactico
import funciones
import gencodigo
from optparse import OptionParser
from sets import ImmutableSet
import TDS as tds
import tipos
import variables

def trataCad(c):
  c.valor= c.lexema[1:-1]

_reservadas=ImmutableSet(["cadena", "de", "devuelve",
        "entero", "entonces", "es", "escribe", "fin",
        "funcion", "globales", "llama",  "locales",
        "nl", "secuencia", "si", "si_no", "vector"])

def trataId(c):
  if c.lexema in _reservadas:
    c.cat= c.lexema

def trataEntero(c):
  try:
    c.valor= int(c.lexema)
  except:
    errores.lexico("No he podido convertir %s en un entero." % c.lexema, c.nlinea)

def error_lexico(linea, cars):
  if len(cars)> 1:
    if len(cars)> 10:
      cars= cars[:10]+"..."
    errores.lexico("No he podido analizar la cadena %s." % repr(cars), linea)
  else:
    errores.lexico("No he podido analizar el carácter %s." % repr(cars), linea)

%

$errores.sintactico("He encontrado entrada después del último fin.", mc_al.linea())$
$mc_al.sincroniza(["mc_EOF"])$

<Programa> ->
  (<Globales>)?
  (<Funcion>)*
  <Compuesta>
    @Programa.principal= Compuesta.arb@
  ;

<Programa> -> error
  @if errsintactico.trataError(mc_al, mc_nt, "<Programa>"):@
  @  mc_reintentar()@
  @else:@
  @  Programa.principal= AST.NodoVacio(mc_al.linea())@
  ;

<Globales> ->
  globales
  @Definicion.variables= VariablesGlobales@
  (
    <Definicion> ";"
  )+
  fin
  ;

<Globales> -> error
  @if errsintactico.trataError(mc_al, mc_nt, "<Globales>"):@
  @  mc_reintentar()@
  ;

<Definicion> ->
  id @l=[id]@
  ( "," id @l.append(id2)@ )*
  ":" <Tipo>
  @for id in l:@
  @  var= variables.Variable(id.lexema, Tipo.tipo, TDS.enFuncion()!= None, id.nlinea)@
  @  Definicion.variables.append(var)@
  @  TDS.define(id.lexema, var, id.nlinea)@
  ;

<Definicion> -> error
  @if errsintactico.trataError(mc_al, mc_nt, "<Definicion>"):@
  @  mc_reintentar()@
  ;

<Tipo>-> entero @Tipo.tipo= tipos.Entero@ ;
<Tipo>-> cadena @Tipo.tipo= tipos.Cadena@ ;
<Tipo>-> vector "[" num "]" de <Tipo> @Tipo.tipo= tipos.Array(num.valor, Tipo1.tipo)@ ;

<Funcion> ->
  funcion id
  @f= funciones.NodoFuncion(id.lexema, funcion.nlinea)@
  @TDS.define(id.lexema, f, id.nlinea)@
  @TDS.entraFuncion(f)@
  <Perfil> es
  @f.fijaPerfil(Perfil.parametros, Perfil.tipo)@
  (
    locales
      (
        @Definicion.variables= f.listaVariables()@
        <Definicion> ";"
      )+
    fin
  )?
  <Compuesta>
  @f.fijaCodigo(Compuesta.arb)@
  @Funciones.append(f)@
  @TDS.salFuncion()@
  ;

<Funcion>-> error
  @if errsintactico.trataError(mc_al, mc_nt, "<Funcion>"):@
  @  mc_reintentar()@
  @else:@
  @  f= TDS.enFuncion()@
  @  if f:@
  @    try:@
  @      t= f.tipoDevuelto@
  @    except AttributeError:@
  @      f.fijaPerfil([], tipos.Error)@
  @    TDS.salFuncion()@
  ;

<Perfil> ->
  @Perfil.parametros= []@
  "("
    (
      @Definicion.variables= Perfil.parametros@ <Definicion>
      ( ";" @Definicion2.variables= Perfil.parametros@ <Definicion> )*
    )?
  ")" ":"
  <Tipo> @Perfil.tipo= Tipo.tipo@
  ;

<Compuesta> ->
  @l= []@
  secuencia ( <Sentencia> @l.append(Sentencia.arb)@ )* fin
  @Compuesta.arb= AST.NodoCompuesta(l, secuencia.nlinea)@
  ;

<Sentencia> ->
  <Compuesta>
  @Sentencia.arb= Compuesta.arb@
  ;

<Sentencia> ->
  escribe <Expresion> ";"
  @Sentencia.arb= AST.NodoEscribe(Expresion.arb, escribe.nlinea)@
  ;

<Sentencia> ->
  nl ";"
  @Sentencia.arb= AST.NodoEscribe(AST.NodoCadena(cadenaNL, nl.nlinea),nl.nlinea)@
  ;

<Sentencia> ->
  si <Expresion> entonces <Sentencia> si_no <Sentencia> fin
  @Sentencia.arb= AST.NodoSi(Expresion.arb, Sentencia1.arb, Sentencia2.arb, si.nlinea)@
  ;

<Sentencia> ->
  @nlinea= mc_al.linea()@
  <AccesoVariable> ":=" <Expresion> ";"
  @Sentencia.arb= AST.NodoAsignacion(AccesoVariable.arb, Expresion.arb, nlinea)@
  ;

<Sentencia> ->
  devuelve <Expresion> ";"
  @f= TDS.enFuncion()@
  @if not f:@
  @  errores.semantico("Sólo puede aparecer devuelve dentro de una función.",@
  @    devuelve.nlinea)@
  @  f= TDS.recupera(funcionError)@
  @Sentencia.arb= AST.NodoDevuelve(Expresion.arb, f, devuelve.nlinea)@
  ;

<Sentencia>-> error
  @if errsintactico.trataError(mc_al, mc_nt, "<Sentencia>"):@
  @  mc_reintentar()@
  @else:@
  @  Sentencia.arb= AST.NodoVacio(mc_al.linea())@
  ;

<Expresion> ->
  <Comparado> @arb= Comparado.arb@
  ( opcom <Comparado>
    @arb= AST.NodoComparacion(opcom.lexema, arb, Comparado_.arb, opcom.nlinea)@
  )*
  @Expresion.arb= arb@
  ;

<Expresion>-> error
  @if errsintactico.trataError(mc_al, mc_nt, "<Expresion>"):@
  @  mc_reintentar()@
  @else:@
  @  Expresion.arb= AST.NodoVacio(mc_al.linea())@
  ;

<Comparado> ->
  <Producto> @arb= Producto.arb@
  ( opad <Producto>
    @arb= AST.NodoAritmetica(opad.lexema, arb, Producto_.arb, opad.nlinea)@
  )*
  @Comparado.arb= arb@
  ;

<Producto> ->
  <Termino> @arb= Termino.arb@
  ( opmul <Termino>
    @arb= AST.NodoAritmetica(opmul.lexema, arb, Termino_.arb, opmul.nlinea)@
  )*
  @Producto.arb= arb@
  ;

<Termino> ->
  <AccesoVariable>
  @Termino.arb= AccesoVariable.arb@
  | <Llamada> @Termino.arb= Llamada.arb@
  | num @Termino.arb= AST.NodoEntero(num.valor, num.nlinea)@
  | "(" <Expresion> ")" @Termino.arb= Expresion.arb@
  | cad
    @c= cadenas.Cadena(cad.valor)@
    @Termino.arb= AST.NodoCadena(c, cad.nlinea)@
    @Cadenas.append(c)@
  ;

<AccesoVariable> ->
  id
  @if not TDS.existe(id.lexema):@
  @  errores.semantico("La variable %s no está definida." % id.lexema, id.nlinea)@
  @  var= variables.Variable(id.lexema, tipos.Error, TDS.enFuncion()!= None, id.nlinea)@
  @  TDS.define(id.lexema, var, id.nlinea)@
  @arb= AST.NodoAccesoVariable(TDS.recupera(id.lexema), id.nlinea)@
  (
    "[" @nlinea= mc_al.linea()@ <Expresion> "]"
    @arb= AST.NodoAccesoVector(arb, Expresion.arb, nlinea)@
  )*
  @AccesoVariable.arb= arb@
  ;

<Llamada> ->
  llama id
  "("
    @l=[]@
    ( <Expresion> @l.append(Expresion_.arb)@
      ( "," <Expresion> @l.append(Expresion_.arb)@)*
    )?
  ")"
  @if not TDS.existe(id.lexema):@
  @  f= TDS.recupera(funcionError)@
  @  errores.semantico("La función %s no está definida." % id.lexema, id.nlinea)@
  @else:@
  @  f= TDS.recupera(id.lexema)@
  @Llamada.arb= AST.NodoLlamada(f, l, llama.nlinea)@
  ;

%

def inicializaGlobales():
  global TDS, Funciones, VariablesGlobales, Cadenas
  global funcionError, cadenaNL
  TDS=tds.TDS()
  Funciones= []
  VariablesGlobales= []
  Cadenas= []
  cadenaNL= cadenas.Cadena("\n")
  Cadenas.append(cadenaNL)
  funcionError= "#ferror"
  ferror= funciones.NodoFuncion(funcionError,0)
  ferror.fijaPerfil([], tipos.Error)
  TDS.define(funcionError, ferror, 0)
  errsintactico.inicializa(mc_primeros, mc_siguientes)

def main():
  parser= OptionParser(usage="%prog [<opciones>] <fichero>")
  parser.add_option("-l", "--escribeLexico", action="store_true", default=False,
                    help= "Escribe el resultado del análisis léxico")
  parser.add_option("-s", "--escribeAST", action="store_true", default= False,
                    help= "Escribe el AST")
  (opciones, args)= parser.parse_args()
  if len(args)!= 1:
    sys.stderr.write("Error, debes incluir un fichero fuente")
    sys.exit(1)
  else:
    try:
      f= open(args[0])
    except:
      sys.stderr.write("Error, no he podido abrir %s para lectura.\n" % args[0])
      sys.exit(1)

  if opciones.escribeLexico:
    lex= AnalizadorLexico(f)
    lex.avanza()
    while lex.actual.cat!= "mc_EOF":
      print lex.actual
      lex.avanza()
  else:
    inicializaGlobales()
    A= AnalizadorSintactico(f)
    principal= A.Programa.principal
    principal.compsemanticas()
    for f in Funciones:
      f.compsemanticas()
    if opciones.escribeAST:
      if errores.errores:
        errores.escribeErrores(sys.stderr)
      print principal
      for f in Funciones:
        print f.arbol()
    else:
      if errores.errores:
        errores.escribeErrores(sys.stderr)
        sys.exit(1)
      else:
        gencodigo.gencodigo(principal, Funciones, Cadenas, VariablesGlobales)
