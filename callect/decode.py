import os


from .base import Return, Commentaire, Prio

from .conditions import Not, Inf, Sup, InfOrEga, SupOrEga, Ega, In, RemIn, PopIn, And, Or, XAnd, XOr

from .operations import Rac, Exp, Mul, Div, Mod, Sub, Add

from .assignement import Asi, Typ, Local, IsExist

from .boucle import For, IFor, While, Repeat, Break

from .redirec import RedirecItem, RedirecPoint

from .errors import Try, Except, NotDefined

from .types.bloc import Bloc
from .types.bool import True__, False__
from .types.call import Call, Attachement
from .types.event import Event
from .types.inscond import InsCond
from .types.intervalle import Intervalle
from .types.nbr import Pos, Neg, Nul
from .types.objet import Objet
from .types.table import Table
from .types.txt import Txt
from .types.var import Var


class Ligne:

    def __init__(self, path_file):
        self.value = 1
        self.path_file = path_file

    def __call__(self):
        self.value += 1

    def __str__(self):
        return "[L~%s in file %s]" % (self.value, self.path_file)


class Conteneur:

    def __init__(self, value, last, ligne):

        self.value = value

        self.last = last

        self.ligne = ligne

    def push__(self, value):

        value.ligne__ = str(self.ligne)

        return Conteneur(value, self, self.ligne)

    def rem__(self):

        last = self.last

        ligne__ = self.value.ligne__

        self.value.end__(self)

        self.value.ligne__ = ligne__

        return last

    def action(self, objet, Act, acts, *, get_last=True, prio=False):

        cont = self

        cont, objet = end_objet(cont, objet)

        while isinstance(cont.value, acts):
            cont = cont.rem__()

        if not isinstance(cont.value, Act) or prio:
            act = Act()
            
            if get_last:
                act.push__(cont.value.pop__())

            cont.value.push__(act)
            cont = cont.push__(act)

            act.ligne__ = str(self.ligne)

        if get_last:
            cont.value.liée = True

        return None, cont

    def mise_a_niveau(self, acts):

        cont = self

        value_type = type(cont.value)

        while value_type in acts and not cont.value.liée:
            while not isinstance(cont.value, value_type):
                cont = cont.rem__()

            cont = cont.rem__()
            value_type = type(cont.value)

        cont.value.liée = False

        return cont

def action(cont, Act):

    if not isinstance(cont.value, Act):
        act = Act()
        act.push__(cont.value.pop__())

        act.ligne__ = str(cont.ligne)

        cont.value.push__(act)
        cont = cont.push__(act)

    return cont


def end_objet(cont, objet):

    if objet is None:
        return cont, objet


    objet.end__(cont)

    objet.ligne__ = str(cont.ligne)

    value = objet.value


    ### Condition

    if value == 'if':
        objet, cont = cont.action(None, InsCond, (), get_last=False)

    elif value == 'elif':
        objet, cont = cont.action(None, InsCond, ())

    elif value == 'else':
        objet, cont = cont.action(None, InsCond, ())
        cont.value.push__(True__)


    ### Boucle

    elif value == 'for':
        objet, cont = cont.action(None, For, (), get_last=False)

    elif value == 'ifor':
        objet, cont = cont.action(None, IFor, (), get_last=False)

    elif value == 'while':
        objet, cont = cont.action(None, While, (), get_last=False)

    elif value == 'repeat':
        objet, cont = cont.action(None, Repeat, (), get_last=False)

    elif value == 'break':
        cont.value.push__(Break())


    ### Var

    elif value == 'local':
        objet, cont = cont.action(None, Local, (), get_last=False)
        cont.value.liée = True

    elif value == 'return':
        objet, cont = cont.action(None, Return, (), get_last=False)
        cont.value.liée = True


    ### Cond

    elif value == 'in':
        if not isinstance(cont.value, (For, IFor)):
            objet, cont = cont.action(None, In, ())
        cont.value.push__(In)

    elif value == 'remin':
        objet, cont = cont.action(None, RemIn, ())
        cont.value.push__(In)

    elif value == 'popin':
        objet, cont = cont.action(None, PopIn, ())
        cont.value.push__(In)


    ### Essaies

    elif value == 'try':
        objet, cont = cont.action(None, Try, (), get_last=False)

    elif value == 'except':
        if isinstance(cont.value, Try):
            cont = cont.rem__()
        objet, cont = cont.action(None, Except, ())


    ### Autre

    else:
        cont.value.push__(objet)

    return cont, None


