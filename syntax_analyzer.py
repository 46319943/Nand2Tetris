from xml.etree.ElementTree import Element, SubElement, ElementTree
import re
from typing import List, Union

keyword_list = [
    'class', 'constructor', 'function',
    'method', 'field', 'static', 'var', 'int',
    'char', 'boolean', 'void', 'true', 'false',
    'null', 'this', 'let', 'do', 'if', 'else',
    'while', 'return'
]

# metacharacters: . ^ $ * + ? { } [ ] \ | ( )
symbol_list = [
    '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*',
    '/', '&', '|', '<', '>', '=', '~'
]


# \w	匹配包括下划线的任何单词字符。等价于“[A-Za-z0-9_]”。注意Unicode正则表达式会匹配中文字符。
# \W	匹配任何非单词字符。等价于“[^A-Za-z0-9_]”。

# 前后加括号，整个为一组
# 直接使用\W匹配非单词字符即可
# symbol_re = r'(\{|\}|\(|\)|\[|\]|\.|,|;|\+|-|\*|/|&|\||<|>|=|~)'


def tokenize(lines: str):
    # 处理多行注释. 用空白替换/* */

    # 每一行本身就是\n结尾
    code_str = ''.join(lines)
    code_str = re.sub(
        # 非贪婪匹配，匹配最少的注释，避免注释结尾被当作注释内容
        r'/\*(.|\r|\n)*?\*/',
        '',
        code_str
    )
    lines = code_str.split('\n')

    # 创建xml根元素
    root = Element('tokens')

    for line in lines:

        # 去除单行注释
        line = line.split('//')[0]

        # 去除空行、空格
        line = line.strip()
        if line == '':
            continue

        # 用符号（非单词字符）对字符串进行分割，得到token
        # tokens = re.split(r'(\W)', line)

        # 字符串使用引号，不能用引号分割。
        # 字符串应该当作一个整体、作为分隔符进行分割。
        # 字符串包含Unicode字符，但是不能包含换行和引号（应包含制表符），使用非贪婪匹配，匹配最少的字符串，避免引号被包含在字符串中
        # 整个匹配规则作为一组、获取匹配的字符串。其它组的作为非获取匹配（shy groups），仅用来组合模式的各个部分
        tokens = re.split(r'([^\w"]|(?:"(?:.|\r)*?"))', line)

        for token in tokens:

            # 处理空格或空token
            token = token.strip()
            if token == '':
                continue

            # keyword process
            if token in keyword_list:
                SubElement(root, 'keyword').text = token
                continue

            # symbol process
            if token in symbol_list:

                # XML输出特殊符号替换
                if token == '<':
                    token = '&lt;'
                if token == '>':
                    token = '&gt;'
                if token == '&':
                    token = '&amp;'

                SubElement(root, 'symbol').text = token
                continue

            # integerConstant process
            if token.isdecimal():
                SubElement(root, 'integerConstant').text = token
                continue

            # StringConstant process
            if token.startswith('"') and token.endswith('"') and '"' not in token.strip('"'):
                SubElement(root, 'stringConstant').text = token.strip('"')
                continue

            # identifier process
            if (
                    # 非数字开头
                    not token[0].isdecimal()
            ) and (
                    # 由字母数字下划线组成
                    re.fullmatch(r'\w+', token) is not None
            ):
                SubElement(root, 'identifier').text = token
                continue

    return ElementTree(root)


def parse(ele_tree: ElementTree):
    token_root = ele_tree.getroot()
    # 反转token列表，从而使用pop按顺序获取token
    token_element_list = list(token_root)
    token_element_list.reverse()

    return ElementTree(
        compile_class(token_element_list)
    )


def compile_class(token_element_list: List[Element]):
    class_element = Element('class')

    class_keyword = compile_keyword(token_element_list, 'class', require=False)

    if class_keyword is None:
        return None
    class_element.append(class_keyword)

    class_element.append(
        compile_identifier(token_element_list, require=True)
    )

    class_element.append(
        compile_symbol(token_element_list, '{', require=True)
    )

    while True:
        class_var_dec_element = compile_class_var_dec(token_element_list)
        if class_var_dec_element is None:
            break
        class_element.append(class_var_dec_element)

    while True:
        class_subroutine_dec_element = compile_subroutine_dec(token_element_list)
        if class_subroutine_dec_element is None:
            break
        class_element.append(class_subroutine_dec_element)

    class_element.append(
        compile_symbol(token_element_list, '}', require=True)
    )

    return class_element


def compile_class_var_dec(token_element_list: List[Element]):
    class_var_dec_element = Element('classVarDec')

    static_or_field_keyword = compile_keyword(token_element_list, ['static', 'field'], require=False)
    if static_or_field_keyword is None:
        return None
    class_var_dec_element.append(static_or_field_keyword)

    class_var_dec_element.append(
        compile_type(token_element_list, require=True)
    )

    class_var_dec_element.append(
        compile_identifier(token_element_list, require=True)
    )

    while True:
        comma_or_semicolon_symbol = token_element_list.pop()
        if comma_or_semicolon_symbol.tag != 'symbol':
            raise Exception('comma or semicolon symbol not match')
        if comma_or_semicolon_symbol.text == ',':
            class_var_dec_element.append(comma_or_semicolon_symbol)

            var_name_identifier = token_element_list.pop()
            if var_name_identifier.tag != 'identifier':
                raise Exception('var name identifier not match')
            class_var_dec_element.append(var_name_identifier)

            continue

        elif comma_or_semicolon_symbol.text == ';':
            class_var_dec_element.append(comma_or_semicolon_symbol)
            break
        else:
            raise Exception('comma or semicolon text not match')

    return class_var_dec_element


