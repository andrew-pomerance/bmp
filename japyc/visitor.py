import ast
from .nodes import *

class JapycVisitor(ast.NodeVisitor):
    builtins = [
        '_jconst',
        '_jenum',
        '_jput64',
        '_jput32',
        '_jput16',
        '_jput8',
        '_jin8',
        '_jin16',
        '_jin32',
        '_jout8',
        '_jout16',
        '_jout32'
    ]
    
    def _visit_literal(self, node):
        retval = self.visit(node)
        assert isinstance(retval, JapycLiteral)
        return retval
    
    def builtin_jenum(self, node):
        # enums
        assert len(node.args) == 1
        assert isinstance(node.args[0], ast.Str)
        enum_name = node.args[0].s            
        enum_dict = {kw.arg: self._visit_literal(kw.value) for kw in node.keywords}  
        self.enums[enum_name] = enum_dict
        return None
    
    def builtin_jconst(self, node):
        assert len(node.args) == 0
        assert len(node.keywords) == 1
        self.consts[node.keywords[0].arg] = self._visit_literal(node.keywords[0].value)
        return None
    
    def builtin_jput64(self, node):
        return JapycPutInt(self.visit(node.args[0]), 
                           self.visit(node.args[1]), 64)
    
    def builtin_jput32(self, node):
        return JapycPutInt(self.visit(node.args[0]), 
                           self.visit(node.args[1]), 32)

    def builtin_jput16(self, node):
        return JapycPutInt(self.visit(node.args[0]), 
                           self.visit(node.args[1]), 16)

    def builtin_jput8(self, node):
        return JapycPutInt(self.visit(node.args[0]), 
                           self.visit(node.args[1]), 8)        
    
    def __init__(self):
        self.enums = {}
        self.consts = {}
        
    def _visit_with_remove(self, nodes):
        assert isinstance(nodes, list)
        res = []
        for n in nodes:
            tmp = self.visit(n)
            if tmp is not None:
                res.append(tmp)
        return res
        
    def visit_Module(self, node):
        return JapycModule(self._visit_with_remove(node.body))
    
    def visit_Name(self, node):
        if node.id in self.consts:
            return self.consts[node.id]
        else:
            return JapycVariable(node.id)
    
    def visit_FunctionDef(self, node):
        assert node.name not in self.builtins
        args = [JapycVariable(a.arg) for a in node.args.args]
        body = self._visit_with_remove(node.body)
        return JapycFunction(node.name, args, body)

    def visit_Expr(self, node):
        return self.visit(node.value)
    
    def visit_Call(self, node):
        assert isinstance(node.func, ast.Name)
        if node.func.id in self.builtins:
            return getattr(self, 'builtin'+node.func.id)(node) 
        else:
            return JapycFunctionCall(node.func.id, self._visit_with_remove(node.args))
        
    def visit_ClassDef(self, node):
        raise NotImplementedError()
            
    def visit_Attribute(self, node):
        assert isinstance(node.value, ast.Name)
        assert node.value.id in self.enums
        assert node.attr in self.enums[node.value.id]
        return self.enums[node.value.id][node.attr]
    
    def visit_Num(self, node):
        return JapycInteger(node.n)
    
    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        def _do_op(x, y):
            if isinstance(node.op, ast.Mult):
                return x*y
            elif isinstance(node.op, ast.Add):
                return x+y
            else:
                raise NotImplementedError()
        if isinstance(left, JapycInteger) and isinstance(right, JapycInteger):
            return JapycInteger(_do_op(left.value, right.value))
        else:
            return JapycBinOp(node.op, self.visit(node.left), self.visit(node.right))
        
    def visit_Str(self, node):
        assert len(node.s) == 1
        c = ord(node.s)
        assert c < 128
        return JapycInteger(c)
    
    def visit_Assign(self, node):
        assert len(node.targets) == 1
        assert isinstance(node.targets[0], ast.Name)
        return JapycSingleAssign(self.visit(node.targets[0]), self.visit(node.value)) 
        
    def generic_visit(self, node):
        raise NotImplementedError('Unimplemented node type: {}'.format(node.__class__.__name__))
