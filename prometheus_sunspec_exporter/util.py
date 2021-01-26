# https://stackoverflow.com/a/52676692/2150411
import ast
import numbers

def is_numeric(obj):
    try:
        if isinstance(obj, numbers.Number):
            return True
        elif isinstance(obj, str):
            nodes = list(ast.walk(ast.parse(obj)))[1:]
            if not isinstance(nodes[0], ast.Expr):
                return False
            if not isinstance(nodes[-1], ast.Num):
                return False
            nodes = nodes[1:-1]
            for i in range(len(nodes)):
                #if used + or - in digit :
                if i % 2 == 0:
                    if not isinstance(nodes[i], ast.UnaryOp):
                        return False
                else:
                    if not isinstance(nodes[i], (ast.USub, ast.UAdd)):
                        return False
            return True
        else:
            return False
    except:
        return False
