import ast

def JapycMeta(type):
    def __init__(cls, name, bases, dct):
        fields = dct['_fields']
        def __init__(self, *args):
            for field,value in zip(fields, args):
                setattr(self, field, value)
        def __str__(self):
            fields = [f+'='+str(getattr(self, f)) for f in fields].join(',')
            return self.__name__+'('+fields+')'
        dct['__init__'] = __init__
        dct['__str__'] = __str__
        return super(JapycMeta, cls).__init__(name, parents, dct)

class JapycAST(ast.AST):
    __metaclass__ = JapycMeta

class JapycModule(JapycAST):
    _fields = ['body']
    
class JapycFunction(JapycAST):
    _fields = ['name', 'args', 'body']
        
class JapycVariable(JapycAST):
    _fields = ['name']

class JapycPutInt(JapycAST):
    _fields = ['address', 'value', 'bits']
        
class JapycLiteral(JapycAST):
    _fields = ['value']

class JapycInteger(JapycLiteral):
    pass

class JapycChar(JapycLiteral):
    pass
        
class JapycBinOp(JapycAST):
    _fields = ['op', 'left', 'right']
        
class JapycFunctionCall(JapycAST):
    _fields = ['fn', 'args']
    
class JapycSingleAssign(JapycAST):
    _fields = ['var', 'value']
