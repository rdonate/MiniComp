#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Este código ha sido generado por metacomp, versión version_mc
import sys, re, string
class mc_error_sintaxis(Exception): pass
class mc_error_noEOF(Exception): pass
class mc_error_abandonar(Exception): pass
def mc_error(nt, esp):
    raise mc_error_sintaxis,(nt,esp)
def mc_abandonar():
    raise mc_error_abandonar
class ComponenteLexico:
    def __init__(self, cat, lexema, nlinea):
        self.cat = cat
        self.lexema = lexema
        self.nlinea = nlinea
    def __str__(self):
        s = ['%s: %s' % (repr(k), repr(v)) for k,v in self.__dict__.items() if k != 'cat']
        if s:
            return '%s (%s)' % (self.cat,', '.join(s))
        else:
            return self.cat
class AnalizadorLexico:
    def __init__(self, entrada):
        if isinstance(entrada, basestring):
            if isinstance(entrada, unicode):
                self.l = entrada
            else:
                self.l = entrada.decode('utf-8')
        else:
            try:
                ll = entrada.readlines()
            except:
                sys.stderr.write('Error: no he podido leer la entrada ¿es un fichero?\n')
                sys.exit(1)
            ll = [ l.decode('utf-8') for l in ll]
            self.l = string.join(ll,'')
            entrada.close()
        self.nlactual = 1
        self.actual = ComponenteLexico(None, None, 0)
        try:
            self.error_lexico = error_lexico
        except:
            self.error_lexico = self._error_lexico
        self.i = 0
    def _error_lexico(self, linea_error, cars):
        sys.stderr.write((u'Error léxico no tratado en línea %d: No esperaba %s.\n' % (linea_error, repr(cars))).encode('utf-8'))
        sys.exit(1)
    def linea(self):
        return self.actual.nlinea
    def sincroniza(self, sincr, enEOF = mc_abandonar):
        while self.actual.cat not in sincr and self.actual.cat != 'mc_EOF':
            self.avanza()
        if self.actual.cat =='mc_EOF' and not 'mc_EOF' in sincr:
            enEOF()
    def avanza(self):
        if self.i >= len(self.l):
            self.actual = ComponenteLexico('mc_EOF', '', self.nlactual)
            return self.actual
        carsError, lineaError = [], 0
        while 1:
            (info, ni) = self.analiza(self.i, self.l)
            if not info is None:
                nl = self.nlactual
                if carsError:
                    self.error_lexico(lineaError, ''.join(carsError))
                    self.nlactual += carsError.count('\n')
                    carsError, lineaError = [], 0
                cat, ff = info
                lexema = self.l[self.i:ni]
                self.i = ni
                self.nlactual += lexema.count('\n')
                componente = ComponenteLexico(cat, lexema, nl)
                if ff:
                    ff(componente)
                if not componente.cat is None:
                    self.actual = componente
                    return componente
                continue
            else:
                if self.i >= len(self.l):
                    if carsError:
                        self.error_lexico(lineaError, ''.join(carsError))
                        self.nlactual += carsError.count('\n')
                    self.actual = ComponenteLexico('mc_EOF', '', self.nlactual)
                    return self.actual
                if lineaError == 0: lineaError = self.nlactual
                carsError.append(self.l[self.i])
                self.i += 1
        return self.actual
    def analiza(self, i, s):
        q = 0
        uf = None
        ufi = None
        while i <= len(s):
            if i == len(s):
                c = ''
            else:
                c = s[i]
            if q < 8:
                if q < 4:
                    if q < 2:
                        if q < 1:
                            if c == u'f':
                                q = 3
                            elif u'\t' <= c <= u'\n' or c == u' ':
                                q = 6
                            elif c == u'"':
                                q = 1
                            elif c == u't':
                                q = 2
                            elif c == u'(':
                                q = 5
                            elif c == u']':
                                q = 7
                            elif c == u')':
                                q = 4
                            else:
                                break
                        else:
                            if not (c == u'\n' or c == u'"'):
                                q = 1
                            elif c == u'"':
                                q = 11
                            else:
                                break
                    else:
                        if q < 3:
                            if c == u'i':
                                q = 10
                            else:
                                break
                        else:
                            if c == u'o':
                                q = 8
                            else:
                                break
                else:
                    if q < 6:
                        if q < 5:
                            uf = (u'!)', None)
                            ufi = i
                            break
                        else:
                            uf = (u'!(', None)
                            ufi = i
                            break
                    else:
                        if q < 7:
                            uf = (None, None)
                            ufi = i
                            if u'\t' <= c <= u'\n' or c == u' ':
                                q = 6
                            else:
                                break
                        else:
                            uf = (u'corchete', None)
                            ufi = i
                            break
            else:
                if q < 12:
                    if q < 10:
                        if q < 9:
                            if c == u'n':
                                q = 9
                            else:
                                break
                        else:
                            if c == u'd':
                                q = 12
                            else:
                                break
                    else:
                        if q < 11:
                            if c == u'n':
                                q = 14
                            else:
                                break
                        else:
                            uf = (u'cadena', trataCadena)
                            ufi = i
                            if c == u'"':
                                q = 1
                            else:
                                break
                else:
                    if q < 14:
                        if q < 13:
                            if c == u'o':
                                q = 13
                            else:
                                break
                        else:
                            uf = (u'fondo', None)
                            ufi = i
                            break
                    else:
                        if q < 15:
                            if c == u't':
                                q = 15
                            else:
                                break
                        else:
                            if q < 16:
                                if c == u'a':
                                    q = 16
                                else:
                                    break
                            else:
                                uf = (u'tinta', None)
                                ufi = i
                                break
            i+=1
        return (uf, ufi)
