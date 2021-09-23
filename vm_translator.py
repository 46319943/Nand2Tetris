'''
stack machine translator
'''


def parse(lines: list[str]):
    line_processed = []

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
    index_str = str(index)
    return [
        '// push temp ' + index_str,

        # D = *(temp + i)
        '@' + str(5 + index),
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
    index_str = str(index)
    return [
        '// pop temp ' + index_str,

        # D =  *(--stack)
        '@R0',
        'M=M-1',
        'A=M',
        'D=M',

        # *(temp + i) = D
        '@' + str(5 + index),
        'M=D',
    ]


def push_pointer(value):
    value_str = str(value)
    if value == 0:
        R = 'R3'
    elif value == 1:
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
    if value == 0:
        R = 'R3'
    elif value == 1:
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

def push_static(index):
    index_str = str(index)
    return [
        
    ]