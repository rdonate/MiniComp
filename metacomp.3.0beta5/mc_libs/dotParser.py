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
            if q < 13:
                if q < 6:
                    if q < 3:
                        if q < 1:
                            if u'\t' <= c <= u'\n' or c == u' ':
                                q = 8
                            elif c == u',':
                                q = 6
                            elif c == u'"':
                                q = 2
                            elif c == u'=':
                                q = 4
                            elif c == u'}':
                                q = 11
                            elif c == u'/':
                                q = 7
                            elif c == u']':
                                q = 3
                            elif c == u';':
                                q = 12
                            elif c == u'-':
                                q = 5
                            elif not (u'\t' <= c <= u'\n' or c == u' ' or c == u'"' or u',' <= c <= u'-' or u'/' <= c <= u'9' or c == u';' or u'=' <= c <= u'>' or c == u'[' or c == u']' or c == u'{' or c == u'}'):
                                q = 13
                            elif c == u'[':
                                q = 9
                            elif c == u'{':
                                q = 10
                            elif u'0' <= c <= u'9':
                                q = 1
                            else:
                                break
                        else:
                            if q < 2:
                                uf = (u'number', processNumber)
                                ufi = i
                                if not (u'\t' <= c <= u'\n' or c == u' ' or c == u'"' or u',' <= c <= u'-' or u'0' <= c <= u'9' or c == u';' or u'=' <= c <= u'>' or c == u'[' or c == u']'):
                                    q = 13
                                elif u'0' <= c <= u'9':
                                    q = 1
                                else:
                                    break
                            else:
                                if c == u'"':
                                    q = 18
                                elif c == u'\\':
                                    q = 17
                                elif not (c == u'\n' or c == u'"' or c == u'\\'):
                                    q = 2
                                else:
                                    break
                    else:
                        if q < 4:
                            uf = (u'!]', None)
                            ufi = i
                            break
                        else:
                            if q < 5:
                                uf = (u'!=', None)
                                ufi = i
                                break
                            else:
                                if c == u'>':
                                    q = 14
                                else:
                                    break
                else:
                    if q < 9:
                        if q < 7:
                            uf = (u'!,', None)
                            ufi = i
                            break
                        else:
                            if q < 8:
                                uf = (u'id', processID)
                                ufi = i
                                if c == u'*':
                                    q = 15
                                elif not (u'\t' <= c <= u'\n' or c == u' ' or c == u'"' or c == u'*' or u',' <= c <= u'-' or c == u'/' or c == u';' or u'=' <= c <= u'>' or c == u'[' or c == u']'):
                                    q = 13
                                elif c == u'/':
                                    q = 16
                                else:
                                    break
                            else:
                                uf = (None, None)
                                ufi = i
                                if u'\t' <= c <= u'\n' or c == u' ':
                                    q = 8
                                else:
                                    break
                    else:
                        if q < 11:
                            if q < 10:
                                uf = (u'![', None)
                                ufi = i
                                break
                            else:
                                uf = (u'!{', None)
                                ufi = i
                                if not (u'\t' <= c <= u'\n' or c == u' ' or c == u'"' or u',' <= c <= u'-' or c == u';' or u'=' <= c <= u'>' or c == u'[' or c == u']'):
                                    q = 13
                                else:
                                    break
                        else:
                            if q < 12:
                                uf = (u'!}', None)
                                ufi = i
                                if not (u'\t' <= c <= u'\n' or c == u' ' or c == u'"' or u',' <= c <= u'-' or c == u';' or u'=' <= c <= u'>' or c == u'[' or c == u']'):
                                    q = 13
                                else:
                                    break
                            else:
                                uf = (u'!;', None)
                                ufi = i
                                break
            else:
                if q < 19:
                    if q < 16:
                        if q < 14:
                            uf = (u'id', processID)
                            ufi = i
                            if not (u'\t' <= c <= u'\n' or c == u' ' or c == u'"' or u',' <= c <= u'-' or c == u';' or u'=' <= c <= u'>' or c == u'[' or c == u']'):
                                q = 13
                            else:
                                break
                        else:
                            if q < 15:
                                uf = (u'!->', None)
                                ufi = i
                                break
                            else:
                                uf = (u'id', processID)
                                ufi = i
                                if u'\t' <= c <= u'\n' or c == u' ' or c == u'"' or u',' <= c <= u'-' or c == u';' or u'=' <= c <= u'>' or c == u'[' or c == u']':
                                    q = 20
                                elif c == u'*':
                                    q = 19
                                elif not (u'\t' <= c <= u'\n' or c == u' ' or c == u'"' or c == u'*' or u',' <= c <= u'-' or c == u';' or u'=' <= c <= u'>' or c == u'[' or c == u']'):
                                    q = 15
                                else:
                                    break
                    else:
                        if q < 17:
                            uf = (u'id', processID)
                            ufi = i
                            if c == '\n':
                                q = 21
                            elif not (u'\t' <= c <= u'\n' or c == u' ' or c == u'"' or u',' <= c <= u'-' or c == u';' or u'=' <= c <= u'>' or c == u'[' or c == u']'):
                                q = 16
                            elif c == u'\t' or c == u' ' or c == u'"' or u',' <= c <= u'-' or c == u';' or u'=' <= c <= u'>' or c == u'[' or c == u']':
                                q = 22
                            else:
                                break
                        else:
                            if q < 18:
                                if c == u'\n' or c == u'"' or c == u'G' or c == u'L' or c == u'N' or c == u'\\' or c == u'l' or c == u'n' or c == u'r':
                                    q = 2
                                else:
                                    break
                            else:
                                uf = (u'string', processString)
                                ufi = i
                                break
                else:
                    if q < 22:
                        if q < 20:
                            uf = (u'id', processID)
                            ufi = i
                            if u'\t' <= c <= u'\n' or c == u' ' or c == u'"' or u',' <= c <= u'-' or c == u';' or u'=' <= c <= u'>' or c == u'[' or c == u']':
                                q = 20
                            elif c == u'/':
                                q = 24
                            elif not (u'\t' <= c <= u'\n' or c == u' ' or c == u'"' or c == u'*' or u',' <= c <= u'-' or c == u'/' or c == u';' or u'=' <= c <= u'>' or c == u'[' or c == u']'):
                                q = 15
                            elif c == u'*':
                                q = 19
                            else:
                                break
                        else:
                            if q < 21:
                                if c == u'*':
                                    q = 23
                                elif c != u'*':
                                    q = 20
                                else:
                                    break
                            else:
                                uf = (None, None)
                                ufi = i
                                break
                    else:
                        if q < 24:
                            if q < 23:
                                if c != u'\n':
                                    q = 22
                                elif c == '\n':
                                    q = 21
                                else:
                                    break
                            else:
                                if not (c == u'*' or c == u'/'):
                                    q = 20
                                elif c == u'/':
                                    q = 25
                                elif c == u'*':
                                    q = 23
                                else:
                                    break
                        else:
                            if q < 25:
                                uf = (None, None)
                                ufi = i
                                if not (u'\t' <= c <= u'\n' or c == u' ' or c == u'"' or u',' <= c <= u'-' or c == u';' or u'=' <= c <= u'>' or c == u'[' or c == u']'):
                                    q = 13
                                else:
                                    break
                            else:
                                uf = (None, None)
                                ufi = i
                                break
            i+=1
        return (uf, ufi)