def decode(data, path_file):

    cont = Conteneur(Bloc(), None, Ligne(path_file))
    cont.value.liée = False

    objet = None


    acts_var = (Asi, Local, Return, IsExist)

    acts_redirec = (RedirecItem, RedirecPoint, Intervalle, Typ, Attachement)

    acts_calcul = (Rac, Exp, Mul, Div, Mod, Sub, Add)

    acts_condition = (Not, Inf, Sup, InfOrEga, SupOrEga, Ega, In, RemIn, PopIn)

    acts_condition_niv_sup = (And, Or, XAnd, XOr)


    index_min = 0

    echappement = False


    for icarac, carac in enumerate(data):

        #print(carac, type(cont.value), cont.value.value)

        carac2 = data[icarac:icarac+2]

        if icarac < index_min:
            continue


        if carac == '\n':
            cont.ligne()
            carac = ' '

        if carac == '\t':
            continue

        ### Commentaire

        if isinstance(objet, Commentaire):
            if carac2 == '//':
                index_min = icarac + 2
                objet = None

        elif carac2 == '//':
            index_min = icarac + 2
            objet = Commentaire()

        ### Echappement

        elif carac ==  '\\':
            if echappement:
                cont.value.push__('\\')
                echappement = False
            else:
                echappement = True

        elif echappement:

            if isinstance(objet, Txt):
                add = objet.push__

                if carac == 'n':
                    add('\n')

                elif carac == 't':
                    add('\t')

                elif carac == '"':
                    add('"')

                elif carac == "'":
                    add("'")

            else:
                add = cont.value.push__

                if carac == 'n':
                    add(Txt('\n'))

                elif carac == 't':
                    add(Txt('\t'))

            echappement = False


        ### Texte

        elif isinstance(objet, Txt):
            if ((carac == '"' and objet._symb == '"')
            or (carac == "'" and objet._symb == "'")):
                cont, objet = end_objet(cont, objet)
            else:
                objet.push__(carac)

        elif carac == '"' or carac == "'":
            cont, objet = end_objet(cont, objet)

            cont = cont.mise_a_niveau(acts_redirec + acts_var + acts_condition + acts_calcul)

            objet = Txt()
            objet._symb = carac


        ### Redirection

        elif carac == '.':

            if isinstance(objet, (Pos, Neg)):
                objet.push__('.')
                continue

            cont, objet = end_objet(cont, objet)

            cont = action(cont, RedirecPoint)

            cont.value.liée = True

        elif carac == '#':

            cont, objet = end_objet(cont, objet)

            if isinstance(cont.value, RedirecPoint):
                cont = cont.rem__()
                
            cont = action(cont, RedirecItem)

            cont.value.liée = True


        ### Attachement

        elif carac == '~':

            cont = cont.mise_a_niveau(acts_redirec)

            cont, objet = end_objet(cont, objet)

            objet, cont = cont.action(objet, Attachement, ())


        ### Intervalle

        elif carac == ';':

            cont, objet = end_objet(cont, objet)

            while isinstance(cont.value, ()):
                cont = cont.rem__()
                
            cont = action(cont, Intervalle)

            cont.value.liée = True


        ### Calcul
                
        elif carac == '+':

            cont, objet = end_objet(cont, objet)

            if not isinstance(cont.value.last__(), (RedirecPoint, RedirecItem, Var, Nul, Pos, Neg, Txt, Call)):
                cont.value.push__(Nul())

            objet, cont = cont.action(objet, Add, (Rac, Exp, Mul, Div, Mod, Sub, RedirecItem, RedirecPoint, Typ))

        elif carac == '-':

            cont, objet = end_objet(cont, objet)

            if not isinstance(cont.value.last__(), (RedirecPoint, RedirecItem, Var, Nul, Pos, Neg, Txt, Call)):
                cont.value.push__(Nul())

            objet, cont = cont.action(objet, Sub, (Rac, Exp, Mul, Div, Mod, Add, RedirecItem, RedirecPoint, Typ))
                
        elif carac == '/':

            objet, cont = cont.action(objet, Div, (Rac, Exp, Mod, Mul, RedirecItem, RedirecPoint, Typ))
                
        elif carac == '%':

            objet, cont = cont.action(objet, Mod, (Rac, Exp, Mul, Div, RedirecItem, RedirecPoint, Typ))

        elif carac == '*':

            objet, cont = cont.action(objet, Mul, (Rac, Exp, Mod, Div, RedirecItem, RedirecPoint, Typ))

        elif carac == '^':

            objet, cont = cont.action(objet, Exp, (Rac, RedirecItem, RedirecPoint, Typ))

        elif carac == 'V':

            objet, cont = cont.action(objet, Rac, (Exp, RedirecItem, RedirecPoint, Typ))


        ### Condition

        elif carac == '!':

            objet, cont = cont.action(objet, Not, (), get_last=False)

            cont.value.liée = True

        elif carac2 == '<=':
            index_min = icarac + 2

            objet, cont = cont.action(objet, InfOrEga, acts_redirec + acts_calcul + (IsExist, Not))

            cont.value.push__(InfOrEga)

        elif carac2 == '>=':
            index_min = icarac + 2

            objet, cont = cont.action(objet, SupOrEga, acts_redirec + acts_calcul + (IsExist, Not))

            cont.value.push__(SupOrEga)

        elif carac == '<':

            objet, cont = cont.action(objet, Inf, acts_redirec + acts_calcul + (IsExist, Not))

            cont.value.push__(Inf)

        elif carac == '>':

            objet, cont = cont.action(objet, Sup, acts_redirec + acts_calcul + (IsExist, Not))

            cont.value.push__(Sup)

        elif carac2 == '==':
            index_min = icarac + 2

            objet, cont = cont.action(objet, Ega, acts_redirec + acts_calcul + (IsExist, Not))

            cont.value.push__(Ega)

        elif carac == '&':

            objet, cont = cont.action(objet, And, acts_redirec + acts_calcul + acts_condition + (IsExist,))

        elif carac == '|':

            objet, cont = cont.action(objet, Or, acts_redirec + acts_calcul + acts_condition + (IsExist,))

        elif carac2 == '&&':
            index_min = icarac + 2

            objet, cont = cont.action(objet, XAnd, acts_redirec + acts_calcul + acts_condition + (IsExist,))

        elif carac2 == '||':
            index_min = icarac + 2

            objet, cont = cont.action(objet, XOr, acts_redirec + acts_calcul + acts_condition + (IsExist,))


        ### Variable

        elif carac == ':':

            objet, cont = cont.action(objet, Typ, acts_redirec)

        elif carac == '=':

            objet, cont = cont.action(objet, Asi, (Local, Return, Typ) + acts_redirec + acts_calcul)

            cont.value.push__(Asi)

        elif carac == '?':

            objet, cont = cont.action(objet, IsExist, acts_redirec)

            cont.value.push__(IsExist)


        ### Autre

        elif carac == '(':

            cont.value.liée = False

            objet, cont = cont.action(objet, Prio, (), get_last=False, prio=True)

        elif carac == ')':

            cont, objet = end_objet(cont, objet)

            while not isinstance(cont.value, Prio):
                cont = cont.rem__()

            cont = cont.rem__()

        elif carac == '[':

            objet, cont = cont.action(objet, Bloc, acts_condition_niv_sup + acts_calcul + acts_condition + acts_redirec, get_last=False, prio=True)

        elif carac == ']':

            cont, objet = end_objet(cont, objet)

            while not isinstance(cont.value, Bloc):
                cont = cont.rem__()

            cont = cont.rem__()

            # @pouet [a+b] ; § a == 2 [p = 1] ; if a < b [7/8]
            if isinstance(cont.value, (Objet, Event, InsCond, For, IFor, While, Repeat, Except)):
                cont = cont.rem__()

        elif carac == '{':

            cont, objet = end_objet(cont, objet)

            if isinstance(cont.value, Typ):
                # pouet:pos{}
                cont = cont.rem__()
                objet, cont = cont.action(objet, Call, (RedirecPoint,))

            elif not isinstance(cont.value, (Objet, IsExist)) and isinstance(cont.value.last__(), (Var, RedirecPoint, RedirecItem, Call, Prio)):
                # pouet{}
                # pouf.piaf{}
                # patate#134{}
                objet, cont = cont.action(objet, Call, (RedirecPoint,))

            else:
                cont = cont.mise_a_niveau(acts_redirec + acts_var + acts_calcul)

            objet, cont = cont.action(objet, Table, (), get_last=False, prio=True)

        elif carac == '}':

            cont, objet = end_objet(cont, objet)

            while not isinstance(cont.value, Table):
                cont = cont.rem__()

            cont = cont.rem__()

            # pouet{}
            if isinstance(cont.value, Call):
                cont = cont.rem__()


        ### Foncion

        elif carac == '@':

            cont = cont.mise_a_niveau(acts_redirec + acts_var + acts_condition + acts_calcul)

            cont, objet = end_objet(cont, objet)

            objet, cont = cont.action(objet, Objet, (), get_last=False)

            if isinstance(cont.last.value, Asi):
                value = cont.last.value.value[0]
                if isinstance(value, Var):
                    cont.value.push__(Txt(str(value)))


        ### Event

        elif carac == '$' or carac == '§':

            cont = cont.mise_a_niveau(acts_redirec + acts_var + acts_condition + acts_calcul)

            cont, objet = end_objet(cont, objet)
            
            while not isinstance(cont.value, Bloc):
                cont = cont.rem__()

            objet, cont = cont.action(objet, Event, (), get_last=False)



        ### Séparation

        elif carac == ',':
            pass


        ### Autre

        elif carac == ' ':

            if objet is None:
                continue

            cont, objet = end_objet(cont, objet)


        elif objet is not None:

            objet.push__(carac)

        else:

            cont = cont.mise_a_niveau(acts_redirec + acts_var + acts_condition + acts_calcul)

            if carac == '0':

                objet = Nul()
                objet.end__(cont)

            elif carac in list('123456789'):

                objet = Pos()
                objet.push__(carac)
            
            else:

                objet = Var()
                objet.push__(carac)


    if objet:
        objet.end__(cont)
        cont.value.push__(objet)
        objet = None

    while cont.last:
        cont = cont.rem__()

    cont.value.end__(cont)

    return cont.value