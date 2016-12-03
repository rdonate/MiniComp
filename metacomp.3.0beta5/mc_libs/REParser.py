#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Este código ha sido generado por metacomp, versión 3.0beta5
import sys
class mc_error_sintaxis(Exception): pass
class mc_error_noEOF(Exception): pass
class mc_error_abandonar(Exception): pass
def mc_error(nt, esp):
    raise mc_error_sintaxis, (nt, esp)
def mc_abandonar():
    raise mc_error_abandonar
def mc_pretty_cat(cat):
    if cat is None or cat[0]!='!':
        return cat
    else:
        return '"%s"' % cat[1:]
class ComponenteLexico:
    def __init__(self, cat, lexema, nlinea):
        self.cat = cat
        self.lexema = lexema
        self.nlinea = nlinea
    def __str__(self):
        s = ['%s: %s' % (repr(k), repr(v)) for k, v in self.__dict__.items() if k != 'cat']
        if s:
            return '%s (%s)' % (mc_pretty_cat(self.cat), ', '.join(s))
        else:
            return mc_pretty_cat(self.cat)
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
            self.l = ''.join(ll)
            entrada.close()
        self.nlactual = 1
        self.actual = ComponenteLexico(None, None, 0)
        try:
            self.error_lexico = error_lexico
        except NameError:
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
            if q < 14:
                if q < 7:
                    if q < 3:
                        if q < 1:
                            if c < u'/':
                                if c < u')':
                                    if c < u'\x0b':
                                        if c < '\n':
                                            q = 9
                                        else:
                                            q = 8
                                    else:
                                        if c < u'(':
                                            q = 9
                                        else:
                                            q = 2
                                else:
                                    if c < u'+':
                                        if c < u'*':
                                            q = 1
                                        else:
                                            q = 4
                                    else:
                                        if c < u',':
                                            q = 7
                                        else:
                                            if c < u'.':
                                                q = 9
                                            else:
                                                q = 5
                            else:
                                if c < u'^':
                                    if c < u'@':
                                        if c < u'?':
                                            q = 9
                                        else:
                                            q = 11
                                    else:
                                        if c < u'[':
                                            q = 9
                                        else:
                                            if c < u'\\':
                                                q = 6
                                            else:
                                                if c <= u'\\':
                                                    q = 3
                                                else:
                                                    break
                                else:
                                    if c < u'}':
                                        if c < u'|':
                                            q = 9
                                        else:
                                            q = 12
                                    else:
                                        if c < u'\u03bb':
                                            q = 9
                                        else:
                                            if c < u'\u03bc':
                                                q = 10
                                            else:
                                                q = 9
                        else:
                            if q < 2:
                                uf = (u'!)', None)
                                ufi = i
                                break
                            else:
                                uf = (u'!(', None)
                                ufi = i
                                if u')' == c:
                                    q = 21
                                else:
                                    break
                    else:
                        if q < 5:
                            if q < 4:
                                if c < u'\x0b':
                                    if c <= u'\t':
                                        q = 19
                                    else:
                                        break
                                else:
                                    q = 19
                            else:
                                uf = (u'!*', None)
                                ufi = i
                                break
                        else:
                            if q < 6:
                                uf = (u'set', processDot)
                                ufi = i
                                break
                            else:
                                if c < u'\\':
                                    if c < u'-':
                                        if c < u'\x0b':
                                            if c <= u'\x08':
                                                q = 15
                                            else:
                                                break
                                        else:
                                            q = 15
                                    else:
                                        if c < u'.':
                                            q = 13
                                        else:
                                            q = 15
                                else:
                                    if c < u'^':
                                        if c < u']':
                                            q = 14
                                        else:
                                            q = 13
                                    else:
                                        if c < u'_':
                                            q = 16
                                        else:
                                            q = 15
                else:
                    if q < 10:
                        if q < 8:
                            uf = (u'!+', None)
                            ufi = i
                            break
                        else:
                            if q < 9:
                                uf = (None, None)
                                ufi = i
                                break
                            else:
                                uf = (u'sym', processSym)
                                ufi = i
                                break
                    else:
                        if q < 12:
                            if q < 11:
                                uf = (u'emptyString', None)
                                ufi = i
                                break
                            else:
                                uf = (u'!?', None)
                                ufi = i
                                break
                        else:
                            if q < 13:
                                uf = (u'!|', None)
                                ufi = i
                                break
                            else:
                                if c < u'\\':
                                    if c < u'\x0b':
                                        if c <= u'\x08':
                                            q = 15
                                        else:
                                            break
                                    else:
                                        if c < u'.':
                                            if c <= u',':
                                                q = 15
                                            else:
                                                break
                                        else:
                                            q = 15
                                else:
                                    if c < u']':
                                        q = 14
                                    else:
                                        if c < u'^':
                                            q = 20
                                        else:
                                            q = 15
            else:
                if q < 21:
                    if q < 17:
                        if q < 15:
                            if c < u'\x0b':
                                if c <= u'\x08':
                                    q = 15
                                else:
                                    break
                            else:
                                q = 15
                        else:
                            if q < 16:
                                if c < u'.':
                                    if c < u'\x0b':
                                        if c <= u'\x08':
                                            q = 15
                                        else:
                                            break
                                    else:
                                        if c < u'-':
                                            q = 15
                                        else:
                                            q = 25
                                else:
                                    if c < u']':
                                        if c < u'\\':
                                            q = 15
                                        else:
                                            q = 14
                                    else:
                                        if c < u'^':
                                            q = 24
                                        else:
                                            q = 15
                            else:
                                if c < u'.':
                                    if c < u'\x0b':
                                        if c <= u'\x08':
                                            q = 15
                                        else:
                                            break
                                    else:
                                        if c < u'-':
                                            q = 15
                                        else:
                                            q = 17
                                else:
                                    if c < u']':
                                        if c < u'\\':
                                            q = 15
                                        else:
                                            q = 14
                                    else:
                                        if c < u'^':
                                            q = 18
                                        else:
                                            q = 15
                    else:
                        if q < 19:
                            if q < 18:
                                if c < u'\\':
                                    if c < u'\x0b':
                                        if c <= u'\x08':
                                            q = 15
                                        else:
                                            break
                                    else:
                                        if c < u'.':
                                            if c <= u',':
                                                q = 15
                                            else:
                                                break
                                        else:
                                            q = 15
                                else:
                                    if c < u']':
                                        q = 22
                                    else:
                                        if c < u'^':
                                            q = 23
                                        else:
                                            q = 15
                            else:
                                uf = (u'set', processSet)
                                ufi = i
                                if c < u'\\':
                                    if c < u'\x0b':
                                        if c <= u'\x08':
                                            q = 15
                                        else:
                                            break
                                    else:
                                        if c < u'.':
                                            if c <= u',':
                                                q = 15
                                            else:
                                                break
                                        else:
                                            q = 15
                                else:
                                    if c < u']':
                                        q = 14
                                    else:
                                        if c < u'^':
                                            q = 20
                                        else:
                                            q = 15
                        else:
                            if q < 20:
                                uf = (u'sym', processEscape)
                                ufi = i
                                break
                            else:
                                uf = (u'set', processSet)
                                ufi = i
                                break
                else:
                    if q < 25:
                        if q < 23:
                            if q < 22:
                                uf = (u'emptyString', None)
                                ufi = i
                                break
                            else:
                                if c < u'\x0b':
                                    if c <= u'\x08':
                                        q = 15
                                    else:
                                        break
                                else:
                                    q = 15
                        else:
                            if q < 24:
                                uf = (u'set', processSet)
                                ufi = i
                                break
                            else:
                                uf = (u'set', processSet)
                                ufi = i
                                break
                    else:
                        if q < 27:
                            if q < 26:
                                if c < u'\\':
                                    if c < u'\x0b':
                                        if c <= u'\x08':
                                            q = 27
                                        else:
                                            break
                                    else:
                                        if c < u'.':
                                            if c <= u',':
                                                q = 27
                                            else:
                                                break
                                        else:
                                            q = 27
                                else:
                                    if c < u']':
                                        q = 26
                                    else:
                                        if c < u'^':
                                            q = 24
                                        else:
                                            q = 27
                            else:
                                if c < u'\x0b':
                                    if c <= u'\x08':
                                        q = 27
                                    else:
                                        break
                                else:
                                    q = 27
                        else:
                            if q < 28:
                                if c < u'.':
                                    if c < u'\x0b':
                                        if c <= u'\x08':
                                            q = 15
                                        else:
                                            break
                                    else:
                                        if c < u'-':
                                            q = 15
                                        else:
                                            q = 28
                                else:
                                    if c < u']':
                                        if c < u'\\':
                                            q = 15
                                        else:
                                            q = 14
                                    else:
                                        if c < u'^':
                                            q = 24
                                        else:
                                            q = 15
                            else:
                                if u']' == c:
                                    q = 24
                                else:
                                    break
            i += 1
        return (uf, ufi)
