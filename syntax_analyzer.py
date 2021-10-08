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


def tokenize(lines: List[str]):
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
                # 不需要，模块自动转译。
                # 这里弄了之后，相反无法识别符号了

                # if token == '<':
                #     token = '&lt;'
                # if token == '>':
                #     token = '&gt;'
                # if token == '&':
                #     token = '&amp;'

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


def compile_identifier(token_element_list: List[Element], require=True):
    identifier_token = token_element_list[-1]

    if identifier_token.tag != 'identifier':
        if require:
            raise Exception('identifier require')
        else:
            return None

    return token_element_list.pop()


def compile_type(token_element_list: List[Element], require=True):
    type_keyword_or_identifier = token_element_list[-1]

    if type_keyword_or_identifier.tag == 'keyword':
        if type_keyword_or_identifier.text not in ['int', 'char', 'boolean']:
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
        comma_symbol = compile_symbol(
            token_element_list, ',', require=False
        )
        if comma_symbol is None:
            break

        class_var_dec_element.append(comma_symbol)
        class_var_dec_element.append(
            compile_identifier(token_element_list, require=True)
        )
        continue

    class_var_dec_element.append(
        compile_symbol(token_element_list, ';', require=True)
    )

    return class_var_dec_element


def compile_subroutine_dec(token_element_list: List[Element]):
    class_subroutine_dec_element = Element('subroutineDec')

    constructor_or_function_or_method_keyword = compile_keyword(
        token_element_list, ['constructor', 'function', 'method'], require=False
    )
    if constructor_or_function_or_method_keyword is None:
        return None
    class_subroutine_dec_element.append(constructor_or_function_or_method_keyword)

    void_or_type_keyword_or_identifier = token_element_list.pop()
    if void_or_type_keyword_or_identifier.tag == 'keyword':
        if void_or_type_keyword_or_identifier.text not in ['void', 'int', 'char', 'boolean']:
            raise Exception('void or type text not match')
    elif void_or_type_keyword_or_identifier.tag != 'identifier':
        raise Exception('type tag not match identifier')
    class_subroutine_dec_element.append(void_or_type_keyword_or_identifier)

    class_subroutine_dec_element.append(
        compile_identifier(token_element_list, require=True)
    )

    class_subroutine_dec_element.append(
        compile_symbol(token_element_list, '(', require=True)
    )

    class_subroutine_dec_element.append(
        compile_parameter_list(token_element_list)
    )

    class_subroutine_dec_element.append(
        compile_symbol(token_element_list, ')', require=True)
    )

    class_subroutine_dec_element.append(
        compile_subroutine_body(token_element_list)
    )

    return class_subroutine_dec_element


def compile_parameter_list(token_element_list: List[Element]):
    parameter_list_element = Element('parameterList')

    type_element = compile_type(token_element_list, require=False)
    if type_element is not None:
        parameter_list_element.append(type_element)

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


def compile_subroutine_body(token_element_list: List[Element]):
    subroutine_body_element = Element('subroutineBody')

    subroutine_body_element.append(
        compile_symbol(token_element_list, '{', require=True)
    )

    while True:
        var_dec_element = compile_var_dec(token_element_list, require=False)
        if var_dec_element is None:
            break
        subroutine_body_element.append(var_dec_element)

    subroutine_body_element.append(
        compile_statements(token_element_list)
    )

    subroutine_body_element.append(
        compile_symbol(token_element_list, '}', require=True)
    )

    return subroutine_body_element


def compile_var_dec(token_element_list: List[Element], require=True):
    var_dec_element = Element('varDec')

    var_keyword = compile_keyword(token_element_list, 'var', require=False)
    if var_keyword is None:
        if require:
            raise Exception('var keyword require')
        else:
            return None

    var_dec_element.append(
        var_keyword
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
            compile_identifier(token_element_list, require=True)
        )

    var_dec_element.append(
        compile_symbol(token_element_list, ';', require=True)
    )

    return var_dec_element


def compile_statements(token_element_list: List[Element]):
    statements_element = Element('statements')

    while True:
        statement_keyword = token_element_list[-1]
        if statement_keyword.tag != 'keyword' or statement_keyword.text not in ['let', 'if', 'while', 'do', 'return']:
            break

        if statement_keyword.text == 'let':
            statements_element.append(
                compile_let_statement(token_element_list)
            )
        elif statement_keyword.text == 'if':
            statements_element.append(
                compile_if_statement(token_element_list)
            )
        elif statement_keyword.text == 'while':
            statements_element.append(
                compile_while_statement(token_element_list)
            )
        elif statement_keyword.text == 'do':
            statements_element.append(
                compile_do_statement(token_element_list)
            )
        elif statement_keyword.text == 'return':
            statements_element.append(
                compile_return_statement(token_element_list)
            )

    return statements_element


