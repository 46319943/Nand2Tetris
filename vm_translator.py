'''
stack machine translator
'''
from typing import List

function_ret_count_map = {}


def parse(lines: List[str], file_name: str):
    line_processed = []
    current_function_name = ''

    for line in lines:

        # 去除注释
        line = line.split('//')[0]

        # 去除空行、空格
        line = line.strip()
        if line == '':
            continue

        line_index = len(line_processed)

        if line == 'add':
            line_processed.extend(add())
        elif line == 'sub':
            line_processed.extend(sub())
        elif line == 'neg':
            line_processed.extend(neg())
        elif line == 'eq':
            line_processed.extend(eq(line_index))
        elif line == 'gt':
            line_processed.extend(gt(line_index))
        elif line == 'lt':
            line_processed.extend(lt(line_index))
        elif line == 'and':
            line_processed.extend(And())
        elif line == 'or':
            line_processed.extend(Or())
        elif line == 'not':
            line_processed.extend(Not())
        elif line.startswith('push constant '):
            line_processed.extend(
                push_constant(line.lstrip('push constant '))
            )
        elif line.startswith('push local '):
            line_processed.extend(
                push_local(line.lstrip('push local '))
            )
        elif line.startswith('pop local '):
            line_processed.extend(
                pop_local(line.lstrip('pop local '))
            )
        elif line.startswith('push argument '):
            line_processed.extend(
                push_argument(line.lstrip('push argument '))
            )
        elif line.startswith('pop argument '):
            line_processed.extend(
                pop_argument(line.lstrip('pop argument '))
            )
        elif line.startswith('push this '):
            line_processed.extend(
                push_this(line.lstrip('push this '))
            )
        elif line.startswith('pop this '):
            line_processed.extend(
                pop_this(line.lstrip('pop this '))
            )
        elif line.startswith('push that '):
            line_processed.extend(
                push_that(line.lstrip('push that '))
            )
        elif line.startswith('pop that '):
            line_processed.extend(
                pop_that(line.lstrip('pop that '))
            )
        elif line.startswith('push temp '):
            line_processed.extend(
                push_temp(line.lstrip('push temp '))
            )
        elif line.startswith('pop temp '):
            line_processed.extend(
                pop_temp(line.lstrip('pop temp '))
            )
        elif line.startswith('push pointer '):
            line_processed.extend(
                push_pointer(line.lstrip('push pointer '))
            )
        elif line.startswith('pop pointer '):
            line_processed.extend(
                pop_pointer(line.lstrip('pop pointer '))
            )
        elif line.startswith('push static '):
            line_processed.extend(
                push_static(line.lstrip('push static '), file_name)
            )
        elif line.startswith('pop static '):
            line_processed.extend(
                pop_static(line.lstrip('pop static '), file_name)
            )
        elif line.startswith('label '):
            line_processed.extend(
                label(line.lstrip('label '))
            )
        elif line.startswith('goto '):
            line_processed.extend(
                goto(line.lstrip('goto '))
            )
        elif line.startswith('if-goto '):
            line_processed.extend(
                if_goto(line.lstrip('if-goto '))
            )
        elif line.startswith('function '):
            current_function_name = line.strip(' ').split(' ')[1]

            pass
        elif line.startswith('call '):
            _, function_name, argument_count = line.strip(' ').split(' ')
            call(function_name, argument_count, current_function_name)

    return line_processed


def push_constant(constant):
    return [
        '// push constant ' + str(constant),

        # D = constant
        '@' + str(constant),
        'D=A',

        # *stack = constant
        '@R0',
        'A=M',
        'M=D',

        # stack++
        '@R0',
        'M=M+1'
    ]


def add():
    return [
        '// x + y',

        # stack--
        '@R0',
        'M=M-1',

        # D=y=*stack
        'A=M',
        'D=M',

        # stack--
        '@R0',
        'M=M-1',

        # *stack=x+y=*stack+D
        'A=M',
        'M=M+D',

        # stack++
        '@R0',
        'M=M+1',
    ]


def sub():
    return [
        '// x - y',

        # stack--
        '@R0',
        'M=M-1',

        # D=y=*stack
        'A=M',
        'D=M',

        # stack - 1
        'A=A-1',

        # *(stack-1)=x-y=*(stack-1)-D
        'M=M-D',
    ]


def neg():
    return [
        '// -y',

        # stack - 1
        '@R0',
        'A=M-1',

        # -*(stack-1)
        'M=-M'
    ]


def eq(line_index):
    label_suffix = str(line_index)

    return [
        '// x == y',

        # stack--
        '@R0',
        'M=M-1',

        # D=y=*stack
        'A=M',
        'D=M',

        # stack - 1
        'A=A-1',

        # x-y=*(stack-1)-D
        'D=M-D',
        '@EQ_TRUE' + '_' + label_suffix,
        'D;JEQ',

        # if not eq, return 0
        'D=0',
        '@EQ_IF_END' + '_' + label_suffix,
        '0;JMP',

        # if eq, return -1
        f'(EQ_TRUE_{label_suffix})',
        'D=-1',

        # eq if end
        f'(EQ_IF_END_{label_suffix})',
        '@R0',
        'A=M-1',
        'M=D',

    ]