# Código de usuario
class Info:
  def __init__(self):
    self.fondo= None
    self.tinta= None
    self.raiz= []
    self.hijos= []
_nombres= {
  "mc_EOF": "fin de la entrada",
  "cadena": "literal de cadena",
  "corchete": "corchete cerrado",
  "fondo": "color de fondo",
  "tinta": "color de tinta",
  "!(": "paréntesis abierto",
  "!)": "paréntesis cerrado"
}
def trataCadena (cad):
  cad.cad= string.replace(cad.lexema[1:-1], '""', '"')
def error_lexico(linea, cadena):
  if len(cadena)==1:
    error("Carácter %s inesperado en línea %d." % (repr(cadena), linea))
  else:
    error("Caracteres %s inesperados en línea %d." % (repr(cadena[:10]), linea))
class vAExcepcion(Exception):
  def __init__(self, mensaje):
    self.mensaje= mensaje
  def __str__(self):
    return self.mensaje
def error(mensaje):
  raise vAExcepcion(mensaje)
def error_sintactico(encontrado, esperado, linea):
  n1= _nombres[encontrado.cat]
  n2= " o un ".join([ _nombres[t] for t in esperado])
  error("En la línea %d, he encontrado un %s donde esperaba un %s"%
        (linea, n1, n2))