# Código de usuario
reserved = set(["digraph", "edge", "graph", "node", "strict"])
inContext = set()
acceptable = set()
def changeContext(s):
    global inContext
    inContext = s
def changeAcceptable(s):
	global acceptable
	acceptable = s
graphContext = set(["bb", "size", "page", "ratio", "layout", "margin", "nodesep", "ranksep",
                    "ordering", "rankdir", "pagedir", "rank", "rotate", "center",
                    "nslimit", "mclimit", "layers", "color", "bgcolor", "href", "URL",
                    "stylesheet", "splines"])
nodeContext = set(["height", "width", "fixedsize", "shape", "label", "fontsize", "fontname",
                   "color", "fillcolor", "fontcolor", "style", "layer", "regular", "peripheries",
                   "sides", "orientation", "distortion", "skew", "href", "URL", "target", "pos",
                   "tooltip"])
edgeContext = set(["minlen", "weight", "label", "fontsize", "fontname", "fontcolor", "style",
                   "color", "dir", "tailclip", "headclip", "href", "URL", "target", "tooltip",
                   "arrowhead", "arrowtail", "arrowsize", "headlabel", "taillabel", "headhref",
                   "headURL", "headtarget", "headtooltip", "tailhref", "tailURL", "tailtarget",
                   "tailtooltip", "labeldistance", "samehead", "sametail", "constraint", "layer",
                   "pos", "lp"
                   ])