def gt(line_index):
    label_suffix = str(line_index)

    return [
        '// x > y',

        # stack--
        '@R0',
        'M=M-1',

        # D=y=*stack
        'A=M',
        'D=M',

        # stack - 1
        'A=A-1',

        # x-y=*(stack-1)-D
        'D=M-D',
        '@GT_TRUE' + '_' + label_suffix,
        'D;JGT',

        # if not gt, return 0
        'D=0',
        '@GT_IF_END' + '_' + label_suffix,
        '0;JMP',

        # if gt, return -1
        f'(GT_TRUE_{label_suffix})',
        'D=-1',

        # gt if end
        f'(GT_IF_END_{label_suffix})',
        '@R0',
        'A=M-1',
        'M=D',
    ]


def lt(line_index):
    label_suffix = str(line_index)

    return [
        '// x < y',

        # stack--
        '@R0',
        'M=M-1',

        # D=y=*stack
        'A=M',
        'D=M',

        # stack - 1
        'A=A-1',

        # x-y=*(stack-1)-D
        'D=M-D',
        '@LT_TRUE' + '_' + label_suffix,
        'D;JLT',

        # if not lt, return 0
        'D=0',
        '@LT_IF_END' + '_' + label_suffix,
        '0;JMP',

        # if lt, return -1
        f'(LT_TRUE_{label_suffix})',
        'D=-1',

        # lt if end
        f'(LT_IF_END_{label_suffix})',
        '@R0',
        'A=M-1',
        'M=D',
    ]


def And():
    return [
        '// x And y',

        # stack--
        '@R0',
        'M=M-1',

        # D=y=*stack
        'A=M',
        'D=M',

        # stack - 1
        'A=A-1',

        # *(stack-1) = x And y = *(stack-1) And D
        'M=D&M'

    ]


def Or():
    return [
        '// x Or y',

        # stack--
        '@R0',
        'M=M-1',

        # D=y=*stack
        'A=M',
        'D=M',

        # stack - 1
        'A=A-1',

        # *(stack-1) = x Or y = *(stack-1) Or D
        'M=D|M'

    ]


def Not():
    return [
        '// Not y',

        # stack - 1
        '@R0',
        'A=M-1',

        # *(stack-1) = Not *(stack-1)
        'M=!M'

    ]


def push_local(index):
    index_str = str(index)
    return [
        '// push local ' + index_str,

        # D = *(LCL + i)
        '@' + index_str,
        'D=A',
        '@R1',
        'A=M+D',
        'D=M',

        # *stack = D
        '@R0',
        'A=M',
        'M=D',

        # stack++
        '@R0',
        'M=M+1',
    ]


def pop_local(index):
    '''
    因为LCL + i一定需要使用到D，而*stack的结果必须使用D才能存入*(LCL + i)，
    所以必须缓存LCL + i的值，让其索引的时候不用D
    :param index:
    :return:
    '''
    index_str = str(index)
    return [
        '// pop local ' + index_str,

        # LCL = LCL + i
        '@' + index_str,
        'D=A',
        '@R1',
        'M=M+D',

        # D =  *(--stack)
        '@R0',
        'M=M-1',
        'A=M',
        'D=M',

        # *LCL = D
        '@R1',
        'A=M',
        'M=D',

        # LCL = LCL - i
        '@' + index_str,
        'D=A',
        '@R1',
        'M=M-D',
    ]


def push_argument(index):
    index_str = str(index)
    return [
        '// push argument ' + index_str,
        '@' + index_str,
        'D=A',
        '@R2',
        'A=M+D',
        'D=M',
        '@R0',
        'A=M',
        'M=D',
        '@R0',
        'M=M+1',
    ]


def pop_argument(index):
    index_str = str(index)
    return [
        '// pop argument ' + index_str,
        '@' + index_str,
        'D=A',
        '@R2',
        'M=M+D',
        '@R0',
        'M=M-1',
        'A=M',
        'D=M',
        '@R2',
        'A=M',
        'M=D',
        '@' + index_str,
        'D=A',
        '@R2',
        'M=M-D',
    ]


def push_this(index):
    index_str = str(index)
    return [
        '// push this ' + index_str,
        '@' + index_str,
        'D=A',
        '@R3',
        'A=M+D',
        'D=M',
        '@R0',
        'A=M',
        'M=D',
        '@R0',
        'M=M+1',
    ]