mc_primeros = {
    '<Arbol>' : [u'!('],
    '<Entrada>' : [u'!('],
    '<Fondo>' : [u'fondo'],
    '<Tinta>' : [u'tinta'],
}
mc_siguientes = {
    '<Arbol>' : [u'!)', u'!(', 'mc_EOF'],
    '<Entrada>' : ['mc_EOF'],
    '<Fondo>' : [u'cadena', u'tinta'],
    '<Tinta>' : [u'cadena', u'fondo'],
}
mc_aceptables = {
    '<Arbol>' : [u'!('],
    '<Entrada>' : [u'!('],
    '<Fondo>' : [u'fondo'],
    '<Tinta>' : [u'tinta'],
}
mc_anulables = {
    '<Arbol>' : False,
    '<Entrada>' : False,
    '<Fondo>' : False,
    '<Tinta>' : False,
}
class Atributos: pass
class AnalizadorSintactico:
    def __init__(self, entrada, entorno = None):
        self.mc_entorno = entorno
        self.mc_al = AnalizadorLexico(entrada)
        self.mc_al.avanza()
        self.mc_reintento = [True]
        mc_reintentar = self.mc_reintentar
        while self.mc_reintento[-1]:
            self.mc_reintento[-1] = False
            self.Entrada = Atributos()
            try:
                self.mc_analiza_Entrada(self.Entrada)
                if self.mc_al.actual.cat != 'mc_EOF':
                    raise mc_error_noEOF
            except mc_error_sintaxis, (nt,esp):
                sys.stderr.write('Error no tratado en línea %d:\n'% self.mc_al.actual.nlinea)
                sys.stderr.write((u'Estaba analizando la expansión del no terminal %s y he encontrado\n el terminal %s.\n' % (nt, self.mc_al.actual.cat)).encode('utf-8'))
                if len(esp)==1:
                    sys.stderr.write((u'Sólo valía un %s.\n' % esp[0]).encode('utf-8'))
                else:
                    sys.stderr.write((u'Tendría que haber sido uno de los siguientes: %s.\n' % string.join(esp,',')).encode('utf-8'))
                sys.exit(1)
            except mc_error_noEOF:
                sys.stderr.write((u'Error no tratado en línea %d:\n' % self.mc_al.actual.nlinea).encode('utf-8'))
                sys.stderr.write('He encontrado entrada donde esperaba ver el final del fichero\n')
                sys.exit(1)
            except mc_error_abandonar:
                pass
    def mc_reintentar(self):
        self.mc_reintento[-1] = True
    def mc_analiza_Arbol(self, Arbol):
        mc_al= self.mc_al
        self.mc_reintento.append(True)
        mc_reintentar= self.mc_reintentar
        while self.mc_reintento[-1]:
            self.mc_reintento[-1]= False
            try:
                if not mc_al.actual.cat== '!(':
                    mc_error('<Arbol>', [ '!(' ])
                Fondo= Fondo1= Atributos()
                Tinta= Tinta1= Atributos()
                Tinta2= Atributos()
                Fondo2= Atributos()
                Arbol1= Atributos()
                mc_al.avanza()
                info=Info()
                if mc_al.actual.cat in [ 'fondo', 'tinta' ]:
                    if mc_al.actual.cat== 'fondo':
                        self.mc_analiza_Fondo(Fondo1)
                        Fondo_= Fondo1
                        info.fondo= Fondo_.color
                        if mc_al.actual.cat== 'tinta':
                            self.mc_analiza_Tinta(Tinta1)
                            Tinta_= Tinta1
                            info.tinta= Tinta_.color
                    else:
                        self.mc_analiza_Tinta(Tinta2)
                        Tinta_= Tinta2
                        info.tinta= Tinta_.color
                        if mc_al.actual.cat== 'fondo':
                            self.mc_analiza_Fondo(Fondo2)
                            Fondo_= Fondo2
                            info.fondo= Fondo_.color
                if mc_al.actual.cat == 'cadena':
                    cadena = cadena1 = cadena_ = mc_al.actual
                    mc_al.avanza()
                else:
                    mc_error('<Arbol>', ['cadena'])
                info.raiz= [cadena.cad]
                while mc_al.actual.cat== 'cadena':
                    cadena2 = cadena_ = mc_al.actual
                    mc_al.avanza()
                    info.raiz.append(cadena_.cad)
                if not mc_al.actual.cat in [ '!(', '!)' ]:
                    mc_error('<Arbol>',[ '!(', '!)', 'cadena' ])
                while mc_al.actual.cat== '!(':
                    Arbol1.nivel= Arbol.nivel+1
                    self.mc_analiza_Arbol(Arbol1)
                    Arbol_= Arbol1
                    info.hijos.append(Arbol1.arbol)
                if not mc_al.actual.cat== '!)':
                    mc_error('<Arbol>',[ '!(', '!)' ])
                Arbol.arbol= info
                if mc_al.actual.cat == '!)':
                    mc_al.avanza()
                else:
                    mc_error('<Arbol>', ['!)'])
            except mc_error_sintaxis, (mc_nt, mc_t):
                if mc_al.actual.cat=="corchete": 
                  if Arbol.nivel:                
                    return                       
                  else:                          
                    mc_al.avanza()               
                else:                            
                  error_sintactico(mc_al.actual, mc_t, mc_al.linea())
        self.mc_reintento.pop()
    def mc_analiza_Entrada(self, Entrada):
        mc_al= self.mc_al
        self.mc_reintento.append(True)
        mc_reintentar= self.mc_reintentar
        while self.mc_reintento[-1]:
            self.mc_reintento[-1]= False
            try:
                if not mc_al.actual.cat== '!(':
                    mc_error('<Entrada>', [ '!(' ])
                Arbol= Arbol1= Atributos()
                Arbol2= Atributos()
                Arbol.nivel= 0
                self.mc_analiza_Arbol(Arbol1)
                Arbol_= Arbol1
                Entrada.arboles=[Arbol.arbol]
                while mc_al.actual.cat== '!(':
                    Arbol2.nivel=0
                    self.mc_analiza_Arbol(Arbol2)
                    Arbol_= Arbol2
                    Entrada.arboles.append(Arbol2.arbol)
                if not mc_al.actual.cat== 'mc_EOF':
                    mc_error('<Entrada>',[ '!(', 'mc_EOF' ])
            except mc_error_sintaxis, (mc_nt, mc_t):
                error_sintactico(mc_al.actual, mc_t, mc_al.linea())
        self.mc_reintento.pop()
    def mc_analiza_Fondo(self, Fondo):
        mc_al= self.mc_al
        if not mc_al.actual.cat== 'fondo':
            mc_error('<Fondo>', [ 'fondo' ])
        fondo = fondo1 = fondo_ = mc_al.actual
        mc_al.avanza()
        if mc_al.actual.cat == '!(':
            mc_al.avanza()
        else:
            mc_error('<Fondo>', ['!('])
        if mc_al.actual.cat == 'cadena':
            cadena = cadena1 = cadena_ = mc_al.actual
            mc_al.avanza()
        else:
            mc_error('<Fondo>', ['cadena'])
        if mc_al.actual.cat == '!)':
            mc_al.avanza()
        else:
            mc_error('<Fondo>', ['!)'])
        Fondo.color= cadena.cad
    def mc_analiza_Tinta(self, Tinta):
        mc_al= self.mc_al
        if not mc_al.actual.cat== 'tinta':
            mc_error('<Tinta>', [ 'tinta' ])
        tinta = tinta1 = tinta_ = mc_al.actual
        mc_al.avanza()
        if mc_al.actual.cat == '!(':
            mc_al.avanza()
        else:
            mc_error('<Tinta>', ['!('])
        if mc_al.actual.cat == 'cadena':
            cadena = cadena1 = cadena_ = mc_al.actual
            mc_al.avanza()
        else:
            mc_error('<Tinta>', ['cadena'])
        if mc_al.actual.cat == '!)':
            mc_al.avanza()
        else:
            mc_error('<Tinta>', ['!)'])
        Tinta.color= cadena.cad
if __name__=='__main__':
    try:
        mc_main = main
    except NameError:
        def mc_main():
            AnalizadorSintactico(sys.stdin)
    mc_main()