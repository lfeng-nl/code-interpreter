import sys
import io
import threading
import time
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, Optional


class CodeExecutor:
    """安全的Python代码执行器"""
    
    def __init__(self, timeout: int = 10, max_output_size: int = 10000):
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.restricted_builtins = self._get_restricted_builtins()
    
    def _get_restricted_builtins(self) -> Dict[str, Any]:
        """获取受限的内置函数集合"""
        safe_builtins = {
            'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
            'callable', 'chr', 'classmethod', 'complex', 'dict', 'dir', 'divmod',
            'enumerate', 'filter', 'float', 'format', 'frozenset', 'getattr',
            'globals', 'hasattr', 'hash', 'hex', 'id', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max',
            'memoryview', 'min', 'next', 'object', 'oct', 'ord', 'pow',
            'print', 'property', 'range', 'repr', 'reversed', 'round',
            'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str',
            'sum', 'super', 'tuple', 'type', 'vars', 'zip'
        }
        
        # 只保留安全的内置函数
        restricted = {}
        builtins_dict = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
        
        for name in safe_builtins:
            if name in builtins_dict:
                restricted[name] = builtins_dict[name]
        
        # 添加安全的__import__函数
        restricted['__import__'] = self._safe_import
        
        return restricted
    
    def _safe_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """安全的import函数，只允许导入白名单中的模块"""
        safe_modules = {
            'math', 'random', 'datetime', 'json', 'time', 'collections',
            'itertools', 'functools', 're', 'string', 'decimal', 'fractions',
            'statistics', 'uuid', 'hashlib', 'base64', 'binascii'
        }
        
        if name in safe_modules:
            return __import__(name, globals, locals, fromlist, level)
        else:
            raise ImportError(f"模块 '{name}' 不在允许的导入列表中")
    
    def _create_safe_globals(self) -> Dict[str, Any]:
        """创建安全的全局命名空间"""
        safe_globals = {
            '__builtins__': self.restricted_builtins,
            '__name__': '__main__',
            '__doc__': None,
        }
        
        # 添加一些安全的模块
        import math
        import random
        import datetime
        import json
        
        safe_globals.update({
            'math': math,
            'random': random,
            'datetime': datetime,
            'json': json,
        })
        
        return safe_globals
    
    def execute(self, code: str) -> Dict[str, Any]:
        """
        执行Python代码
        
        Args:
            code: 要执行的Python代码
            
        Returns:
            包含执行结果的字典
        """
        result = {
            'success': False,
            'output': '',
            'error': None,
            'execution_time': 0
        }
        
        if not code.strip():
            result['error'] = '代码不能为空'
            return result
        
        # 创建输出捕获
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # 执行结果容器
        execution_result = {'completed': False, 'exception': None}
        
        def execute_code():
            try:
                start_time = time.time()
                
                # 创建安全的执行环境
                safe_globals = self._create_safe_globals()
                safe_locals = {}
                
                # 重定向输出
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    # 执行代码
                    exec(code, safe_globals, safe_locals)
                
                execution_result['completed'] = True
                result['execution_time'] = time.time() - start_time
                
            except Exception as e:
                execution_result['exception'] = e
                execution_result['completed'] = True
        
        # 在单独线程中执行代码以支持超时
        thread = threading.Thread(target=execute_code)
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.timeout)
        
        # 检查执行结果
        if not execution_result['completed']:
            result['error'] = f'代码执行超时（超过{self.timeout}秒）'
            return result
        
        if execution_result['exception']:
            result['error'] = f'{type(execution_result["exception"]).__name__}: {str(execution_result["exception"])}'
            # 添加错误输出到stderr
            stderr_output = stderr_capture.getvalue()
            if stderr_output:
                result['error'] += f'\n{stderr_output}'
            return result
        
        # 获取输出
        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()
        
        # 合并输出
        output_parts = []
        if stdout_output:
            output_parts.append(stdout_output)
        if stderr_output:
            output_parts.append(f'stderr: {stderr_output}')
        
        full_output = '\n'.join(output_parts)
        
        # 限制输出大小
        if len(full_output) > self.max_output_size:
            full_output = full_output[:self.max_output_size] + '\n... (输出被截断)'
        
        result['success'] = True
        result['output'] = full_output
        
        return result


def test_executor():
    """测试代码执行器"""
    executor = CodeExecutor()
    
    # 测试正常代码
    result = executor.execute("print('Hello, World!')")
    print("测试1 - 正常代码:", result)
    
    # 测试数学计算
    result = executor.execute("""
import math
result = math.sqrt(16)
print(f"sqrt(16) = {result}")
""")
    print("测试2 - 数学计算:", result)
    
    # 测试错误代码
    result = executor.execute("print(undefined_variable)")
    print("测试3 - 错误代码:", result)
    
    # 测试危险代码（应该被阻止）
    result = executor.execute("import os; os.system('ls')")
    print("测试4 - 危险代码:", result)


if __name__ == '__main__':
    test_executor()