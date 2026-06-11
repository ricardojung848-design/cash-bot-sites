import ast

def validate_code_syntax(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
            ast.parse(code)
        return True, "OK"
    except Exception as e:
        return False, str(e)