##############################################################################
#
# re2ag 0.1: a visualizer for regular expressions and automata
# Copyright (C) 2010 Juan Miguel Vilar
#                    Universitat Jaume I, Castelló (Spain)
#
# This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Any questions regarding this software should be directed to:
#
#   Juan Miguel Vilar
#   Departament de Llenguatges i Sistemes Informàtics
#   Universitat Jaume I
#   E12071 Castellón (SPAIN)
#
#   email: jvilar@lsi.uji.es
#
###############################################################################
#
# Parser for (a subclass of) dot files
#

None	None	[ \n\t]+
None	None	/\*(/|\**[^/*])*\*+/
None	None	//[^\n]*\n
number	processNumber	[0-9]+
string	processString	"([^"\\\n]|\\[\n\\n"NGLlr])*"
# This way of identifying ids is a terrible hack to allow unicode letters.
# Dot does not use inverted commas when the string has only characters that
# unicode considers letters, but it is difficult at the moment to specify
# that set in metacomp.
id	processID	[^][=",>; \t\n-]+

%

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

%

<Graph> ->   @Graph.graphAttributes = {}@
			 @Graph.edgeAttributes = {}@
			 @Graph.nodeAttributes = {}@
			 @Graph.edges = []@
			 @Graph.nodes = []@
            digraph id "{"
             ( 
               @Content.graphAttributes = Graph.graphAttributes@
               @Content.edgeAttributes = Graph.edgeAttributes@
               @Content.nodeAttributes = Graph.nodeAttributes@
               @Content.edges = Graph.edges@
               @Content.nodes = Graph.nodes@
               <Content>
             )* "}" ;

<Content> -> graph
               @changeContext(graphContext)@
               @Attributes.d = Content.graphAttributes@
             <Attributes> ";" ;

<Content> -> edge
               @changeContext(edgeContext)@
               @Attributes.d = Content.edgeAttributes@
             <Attributes> ";" ;

<Content> -> node
               @changeContext(nodeContext)@
               @Attributes.d = Content.nodeAttributes@
             <Attributes> ";" ;

<Content> -> <IdOrNumber>
                 @Attributes.d = {}@
               (
                  "->" <IdOrNumber> 
                          @changeContext(edgeContext)@
                          @Content.edges.append((IdOrNumber1.lex, IdOrNumber2.lex, Attributes.d))@
               |
                          @changeContext(nodeContext)@
                          @Content.nodes.append((IdOrNumber1.lex, Attributes.d))@
               
               )
               <Attributes>
             ";" ;

<Attributes> -> "["
                   <Pair> @Attributes.d[Pair.type] = Pair.value@
                   ("," <Pair> @Attributes.d[Pair_.type] = Pair_.value@)*
               "]" ;

<Pair> -> bb "=" string @Pair.type = "bb"; Pair.value = string.v@ ;
<Pair> -> height "=" <StringOrNumber> @Pair.type = "height"; Pair.value = StringOrNumber.v@ ;
<Pair> -> label "=" <IdStringOrNumber> @Pair.type = "label"; Pair.value = IdStringOrNumber.v@ ;
<Pair> -> lp "=" string @Pair.type = "lp"; Pair.value = string.v@ ;
<Pair> -> peripheries "=" number @Pair.type = "peripheries"; Pair.value = number.v@ ;
<Pair> -> pos "=" string @Pair.type = "pos"; Pair.value = string.v@ ;
<Pair> -> size "=" string @Pair.type = "size"; Pair.value = string.v@ ;
<Pair> -> rankdir @changeAcceptable(set(["LR","RL","BT"]))@
          "="
            ( LR @Pair.value = "LR"@
            | RL @Pair.value = "RL"@
            | BT @Pair.value = "BT"@
            ) @Pair.type = "rankdir"@
              @changeAcceptable(set())@
          ;
<Pair> -> rotate "=" number @Pair.type = "rotate"; Pair.value = number.v@ ;
<Pair> -> shape @changeAcceptable(set(["ellipse", "plaintext"]))@
          "="
            ( ellipse @Pair.value = "ellipse"@
            | plaintext @Pair.value = "plaintext"@
            ) @Pair.type = "shape"@
              @changeAcceptable(set())@
          ;
<Pair> -> width "=" <StringOrNumber> @Pair.type = "width"; Pair.value = StringOrNumber.v@ ;

<IdOrNumber> -> id @IdOrNumber.lex = id.lexema@ ;
<IdOrNumber> -> number @IdOrNumber.lex = number.lexema@ ;

<IdOrString> -> id @IdOrString.v = id.lexema@ ;
<IdOrString> -> string @IdOrString.v = string.v@ ;

<IdStringOrNumber> -> id @IdStringOrNumber.v = id.lexema@ ;
<IdStringOrNumber> -> number @IdStringOrNumber.v = number.lexema@ ;
<IdStringOrNumber> -> string @IdStringOrNumber.v = string.v@ ;


<StringOrNumber> -> number @StringOrNumber.v = float(number.v)@ ;
<StringOrNumber> -> string @StringOrNumber.v = float(string.v)@ ;
