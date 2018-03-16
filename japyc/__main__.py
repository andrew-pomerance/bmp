'''
 japyc - Just Another PYthon Compiler
(C) 2018 Andrew Pomerance
''' 

import ast
import pprint
from .visitor import JapycVisitor 
from .llvm import LLVMEmitter, compile_ir

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
    

        