# Código de usuario
import erNodes
import charClass
def processCount(c):
  l = c.lexema[1:-1].split(",")
  if len(l) == 2:
    c.min = int(l[0])
    c.max = int(l[1])
  else:
    c.min = int(l[0])
    c.max = c.min
def processEscape(c):
  if c.lexema not in [r"\n", r"\t"]:
    c.value= c.lexema[1:]
  elif c.lexema== r"\n":
    c.value = "\n"
  elif c.lexema== r"\t":
    c.value = "\t"
def processSym(c):
  c.value= c.lexema
def processDot(cl):
  cl.charClass = charClass.full
def processSet(cl):
  s= cl.lexema[1:-1]
  if s[0]== u"^":
    i= 1
  else:
    i= 0
  l= []
  while i< len(s):
    if s[i] == u"\\":
      if s[i+1] == u"n":
        l.append((u"\n", u"\n"))
      elif s[i+1] == "t":
        l.append((u"\t", u"\t"))
      else:
        l.append((s[i+1], s[i+1]))
      i+= 2
    elif i< len(s)-2 and s[i+1]== u'-':
      l.append((s[i], s[i+2]))
      i+= 3
    else:
      l.append((s[i], s[i]))
      i+= 1
  cl.charClass = charClass.CharClass(s[0]!= u"^", l)
