import ast
from llvmlite import ir, binding
binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()


class LLVMEmitter(object):
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
        # note this isn't going to work for recursive functions
        # hard coded return value, hardcoded 64 bit integers
        function_type = ir.FunctionType(ir.VoidType(), [ir.IntType(64) for _ in node.args])  
        fn = ir.Function(self.module, function_type, name=node.name)
        block = fn.append_basic_block(name='entry')
        self.functions[node.name] = fn
        self.builder = ir.IRBuilder(block)
        # lookup table for function arguments and local variables
        self.function_arguments = {ast_arg.name: llvm_arg for ast_arg,llvm_arg in zip(node.args, fn.args)}
        self.local_variables = {}
        
        self._recurse(node.body)
            
        self.builder.ret_void()
        
        
    def visit_JapycBinOp(self, node):
        a = self.visit(node.left)
        b = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return self.builder.add(a, b)
        elif isinstance(node.op, ast.Mult):
            return self.builder.mul(a, b)
        else:
            raise NotImplementedError()
        
    def visit_JapycInteger(self, node):
        return ir.Constant(ir.IntType(64), node.value)
    
    def get_local(self, name):
        if name in self.local_variables:
            return self.local_variables[name]
        else:
            ref = self.builder.alloca(ir.IntType(64))
            self.local_variables[name] = ref
            return ref
    
    def visit_JapycVariable(self, node, *, load=True):
        if node.name in self.function_arguments:
            return self.function_arguments[node.name]
        else:
            var = self.get_local(node.name)
            if load:
                return self.builder.load(var)
            else:
                return var
        
    def visit_JapycPutInt(self, node):        
        int_type = ir.IntType(node.bits)
        addr = self.builder.inttoptr(self.visit(node.address), int_type.as_pointer())
        value = self.visit(node.value)
        self.builder.store(value, addr)
        
    def visit_JapycFunctionCall(self, node):
        args = self._recurse(node.args)
        self.builder.call(self.functions[node.fn], args)
        
    def visit_JapycSingleAssign(self, node):
        var = self.visit(node.var, load=False)
        assert not isinstance(var, ir.Argument)
        val = self.visit(node.value)
        return self.builder.store(val, var)
        
    def generic_visit(self, node):
        raise NotImplementedError('node type not implemented: {}'.format(node.__class__.__name__))        

    def visit(self, node, **kwargs):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, **kwargs)

        
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