def compile_let_statement(token_element_list: List[Element]):
    let_statement_element = Element('letStatement')

    let_statement_element.append(
        compile_keyword(token_element_list, 'let', require=True)
    )

    let_statement_element.append(
        compile_identifier(token_element_list, require=True)
    )

    left_brackets_symbol = compile_symbol(token_element_list, '[', require=False)
    if left_brackets_symbol is not None:
        let_statement_element.append(left_brackets_symbol)
        let_statement_element.append(
            compile_expression(token_element_list, require=True)
        )
        let_statement_element.append(
            compile_symbol(token_element_list, ']', require=True)
        )

    let_statement_element.append(
        compile_symbol(token_element_list, '=', require=True)
    )

    let_statement_element.append(
        compile_expression(token_element_list, require=True)
    )

    let_statement_element.append(
        compile_symbol(token_element_list, ';', require=True)
    )

    return let_statement_element


def compile_if_statement(token_element_list: List[Element]):
    if_statement_element = Element('ifStatement')

    if_statement_element.append(
        compile_keyword(token_element_list, 'if', require=True)
    )

    if_statement_element.append(
        compile_symbol(token_element_list, '(', require=True)
    )

    if_statement_element.append(
        compile_expression(token_element_list, require=True)
    )

    if_statement_element.append(
        compile_symbol(token_element_list, ')', require=True)
    )

    if_statement_element.append(
        compile_symbol(token_element_list, '{', require=True)
    )

    if_statement_element.append(
        compile_statements(token_element_list)
    )

    if_statement_element.append(
        compile_symbol(token_element_list, '}', require=True)
    )

    else_keyword = compile_keyword(token_element_list, 'else', require=False)
    if else_keyword is not None:
        if_statement_element.append(else_keyword)

        if_statement_element.append(
            compile_symbol(token_element_list, '{', require=True)
        )

        if_statement_element.append(
            compile_statements(token_element_list)
        )

        if_statement_element.append(
            compile_symbol(token_element_list, '}', require=True)
        )

    return if_statement_element


def compile_while_statement(token_element_list: List[Element]):
    while_statement_element = Element('whileStatement')

    while_statement_element.append(
        compile_keyword(token_element_list, 'while', require=True)
    )

    while_statement_element.append(
        compile_symbol(token_element_list, '(', require=True)
    )

    while_statement_element.append(
        compile_expression(token_element_list, require=True)
    )

    while_statement_element.append(
        compile_symbol(token_element_list, ')', require=True)
    )

    while_statement_element.append(
        compile_symbol(token_element_list, '{', require=True)
    )

    while_statement_element.append(
        compile_statements(token_element_list)
    )

    while_statement_element.append(
        compile_symbol(token_element_list, '}', require=True)
    )

    return while_statement_element


def compile_do_statement(token_element_list: List[Element]):
    do_statement_element = Element('doStatement')
    do_statement_element.append(
        compile_keyword(token_element_list, 'do', require=True)
    )
    do_statement_element.append(
        compile_identifier(token_element_list, require=True)
    )

    # LL(2)
    next_token = token_element_list[-1]

    # varName
    if next_token.tag != 'symbol':
        raise Exception('subroutineCall require')

    # subroutineCall
    elif next_token.text == '(':
        do_statement_element.append(
            compile_symbol(token_element_list, '(', require=True)
        )
        do_statement_element.append(
            compile_expression_list(token_element_list)
        )
        do_statement_element.append(
            compile_symbol(token_element_list, ')', require=True)
        )
    # class.subroutineCall
    elif next_token.text == '.':
        do_statement_element.append(
            compile_symbol(token_element_list, '.', require=True)
        )
        do_statement_element.append(
            compile_identifier(token_element_list, require=True)
        )
        do_statement_element.append(
            compile_symbol(token_element_list, '(', require=True)
        )
        do_statement_element.append(
            compile_expression_list(token_element_list)
        )
        do_statement_element.append(
            compile_symbol(token_element_list, ')', require=True)
        )
    else:
        raise Exception('subroutineCall symbol text not match')

    do_statement_element.append(
        compile_symbol(token_element_list, ';', require=True)
    )

    return do_statement_element