##  print cl.charClass
def error_lexico(nlinea, c):
  mc_abandonar()
def reParse(s):
  return AnalizadorSintactico(s).RE.exp
__needEscape = set(["\\", "(", ")", "[", "]", "+", "*", "|", "?", ".", "λ"])
def escapeChar(c):
  if c in __needEscape:
    return "\\" + c
  else:
    return c
def stringAsRE(s):
  if s == "":
    return erNodes.EmptyString("λ")
  else:
    ers = [ erNodes.SymbolSet(charClass.CharClass(True, [(c,c)]), escapeChar(c)) for c in s ]
    return reduce(lambda x, y: erNodes.Concatenation(x,y), ers)
mc_primeros = {
    '<B>' : [u'!(', u'set', u'emptySet', u'sym', u'emptyString'],
    '<E>' : [u'!(', u'set', u'emptySet', u'sym', u'emptyString'],
    '<F>' : [u'!(', u'set', u'emptySet', u'sym', u'emptyString'],
    '<RE>' : [u'!(', u'set', u'emptySet', u'sym', u'emptyString'],
    '<T>' : [u'!(', u'set', u'emptySet', u'sym', u'emptyString'],
}
mc_siguientes = {
    '<B>' : [u'set', u'!)', u'!(', u'!+', u'!*', u'sym', u'emptyString', 'mc_EOF', u'emptySet', u'!|', u'!?'],
    '<E>' : [u'!)', 'mc_EOF'],
    '<F>' : [u'set', u'!)', u'!(', u'sym', u'emptyString', 'mc_EOF', u'emptySet', u'!|'],
    '<RE>' : ['mc_EOF'],
    '<T>' : ['mc_EOF', u'!)', u'!|'],
}
mc_aceptables = {
    '<B>' : [u'!(', u'set', u'emptySet', u'sym', u'emptyString'],
    '<E>' : [u'!(', u'set', u'emptySet', u'sym', u'emptyString'],
    '<F>' : [u'!(', u'set', u'emptySet', u'sym', u'emptyString'],
    '<RE>' : [u'!(', u'set', u'emptySet', u'sym', u'emptyString'],
    '<T>' : [u'!(', u'set', u'emptySet', u'sym', u'emptyString'],
}
mc_anulables = {
    '<B>' : False,
    '<E>' : False,
    '<F>' : False,
    '<RE>' : False,
    '<T>' : False,
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
            self.RE = Atributos()
            try:
                self.mc_analiza_RE(self.RE)
                if self.mc_al.actual.cat != 'mc_EOF':
                    raise mc_error_noEOF
            except mc_error_sintaxis, (nt, esp):
                sys.stderr.write('Error no tratado en línea %d:\n' % self.mc_al.actual.nlinea)
                sys.stderr.write((u'Estaba analizando la expansión del no terminal %s y he encontrado\n el terminal %s.\n' % (nt, self.mc_al.actual)).encode('utf-8'))
                if len(esp)==1:
                    sys.stderr.write((u'Sólo valía un %s.\n' % mc_pretty_cat(esp[0])).encode('utf-8'))
                else:
                    sys.stderr.write((u'Tendría que haber sido uno de los siguientes: %s.\n' % ','.join(map(mc_pretty_cat,esp))).encode('utf-8'))
                sys.exit(1)
            except mc_error_noEOF:
                mc_al = self.mc_al
                self.RE.exp= None
            except mc_error_abandonar:
                pass
    def mc_reintentar(self):
        self.mc_reintento[-1] = True
    def mc_analiza_B(self, B):
        mc_al = self.mc_al
        if not mc_al.actual.cat in [ u'!(', 'emptySet', 'emptyString', 'set', 'sym' ]:
            mc_error('<B>', [ u'!(', 'emptySet', 'emptyString', 'set', 'sym' ])
        E = E1 = Atributos()
        if mc_al.actual.cat == u'!(':
            mc_al.avanza()
            self.mc_analiza_E(E1)
            E_ = E1
            if mc_al.actual.cat == u'!)':
                mc_al.avanza()
            else:
                mc_error('<B>', [u'!)'])
            B.exp= E.exp
        elif mc_al.actual.cat == u'sym':
            sym = sym1 = sym_ = mc_al.actual
            mc_al.avanza()
            B.exp= erNodes.SymbolSet(charClass.CharClass(True, [(sym.value, sym.value)]), sym.lexema)
        elif mc_al.actual.cat == u'set':
            set = set1 = set_ = mc_al.actual
            mc_al.avanza()
            B.exp= erNodes.SymbolSet(set.charClass, set.lexema)
        elif mc_al.actual.cat == u'emptyString':
            emptyString = emptyString1 = emptyString_ = mc_al.actual
            mc_al.avanza()
            B.exp= erNodes.EmptyString(emptyString.lexema)
        else:
            emptySet = emptySet1 = emptySet_ = mc_al.actual
            mc_al.avanza()
            B.exp= erNodes.EmptySet(emptySet.lexema)
    def mc_analiza_E(self, E):
        mc_al = self.mc_al
        if not mc_al.actual.cat in [ u'!(', 'emptySet', 'emptyString', 'set', 'sym' ]:
            mc_error('<E>', [ u'!(', 'emptySet', 'emptyString', 'set', 'sym' ])
        T = T1 = Atributos()
        T2 = Atributos()
        self.mc_analiza_T(T1)
        T_ = T1
        l= [T.exp]
        while mc_al.actual.cat == u'!|':
            mc_al.avanza()
            self.mc_analiza_T(T2)
            T_ = T2
            l.append(T2.exp)
        if not mc_al.actual.cat in [ u'!)', 'mc_EOF' ]:
            mc_error('<E>',[ u'!)', '!|', 'mc_EOF' ])
        if len(l)== 1:
          E.exp= l[0]
        else:
          E.exp= erNodes.OrNode(l)
    def mc_analiza_F(self, F):
        mc_al = self.mc_al
        if not mc_al.actual.cat in [ u'!(', 'emptySet', 'emptyString', 'set', 'sym' ]:
            mc_error('<F>', [ u'!(', 'emptySet', 'emptyString', 'set', 'sym' ])
        B = B1 = Atributos()
        self.mc_analiza_B(B1)
        B_ = B1
        exp= B.exp
        while mc_al.actual.cat in [ u'!*', '!+', '!?' ]:
            if mc_al.actual.cat == u'!*':
                mc_al.avanza()
                exp= erNodes.Closure(exp, False)
            elif mc_al.actual.cat == u'!+':
                mc_al.avanza()
                exp= erNodes.Closure(exp, True)
            else:
                mc_al.avanza()
                exp= erNodes.Optional(exp)
        if not mc_al.actual.cat in [ u'!(', '!)', '!|', 'emptySet', 'emptyString', 'mc_EOF', 'set', 'sym' ]:
            mc_error('<F>',[ u'!(', '!)', '!*', '!+', '!?', '!|', 'emptySet', 'emptyString', 'mc_EOF', 'set', 'sym' ])
        F.exp= exp
    def mc_analiza_RE(self, RE):
        mc_al = self.mc_al
        self.mc_reintento.append(True)
        mc_reintentar= self.mc_reintentar
        while self.mc_reintento[-1]:
            self.mc_reintento[-1]= False
            try:
                if not mc_al.actual.cat in [ u'!(', 'emptySet', 'emptyString', 'set', 'sym' ]:
                    mc_error('<RE>', [ u'!(', 'emptySet', 'emptyString', 'set', 'sym' ])
                E = E1 = Atributos()
                RE.exp= None
                self.mc_analiza_E(E1)
                E_ = E1
                RE.exp= E.exp
            except mc_error_sintaxis, (mc_nt, mc_t):
                RE.exp= None
                mc_abandonar()
        self.mc_reintento.pop()
    def mc_analiza_T(self, T):
        mc_al = self.mc_al
        if not mc_al.actual.cat in [ u'!(', 'emptySet', 'emptyString', 'set', 'sym' ]:
            mc_error('<T>', [ u'!(', 'emptySet', 'emptyString', 'set', 'sym' ])
        F = F1 = Atributos()
        F2 = Atributos()
        self.mc_analiza_F(F1)
        F_ = F1
        exp= F.exp
        while mc_al.actual.cat in [ u'!(', 'emptySet', 'emptyString', 'set', 'sym' ]:
            self.mc_analiza_F(F2)
            F_ = F2
            exp= erNodes.Concatenation(exp, F2.exp)
        if not mc_al.actual.cat in [ u'!)', '!|', 'mc_EOF' ]:
            mc_error('<T>',[ u'!(', '!)', '!|', 'emptySet', 'emptyString', 'mc_EOF', 'set', 'sym' ])
        T.exp= exp
if __name__ == '__main__':
    try:
        mc_main = main
    except NameError:
        def mc_main():
            AnalizadorSintactico(sys.stdin)
    mc_main()