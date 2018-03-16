import ast
from .nodes import *

class JapycVisitor(ast.NodeVisitor):
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
        args = [JapycVariable(a.arg) for a in node.args.args]
        body = self._visit_with_remove(node.body)
        return JapycFunction(node.name, args, body)

    def visit_Expr(self, node):
        return self.visit(node.value)
    
    def visit_Call(self, node):
        assert isinstance(node.func, ast.Name)
        put_builtins = ('put_int64', 'put_int32', 'put_int16', 'put_int8')
        if node.func.id in put_builtins:
            bits = int(node.func.id[7:])
            memory_address = self.visit(node.args[0])
            value = self.visit(node.args[1])
            return JapycPutInt(memory_address, value, bits)
        elif node.func.id == 'const':
            assert len(node.keywords) == 1
            assert node.keywords[0].arg is not None
            val = self.visit(node.keywords[0].value)
            assert isinstance(val, JapycLiteral)          
            self.consts[node.keywords[0].arg] = val
            return None
        else:
            return JapycFunctionCall(node.func.id, self._visit_with_remove(node.args))
        
    def visit_ClassDef(self, node):
        assert len(node.bases) == 1
        if node.bases[0].id != 'Enum':
            raise NotImplementedError()
        enum_dict = {}
        for enum_node in node.body:
            # each node in an enum classdef body is an Assign node
            # if there are any shenanigans, go ahead and barf
            assert isinstance(enum_node, ast.Assign)
            assert len(enum_node.targets) == 1
            assert isinstance(enum_node.targets[0], ast.Name)
            val = self.visit(enum_node.value)
            assert isinstance(val, JapycLiteral)
            enum_dict[enum_node.targets[0].id] = val
        self.enums[node.name] = enum_dict
        return None
            
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
