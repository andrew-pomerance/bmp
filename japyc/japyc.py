'''
 japyc - Just Another PYthon Compiler
(C) 2018 Andrew Pomerance
''' 

import ast
import pprint

def ast2tree(node, include_attrs=True):
    def _transform(node):
        if isinstance(node, ast.AST):
            fields = ((a, _transform(b))
                      for a, b in ast.iter_fields(node))
            if include_attrs:
                attrs = ((a, _transform(getattr(node, a)))
                         for a in node._attributes
                         if hasattr(node, a))
                return (node.__class__.__name__, dict(fields), dict(attrs))
            return (node.__class__.__name__, dict(fields))
        elif isinstance(node, list):
            return [_transform(x) for x in node]
        elif isinstance(node, str):
            return repr(node)
        return node
    if not isinstance(node, ast.AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    return _transform(node)

def pformat_ast(node, include_attrs=False, **kws):
    return pprint.pformat(ast2tree(node, include_attrs), **kws)

class CommandLineParser(object):
    def __init__(self, argv, *args, **kwargs):
        
        self.input_filename = argv[1]
        try:
            dasho_index = argv.index('-o')
            self.output_filename = argv[dasho_index+1]
        except ValueError:                  
            self.output_filename = self.input_filename.replace('.py', '.o')
        self.debug = '-debug' in argv
        
    def debug_print(self, s):
        if self.debug:
            print(s)

def print_help():
    print('help goes here as needed')
    
def JapycMeta(type):
    def __init__(cls, name, bases, dct):
        fields = dct['_fields']
        def __init__(self, *args):
            for field,value in zip(fields, args):
                setattr(self, field, value)
        dct['__init__'] = __init__
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
        
class JapycInteger(JapycAST):
    _fields = ['value']
        
class JapycChar(JapycAST):
    _fields = ['value']
        
class JapycBinOp(JapycAST):
    _fields = ['op', 'left', 'right']
        
class JapycFunctionCall(JapycAST):
    _fields = ['fn', 'args']

class JapycVisitor(ast.NodeVisitor):
    def __init__(self):
        self.enums = {}
        
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
        return JapycVariable(node.id)
    
    def visit_FunctionDef(self, node):
        args = [JapycVariable(a.arg) for a in node.args.args]
        body = self._visit_with_remove(node.body)
        return JapycFunction(node.name, args, body)

    def visit_Expr(self, node):
        return self.visit(node.value)
    
    def visit_Call(self, node):
        put_builtins = ('put_int64', 'put_int32', 'put_int16', 'put_int8')
        if node.func.id in put_builtins:
            bits = int(node.func.id[7:])
            memory_address = self.visit(node.args[0])
            value = self.visit(node.args[1])
            return JapycPutInt(memory_address, value, bits)
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
            assert isinstance(enum_node.value, ast.Num)
            enum_dict[enum_node.targets[0].id] = enum_node.value.n
        self.enums[node.name] = enum_dict
        return None
            
    def visit_Attribute(self, node):
        assert isinstance(node.value, ast.Name)
        assert node.value.id in self.enums
        assert node.attr in self.enums[node.value.id]
        return JapycInteger(self.enums[node.value.id][node.attr])
    
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
        if len(node.s) != 1:
            raise NotImplementedError('Only 1 char long strings, please')
        c = ord(node.s)
        if c > 127:
            raise NotImplementedError('Only ASCII characters for now')
        return JapycInteger(c)
        
    def generic_visit(self, node):
        raise NotImplementedError('Unimplemented node type: {}'.format(node.__class__.__name__))
        
from llvmlite import ir, binding
binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()  # yes, even this one


class LLVMEmitter(ast.NodeVisitor):
    def __init__(self, filename):
        super().__init__()
        self.builder = None
        self.filename = filename
        self.functions = {}
        
    def _recurse(self, node_list):
        if node_list:
            return [self.visit(child) for child in node_list]     
        else:
            return []   
                
        
    def visit_JapycModule(self, node):
        self.module = ir.Module(name=self.filename)        
        self._recurse(node.body)
        return self.module
        
    def visit_JapycFunction(self, node):
        # hard coded return value, hardcoded 64 bit integers
        function_type = ir.FunctionType(ir.VoidType(), [ir.IntType(64) for _ in node.args])  
        fn = ir.Function(self.module, function_type, name=node.name)
        block = fn.append_basic_block(name='entry')
        self.functions[node.name] = fn
        self.builder = ir.IRBuilder(block)
        # lookup table for function arguments
        self.function_arguments = {ast_arg.name: llvm_arg for ast_arg,llvm_arg in zip(node.args, fn.args)}
        
        self._recurse(node.body)
            
        self.builder.ret_void()
        
        
    def visit_JapycBinOp(self, node):
        a = self.visit(node.left)
        b = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return self.builder.add(a, b)
        elif isinstance(node.op, ast.Mult):
            return self.builder.mul(a, b)
        
    def visit_JapycInteger(self, node):
        return ir.Constant(ir.IntType(64), node.value)

    def visit_JapycVariable(self, node):
        if node.name in self.function_arguments:
            return self.function_arguments[node.name]
        else:
            raise NotImplementedError()
    
    def visit_JapycPutInt(self, node):        
        int_type = ir.IntType(node.bits)
        addr = self.builder.inttoptr(self.visit(node.address), int_type.as_pointer())
        value = self.visit(node.value)
        self.builder.store(value, addr)
        
    def visit_JapycFunctionCall(self, node):
        args = self._recurse(node.args)
        self.builder.call(self.functions[node.fn], args)
        
    def generic_visit(self, node):
        raise NotImplementedError('node type not implemented: {}'.format(node.__class__.__name__))        
        
def compile_ir(ir_module):
    """
    Compile the LLVM IR string with the given engine.
    The compiled module object is returned.
    """
    # Create a target machine representing the host
    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine()
    # And an execution engine with an empty backing module
    binding_module = binding.parse_assembly(str(ir_module))
    return target_machine.emit_object(binding_module)


def main(argv):
    try:
        opts = CommandLineParser(argv)
    except:
        print_help()
        exit()
        
    with open(opts.input_filename, 'r') as f:
        python_source = f.read()
        ast_root = ast.parse(python_source, filename=opts.input_filename)
                        
    
    opts.debug_print(pformat_ast(ast_root))
    japyc_root = JapycVisitor().visit(ast_root)
    opts.debug_print(pformat_ast(japyc_root))
    ir_module = LLVMEmitter(opts.input_filename).visit(japyc_root)
    opts.debug_print(ir_module)
    
    obj_code = compile_ir(ir_module)
    with open(opts.output_filename, 'wb') as f:
        f.write(obj_code)
    

if __name__ == '__main__':
    import sys
    main(sys.argv)
    

        