def pop_this(index):
    index_str = str(index)
    return [
        '// pop this ' + index_str,
        '@' + index_str,
        'D=A',
        '@R3',
        'M=M+D',
        '@R0',
        'M=M-1',
        'A=M',
        'D=M',
        '@R3',
        'A=M',
        'M=D',
        '@' + index_str,
        'D=A',
        '@R3',
        'M=M-D',
    ]


def push_that(index):
    index_str = str(index)
    return [
        '// push that ' + index_str,
        '@' + index_str,
        'D=A',
        '@R4',
        'A=M+D',
        'D=M',
        '@R0',
        'A=M',
        'M=D',
        '@R0',
        'M=M+1',
    ]


def pop_that(index):
    index_str = str(index)
    return [
        '// pop that ' + index_str,
        '@' + index_str,
        'D=A',
        '@R4',
        'M=M+D',
        '@R0',
        'M=M-1',
        'A=M',
        'D=M',
        '@R4',
        'A=M',
        'M=D',
        '@' + index_str,
        'D=A',
        '@R4',
        'M=M-D',
    ]


def push_temp(index):
    index_int = int(index)
    index_str = str(index)
    return [
        '// push temp ' + index_str,

        # D = *(temp + i)
        '@' + str(5 + index_int),
        'D=M',

        # *stack = D
        '@R0',
        'A=M',
        'M=D',

        # stack++
        '@R0',
        'M=M+1',
    ]


def pop_temp(index):
    index_int = int(index)
    index_str = str(index)
    return [
        '// pop temp ' + index_str,

        # D =  *(--stack)
        '@R0',
        'M=M-1',
        'A=M',
        'D=M',

        # *(temp + i) = D
        '@' + str(5 + index_int),
        'M=D',
    ]


def push_pointer(value):
    value_str = str(value)
    if value_str == '0':
        R = 'R3'
    elif value_str == '1':
        R = 'R4'
    else:
        raise Exception()
    return [
        '// push pointer ' + value_str,

        # D = THIS/THAT
        '@' + R,
        'D=M',

        # *stack = D
        '@R0',
        'A=M',
        'M=D',

        # stack++
        '@R0',
        'M=M+1',
    ]


def pop_pointer(value):
    value_str = str(value)
    if value_str == '0':
        R = 'R3'
    elif value_str == '1':
        R = 'R4'
    else:
        raise Exception()
    return [
        '// pop pointer ' + value_str,

        # stack--
        '@R0',
        'M=M-1',

        # D = *stack
        'A=M',
        'D=M',

        # THIS/THAT = D
        '@' + R,
        'M=D'
    ]


def push_static(index, file_name: str):
    index_str = str(index)
    return [
        '// push static ' + index_str,

        # D = static
        '@' + file_name + '.' + index_str,
        'D=M',

        # *(stack++) = D
        '@R0',
        'A=M',
        'M=D',
        '@R0',
        'M=M+1',
    ]


def pop_static(index, file_name: str):
    index_str = str(index)
    return [
        '// pop static ' + index_str,

        # D = *(--stack)
        '@R0',
        'M=M-1',
        'A=M',
        'D=M',

        # static = D
        '@' + file_name + '.' + index_str,
        'M=D'
    ]


def label(name):
    return [
        '// label ' + name,

        f'({name})'
    ]


def goto(name):
    return [
        '// goto ' + name,

        '@' + name,
        '0;JMP',
    ]


def if_goto(name):
    return [
        '// if-goto ' + name,

        # D = *(--stack)
        '@R0',
        'M=M-1',
        'A=M',
        'D=M',

        # JMP to name if not false (D != 0)
        '@' + name,
        'D;JNE',

    ]


def call(function_name, argument_count, current_function_name):
    ret_addr_label = current_function_name + '$ret.' + str(
        function_ret_count_map.get(current_function_name, 1)
    )

    return [
        '// call ' + function_name + ' ' + argument_count,

        # push retAddrLabel
        '@' + ret_addr_label,
        'D=A',
        '@R0',
        'A=M',
        'M=D',
        '@R0',
        'M=M+1',

        # push LCL
        '@R1',
        'D=A',
        '@R0',
        'A=M',
        'M=D',
        '@R0',
        'M=M+1',

        # push ARG
        '@R2',
        'D=A',
        '@R0',
        'A=M',
        'M=D',
        '@R0',
        'M=M+1',

        # push THIS
        '@R3',
        'D=A',
        '@R0',
        'A=M',
        'M=D',
        '@R0',
        'M=M+1',

        # push THAT
        '@R4',
        'D=A',
        '@R0',
        'A=M',
        'M=D',
        '@R0',
        'M=M+1',

        # ARG = SP-5-nArgs
        '@R0',
        'D=M',
        'D=D-' + str(5 + int(argument_count)),
        '@R2',
        'M=D',

        # LCL = SP
        '@R0',
        'D=M',
        '@R1',
        'M=D',

        # goto functionName
        '@' + function_name,
        '0;JMP',

        f'({ret_addr_label})',
    ]