def compile_subroutine_dec(token_element_list: List[Element]):
    class_subroutine_dec_element = Element('subroutineDec')

    constructor_or_function_or_method_keyword = token_element_list.pop()
    if constructor_or_function_or_method_keyword.tag != 'keyword' or (
            constructor_or_function_or_method_keyword.text not in ['constructor', 'function', 'method']
    ):
        token_element_list.append(constructor_or_function_or_method_keyword)
        return None
        # raise Exception('constructor function method not match')
    class_subroutine_dec_element.append(constructor_or_function_or_method_keyword)

    void_or_type_keyword_or_identifier = token_element_list.pop()
    if void_or_type_keyword_or_identifier.tag == 'keyword' and (
            void_or_type_keyword_or_identifier.text not in ['void', 'int', 'char', 'boolean']):
        raise Exception('void or type text not match')
    elif void_or_type_keyword_or_identifier.tag != 'identifier':
        raise Exception('type tag not match identifier')
    class_subroutine_dec_element.append(void_or_type_keyword_or_identifier)

    subroutine_name_identifier = token_element_list.pop()
    if subroutine_name_identifier.tag != 'identifier':
        raise Exception('subroutine name tag not match identifier')
    class_subroutine_dec_element.append(subroutine_name_identifier)

    left_parentheses_symbol = token_element_list.pop()
    if left_parentheses_symbol.tag != 'symbol' or left_parentheses_symbol.text != '(':
        raise Exception('subroutine dec left parentheses not match')
    class_subroutine_dec_element.append(left_parentheses_symbol)

    parameter_list_element = compile_parameter_list(token_element_list)
    if parameter_list_element is not None:
        class_subroutine_dec_element.append(parameter_list_element)

    class_subroutine_dec_element.append(
        compile_symbol(token_element_list, ')', require=True)
    )

    class_subroutine_dec_element.append(
        compile
    )

    return class_subroutine_dec_element


def compile_subroutine_body(token_element_list: List[Element]):
    subroutine_body_element = Element('subroutineBody')

    subroutine_body_element.append(
        compile_symbol(token_element_list, '{', require=True)
    )

    subroutine_body_element.append(
        compile_statements(token_element_list, require=True)
    )

    subroutine_body_element.append(
        compile_symbol(token_element_list, '}', require=True)
    )

    return subroutine_body_element


def compile_statements(token_element_list: List[Element], require=True):
    statements_element = Element('statements')

    return statements_element


def compile_var_dec(token_element_list: List[Element], require=True):
    var_dec_element = Element('varDec')

    var_keyword = compile_keyword(token_element_list, 'var', require=False)
    if var_keyword is None:
        if require:
            raise Exception('var keyword require')
        else:
            return None

    var_dec_element.append(
        var_dec_element
    )

    var_dec_element.append(
        compile_type(token_element_list, require=True)
    )

    var_dec_element.append(
        compile_identifier(token_element_list, require=True)
    )

    while True:
        comma_symbol = compile_symbol(token_element_list, ',', require=False)
        if comma_symbol is None:
            break
        var_dec_element.append(comma_symbol)
        var_dec_element.append(
            compile_type(token_element_list, require=True)
        )
        var_dec_element.append(
            compile_identifier(token_element_list, require=True)
        )

    return var_dec_element


def compile_type(token_element_list: List[Element], require=True):
    type_keyword_or_identifier = token_element_list[-1]

    if type_keyword_or_identifier.tag == 'keyword' and (
            type_keyword_or_identifier.text not in ['int', 'char', 'boolean']):
        if require:
            raise Exception('type keyword text not match')
        else:
            return None
    elif type_keyword_or_identifier.tag != 'identifier':
        if require:
            raise Exception('type identifier tag not match')
        else:
            return None

    return token_element_list.pop()


def compile_parameter_list(token_element_list: List[Element]):
    parameter_list_element = Element('parameterList')

    type_element = compile_type(token_element_list, require=False)
    if type_element is None:
        return None
    parameter_list_element.append(type_element)

    # var_name_identifier = token_element_list.pop()
    # if var_name_identifier.tag != 'identifier':
    #     raise Exception('var name tag not match identifier')
    # parameter_list_element.append(var_name_identifier)

    parameter_list_element.append(
        compile_identifier(token_element_list, require=True)
    )

    while True:
        if token_element_list[-1].tag == 'symbol' and token_element_list[-1].text == ',':
            parameter_list_element.append(
                token_element_list.pop()
            )
            parameter_list_element.append(
                compile_type(token_element_list, require=True)
            )
            parameter_list_element.append(
                compile_identifier(token_element_list, require=True)
            )
            continue
        else:
            break

    return parameter_list_element


def compile_identifier(token_element_list: List[Element], require=True):
    identifier_token = token_element_list[-1]

    if identifier_token.tag != 'identifier':
        if require:
            raise Exception('identifier require')
        else:
            return None

    return token_element_list.pop()


def compile_keyword(token_element_list: List[Element], keyword_limit: Union[str, List[str]], require=True):
    keyword_token = token_element_list[-1]

    if keyword_token.tag != 'keyword':
        if require:
            raise Exception('keyword require')
        else:
            return None

    if keyword_token.text not in keyword_limit:
        if require:
            raise Exception('keyword text not match')
        else:
            return None

    return token_element_list.pop()


def compile_symbol(token_element_list: List[Element], symbol_limit: Union[str, List[str]], require=True):
    symbol_token = token_element_list[-1]

    if symbol_token.tag != 'symbol':
        if require:
            raise Exception('symbol require')
        else:
            return None

    if symbol_token.text not in symbol_limit:
        if require:
            raise Exception('symbol text not match')
        else:
            return None

    return token_element_list.pop()