def processID(c):
    if c.lexema in reserved or c.lexema in inContext or c.lexema in acceptable:
        c.cat = c.lexema
def processString(c):
    v = ""
    esc = False
    for f in c.lexema[1:-1]:
        if esc:
            if f == "n":
            	v += "\n"
            elif f == "\n":
            	pass
            elif f in "NGLlr":
                v += "\\" + f
            else:
            	v += f
            esc = False
        elif f == "\\":
        	esc = True
        else:
            v += f
    c.v = v
def processNumber(c):
    c.v = int(c.lexema)
mc_primeros = {
    '<Attributes>' : [u'!['],
    '<Content>' : [u'node', u'graph', u'edge', u'id', u'number'],
    '<Graph>' : [u'digraph'],
    '<IdOrNumber>' : [u'id', u'number'],
    '<IdOrString>' : [u'id', u'string'],
    '<IdStringOrNumber>' : [u'id', u'string', u'number'],
    '<Pair>' : [u'rankdir', u'rotate', u'bb', u'pos', u'height', u'width', u'shape', u'label', u'lp', u'peripheries', u'size'],
    '<StringOrNumber>' : [u'number', u'string'],
}
mc_siguientes = {
    '<Attributes>' : [u'!;'],
    '<Content>' : [u'node', u'edge', u'graph', u'!}', u'number', u'id'],
    '<Graph>' : ['mc_EOF'],
    '<IdOrNumber>' : [u'![', u'!->'],
    '<IdOrString>' : [],
    '<IdStringOrNumber>' : [u'!]', u'!,'],
    '<Pair>' : [u'!]', u'!,'],
    '<StringOrNumber>' : [u'!]', u'!,'],
}
mc_aceptables = {
    '<Attributes>' : [u'!['],
    '<Content>' : [u'node', u'graph', u'edge', u'id', u'number'],
    '<Graph>' : [u'digraph'],
    '<IdOrNumber>' : [u'id', u'number'],
    '<IdOrString>' : [u'id', u'string'],
    '<IdStringOrNumber>' : [u'number', u'id', u'string'],
    '<Pair>' : [u'rankdir', u'rotate', u'bb', u'pos', u'height', u'peripheries', u'width', u'shape', u'lp', u'label', u'size'],
    '<StringOrNumber>' : [u'number', u'string'],
}
mc_anulables = {
    '<Attributes>' : False,
    '<Content>' : False,
    '<Graph>' : False,
    '<IdOrNumber>' : False,
    '<IdOrString>' : False,
    '<IdStringOrNumber>' : False,
    '<Pair>' : False,
    '<StringOrNumber>' : False,
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
            self.Graph = Atributos()
            try:
                self.mc_analiza_Graph(self.Graph)
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
    def mc_analiza_Attributes(self, Attributes):
        mc_al= self.mc_al
        if not mc_al.actual.cat== '![':
            mc_error('<Attributes>', [ '![' ])
        Pair= Pair1= Atributos()
        Pair2= Atributos()
        mc_al.avanza()
        self.mc_analiza_Pair(Pair1)
        Pair_= Pair1
        Attributes.d[Pair.type] = Pair.value
        while mc_al.actual.cat== '!,':
            mc_al.avanza()
            self.mc_analiza_Pair(Pair2)
            Pair_= Pair2
            Attributes.d[Pair_.type] = Pair_.value
        if not mc_al.actual.cat== '!]':
            mc_error('<Attributes>',[ '!,', '!]' ])
        if mc_al.actual.cat == '!]':
            mc_al.avanza()
        else:
            mc_error('<Attributes>', ['!]'])
    def mc_analiza_Content(self, Content):
        mc_al= self.mc_al
        if not mc_al.actual.cat in [ 'edge', 'graph', 'id', 'node', 'number' ]:
            mc_error('<Content>', [ 'edge', 'graph', 'id', 'node', 'number' ])
        if mc_al.actual.cat== 'graph':
            Attributes= Attributes1= Atributos()
            graph = graph1 = graph_ = mc_al.actual
            mc_al.avanza()
            changeContext(graphContext)
            Attributes.d = Content.graphAttributes
            self.mc_analiza_Attributes(Attributes1)
            Attributes_= Attributes1
            if mc_al.actual.cat == '!;':
                mc_al.avanza()
            else:
                mc_error('<Content>', ['!;'])
        elif mc_al.actual.cat== 'edge':
            Attributes= Attributes1= Atributos()
            edge = edge1 = edge_ = mc_al.actual
            mc_al.avanza()
            changeContext(edgeContext)
            Attributes.d = Content.edgeAttributes
            self.mc_analiza_Attributes(Attributes1)
            Attributes_= Attributes1
            if mc_al.actual.cat == '!;':
                mc_al.avanza()
            else:
                mc_error('<Content>', ['!;'])
        elif mc_al.actual.cat== 'node':
            Attributes= Attributes1= Atributos()
            node = node1 = node_ = mc_al.actual
            mc_al.avanza()
            changeContext(nodeContext)
            Attributes.d = Content.nodeAttributes
            self.mc_analiza_Attributes(Attributes1)
            Attributes_= Attributes1
            if mc_al.actual.cat == '!;':
                mc_al.avanza()
            else:
                mc_error('<Content>', ['!;'])
        else:
            IdOrNumber= IdOrNumber1= Atributos()
            IdOrNumber2= Atributos()
            Attributes= Attributes1= Atributos()
            self.mc_analiza_IdOrNumber(IdOrNumber1)
            IdOrNumber_= IdOrNumber1
            Attributes.d = {}
            if mc_al.actual.cat== '!->':
                mc_al.avanza()
                self.mc_analiza_IdOrNumber(IdOrNumber2)
                IdOrNumber_= IdOrNumber2
                changeContext(edgeContext)
                Content.edges.append((IdOrNumber1.lex, IdOrNumber2.lex, Attributes.d))
            elif mc_al.actual.cat== '![':
                changeContext(nodeContext)
                Content.nodes.append((IdOrNumber1.lex, Attributes.d))
            else:
                mc_error('<Content>', [ '!->', '![' ])
            self.mc_analiza_Attributes(Attributes1)
            Attributes_= Attributes1
            if mc_al.actual.cat == '!;':
                mc_al.avanza()
            else:
                mc_error('<Content>', ['!;'])
    def mc_analiza_Graph(self, Graph):
        mc_al= self.mc_al
        if not mc_al.actual.cat== 'digraph':
            mc_error('<Graph>', [ 'digraph' ])
        Content= Content1= Atributos()
        Graph.graphAttributes = {}
        Graph.edgeAttributes = {}
        Graph.nodeAttributes = {}
        Graph.edges = []
        Graph.nodes = []
        digraph = digraph1 = digraph_ = mc_al.actual
        mc_al.avanza()
        if mc_al.actual.cat == 'id':
            id = id1 = id_ = mc_al.actual
            mc_al.avanza()
        else:
            mc_error('<Graph>', ['id'])
        if mc_al.actual.cat == '!{':
            mc_al.avanza()
        else:
            mc_error('<Graph>', ['!{'])
        while mc_al.actual.cat in [ 'edge', 'graph', 'id', 'node', 'number' ]:
            Content.graphAttributes = Graph.graphAttributes
            Content.edgeAttributes = Graph.edgeAttributes
            Content.nodeAttributes = Graph.nodeAttributes
            Content.edges = Graph.edges
            Content.nodes = Graph.nodes
            self.mc_analiza_Content(Content1)
            Content_= Content1
        if not mc_al.actual.cat== '!}':
            mc_error('<Graph>',[ '!}', 'edge', 'graph', 'id', 'node', 'number' ])
        if mc_al.actual.cat == '!}':
            mc_al.avanza()
        else:
            mc_error('<Graph>', ['!}'])
    def mc_analiza_IdOrNumber(self, IdOrNumber):
        mc_al= self.mc_al
        if not mc_al.actual.cat in [ 'id', 'number' ]:
            mc_error('<IdOrNumber>', [ 'id', 'number' ])
        if mc_al.actual.cat== 'id':
            id = id1 = id_ = mc_al.actual
            mc_al.avanza()
            IdOrNumber.lex = id.lexema
        else:
            number = number1 = number_ = mc_al.actual
            mc_al.avanza()
            IdOrNumber.lex = number.lexema
    def mc_analiza_IdOrString(self, IdOrString):
        mc_al= self.mc_al
        if not mc_al.actual.cat in [ 'id', 'string' ]:
            mc_error('<IdOrString>', [ 'id', 'string' ])
        if mc_al.actual.cat== 'id':
            id = id1 = id_ = mc_al.actual
            mc_al.avanza()
            IdOrString.v = id.lexema
        else:
            string = string1 = string_ = mc_al.actual
            mc_al.avanza()
            IdOrString.v = string.v
    def mc_analiza_IdStringOrNumber(self, IdStringOrNumber):
        mc_al= self.mc_al
        if not mc_al.actual.cat in [ 'id', 'number', 'string' ]:
            mc_error('<IdStringOrNumber>', [ 'id', 'number', 'string' ])
        if mc_al.actual.cat== 'id':
            id = id1 = id_ = mc_al.actual
            mc_al.avanza()
            IdStringOrNumber.v = id.lexema
        elif mc_al.actual.cat== 'number':
            number = number1 = number_ = mc_al.actual
            mc_al.avanza()
            IdStringOrNumber.v = number.lexema
        else:
            string = string1 = string_ = mc_al.actual
            mc_al.avanza()
            IdStringOrNumber.v = string.v
    def mc_analiza_Pair(self, Pair):
        mc_al= self.mc_al
        if not mc_al.actual.cat in [ 'bb', 'height', 'label', 'lp', 'peripheries', 'pos', 'rankdir', 'rotate', 'shape', 'size', 'width' ]:
            mc_error('<Pair>', [ 'bb', 'height', 'label', 'lp', 'peripheries', 'pos', 'rankdir', 'rotate', 'shape', 'size', 'width' ])
        if mc_al.actual.cat== 'bb':
            bb = bb1 = bb_ = mc_al.actual
            mc_al.avanza()
            if mc_al.actual.cat == '!=':
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['!='])
            if mc_al.actual.cat == 'string':
                string = string1 = string_ = mc_al.actual
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['string'])
            Pair.type = "bb"; Pair.value = string.v
        elif mc_al.actual.cat== 'height':
            StringOrNumber= StringOrNumber1= Atributos()
            height = height1 = height_ = mc_al.actual
            mc_al.avanza()
            if mc_al.actual.cat == '!=':
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['!='])
            self.mc_analiza_StringOrNumber(StringOrNumber1)
            StringOrNumber_= StringOrNumber1
            Pair.type = "height"; Pair.value = StringOrNumber.v
        elif mc_al.actual.cat== 'label':
            IdStringOrNumber= IdStringOrNumber1= Atributos()
            label = label1 = label_ = mc_al.actual
            mc_al.avanza()
            if mc_al.actual.cat == '!=':
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['!='])
            self.mc_analiza_IdStringOrNumber(IdStringOrNumber1)
            IdStringOrNumber_= IdStringOrNumber1
            Pair.type = "label"; Pair.value = IdStringOrNumber.v
        elif mc_al.actual.cat== 'lp':
            lp = lp1 = lp_ = mc_al.actual
            mc_al.avanza()
            if mc_al.actual.cat == '!=':
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['!='])
            if mc_al.actual.cat == 'string':
                string = string1 = string_ = mc_al.actual
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['string'])
            Pair.type = "lp"; Pair.value = string.v
        elif mc_al.actual.cat== 'peripheries':
            peripheries = peripheries1 = peripheries_ = mc_al.actual
            mc_al.avanza()
            if mc_al.actual.cat == '!=':
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['!='])
            if mc_al.actual.cat == 'number':
                number = number1 = number_ = mc_al.actual
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['number'])
            Pair.type = "peripheries"; Pair.value = number.v
        elif mc_al.actual.cat== 'pos':
            pos = pos1 = pos_ = mc_al.actual
            mc_al.avanza()
            if mc_al.actual.cat == '!=':
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['!='])
            if mc_al.actual.cat == 'string':
                string = string1 = string_ = mc_al.actual
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['string'])
            Pair.type = "pos"; Pair.value = string.v
        elif mc_al.actual.cat== 'size':
            size = size1 = size_ = mc_al.actual
            mc_al.avanza()
            if mc_al.actual.cat == '!=':
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['!='])
            if mc_al.actual.cat == 'string':
                string = string1 = string_ = mc_al.actual
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['string'])
            Pair.type = "size"; Pair.value = string.v
        elif mc_al.actual.cat== 'rankdir':
            rankdir = rankdir1 = rankdir_ = mc_al.actual
            mc_al.avanza()
            changeAcceptable(set(["LR","RL","BT"]))
            if mc_al.actual.cat == '!=':
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['!='])
            if mc_al.actual.cat== 'LR':
                LR = LR1 = LR_ = mc_al.actual
                mc_al.avanza()
                Pair.value = "LR"
            elif mc_al.actual.cat== 'RL':
                RL = RL1 = RL_ = mc_al.actual
                mc_al.avanza()
                Pair.value = "RL"
            elif mc_al.actual.cat== 'BT':
                BT = BT1 = BT_ = mc_al.actual
                mc_al.avanza()
                Pair.value = "BT"
            else:
                mc_error('<Pair>', [ 'BT', 'LR', 'RL' ])
            Pair.type = "rankdir"
            changeAcceptable(set())
        elif mc_al.actual.cat== 'rotate':
            rotate = rotate1 = rotate_ = mc_al.actual
            mc_al.avanza()
            if mc_al.actual.cat == '!=':
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['!='])
            if mc_al.actual.cat == 'number':
                number = number1 = number_ = mc_al.actual
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['number'])
            Pair.type = "rotate"; Pair.value = number.v
        elif mc_al.actual.cat== 'shape':
            shape = shape1 = shape_ = mc_al.actual
            mc_al.avanza()
            changeAcceptable(set(["ellipse", "plaintext"]))
            if mc_al.actual.cat == '!=':
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['!='])
            if mc_al.actual.cat== 'ellipse':
                ellipse = ellipse1 = ellipse_ = mc_al.actual
                mc_al.avanza()
                Pair.value = "ellipse"
            elif mc_al.actual.cat== 'plaintext':
                plaintext = plaintext1 = plaintext_ = mc_al.actual
                mc_al.avanza()
                Pair.value = "plaintext"
            else:
                mc_error('<Pair>', [ 'ellipse', 'plaintext' ])
            Pair.type = "shape"
            changeAcceptable(set())
        else:
            StringOrNumber= StringOrNumber1= Atributos()
            width = width1 = width_ = mc_al.actual
            mc_al.avanza()
            if mc_al.actual.cat == '!=':
                mc_al.avanza()
            else:
                mc_error('<Pair>', ['!='])
            self.mc_analiza_StringOrNumber(StringOrNumber1)
            StringOrNumber_= StringOrNumber1
            Pair.type = "width"; Pair.value = StringOrNumber.v
    def mc_analiza_StringOrNumber(self, StringOrNumber):
        mc_al= self.mc_al
        if not mc_al.actual.cat in [ 'number', 'string' ]:
            mc_error('<StringOrNumber>', [ 'number', 'string' ])
        if mc_al.actual.cat== 'number':
            number = number1 = number_ = mc_al.actual
            mc_al.avanza()
            StringOrNumber.v = float(number.v)
        else:
            string = string1 = string_ = mc_al.actual
            mc_al.avanza()
            StringOrNumber.v = float(string.v)
if __name__=='__main__':
    try:
        mc_main = main
    except NameError:
        def mc_main():
            AnalizadorSintactico(sys.stdin)
    mc_main()