def compile_return_statement(token_element_list: List[Element]):
    return_statement_element = Element('returnStatement')
    return_statement_element.append(
        compile_keyword(token_element_list, 'return', require=True)
    )

    expression_element = compile_expression(token_element_list, require=False)
    if expression_element is not None:
        return_statement_element.append(expression_element)

    return_statement_element.append(
        compile_symbol(token_element_list, ';', require=True)
    )

    return return_statement_element


def compile_expression_list(token_element_list: List[Element]):
    expression_list_element = Element('expressionList')

    expresstion_element = compile_expression(token_element_list, require=False)
    if expresstion_element is not None:
        expression_list_element.append(expresstion_element)

        while True:
            comma_symbol = compile_symbol(token_element_list, ',', require=False)
            if comma_symbol is None:
                break
            expression_list_element.append(comma_symbol)
            expression_list_element.append(
                compile_expression(token_element_list, require=True)
            )

    return expression_list_element


def compile_expression(token_element_list: List[Element], require=True):
    expression_element = Element('expression')
    term_element = compile_term(token_element_list, require=False)
    if term_element is None:
        if require:
            raise Exception('term not match')
        else:
            return None
    expression_element.append(term_element)

    while True:
        op_element = compile_symbol(token_element_list, ['+', '-', '*', '/', '&', '|', '<', '>', '='], require=False)
        if op_element is None:
            break

        expression_element.append(op_element)
        expression_element.append(
            compile_term(token_element_list, require=True)
        )

    return expression_element


def compile_term(token_element_list: List[Element], require=True):
    '''

    LL(2) involved

    :param token_element_list:
    :param require:
    :return:
    '''

    term_element = Element('term')
    term_token = token_element_list.pop()
    term_element.append(term_token)

    if term_token.tag in ['integerConstant', 'stringConstant']:
        pass

    elif term_token.tag == 'keyword':
        if term_token.text not in ['true', 'false', 'null', 'this']:
            token_element_list.append(term_token)
            if require:
                raise Exception('keyword constant text not match')
            else:
                return None

    elif term_token.tag == 'identifier':

        # LL(2)
        # 如果使用-2索引，但是pop取出来还是-1。所以前面的term_token还是得pop出来。不匹配再push回去
        next_token = token_element_list[-1]

        # varName
        if next_token.tag != 'symbol':
            pass

        # varName[expression]
        elif next_token.text == '[':
            term_element.append(
                compile_symbol(token_element_list, '[', require=True)
            )
            term_element.append(
                compile_expression(token_element_list, require=True)
            )
            term_element.append(
                compile_symbol(token_element_list, ']', require=True)
            )
        # subroutineCall
        elif next_token.text == '(':
            term_element.append(
                compile_symbol(token_element_list, '(', require=True)
            )
            term_element.append(
                compile_expression_list(token_element_list)
            )
            term_element.append(
                compile_symbol(token_element_list, ')', require=True)
            )
        # class.subroutineCall
        elif next_token.text == '.':
            term_element.append(
                compile_symbol(token_element_list, '.', require=True)
            )
            term_element.append(
                compile_identifier(token_element_list, require=True)
            )
            term_element.append(
                compile_symbol(token_element_list, '(', require=True)
            )
            term_element.append(
                compile_expression_list(token_element_list)
            )
            term_element.append(
                compile_symbol(token_element_list, ')', require=True)
            )
        # varName
        else:
            pass

    elif term_token.tag == 'symbol':
        if term_token.text == '(':
            term_element.append(
                compile_expression(token_element_list, require=True)
            )
            term_element.append(
                compile_symbol(token_element_list, ')', require=True)
            )
        # unaryOp + term
        elif term_token.text in ['-', '~']:
            term_element.append(
                compile_term(token_element_list, require=True)
            )
        else:
            token_element_list.append(term_token)
            if require:
                raise Exception('term symbol text not match')
            else:
                return None
    else:
        token_element_list.append(term_token)
        if require:
            raise Exception('unsupported term')
        else:
            return None

    return term_element


def print_element(element):
    print(
        ', '.join(
            [
                f'({ele.tag}, {ele.text})'
                for ele in list(element)
            ]
        )
    )
