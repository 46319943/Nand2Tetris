symbol_table = {
    'R0': 0,
    'R1': 1,
    'R2': 2,
    'R3': 3,
    'R4': 4,
    'R5': 5,
    'R6': 6,
    'R7': 7,
    'R8': 8,
    'R9': 9,
    'R10': 10,
    'R11': 11,
    'R12': 12,
    'R13': 13,
    'R14': 14,
    'R15': 15,
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
    'SCREEN': 16384,
    'KBD': 24576
}


# c1 ~ c6
comp_table = {
    '0': '101010',
    '1': '111111',
    '-1': '111010',
    'D': '001100',
    'A': '110000',
    '!D': '001101',
    '!A': '110001',
    '-D': '001111',
    '-A': '110011',
    'D+1': '011111',
    'A+1': '110111',
    'D-1': '001110',
    'A-1': '110010',
    'D+A': '000010',
    'D-A': '010011',
    'A-D': '000111',
    'D&A': '000000',
    'D|A': '010101',
}

# d1 ~ d3
dest_table = {
    'M': '001',
    'D': '010',
    'MD': '011',
    'A': '100',
    'AM': '101',
    'AD': '110',
    'AMD': '111',
}

# j1 ~ j3
jump_table = {
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111',
}


def parse(lines: list[str]):
    '''

    :param lines:
    :return:
    '''

    lines_stripped = first_pass(lines)

    line_processed = second_pass(lines_stripped)

    print(line_processed)

    return line_processed


def first_pass(lines: list[str]):
    '''

    :param lines:
    :return:
    '''

    lines_stripped = []

    for line in lines:

        # 去除注释
        line = line.split('//')[0]

        # 去除空行
        line = line.strip()
        if line == '':
            continue

        # 寻找标签
        if line.startswith('('):
            if not line.endswith(')'):
                # TODO: parse error tip
                pass

            # 去头尾括号
            line = line[1:-1]

            # TODO: 处理标签
            symbol_table[line] = len(lines_stripped)

            continue

        lines_stripped.append(line)

    return lines_stripped

def second_pass(lines: list[str]):
    '''

    :param lines:
    :return:
    '''
    variable_counter = 0
    variable_address = 16

    line_processed = []

    for line in lines:

        # A-Instruction
        if line.startswith('@'):
            line = line[1:]

            # Non-Variable
            if line.isnumeric():
                line_processed.append(
                    f'0{int(line):015b}'
                )
                continue

            # Variable
            if line not in symbol_table:
                symbol_table[line] = variable_address + variable_counter
                variable_counter = variable_counter + 1

            line_processed.append(
                f'0{symbol_table[line]:015b}'
            )

            continue

        # C-Instruction
        # dest=comp;jump
        # Either the dest or jump fields may be empty.
        # If dest is empty, the "=" is omitted;
        # If jump is empty, the ";" is omitted.

        if '=' in line:
            dest = line.split('=')[0].strip()
            dest_str = dest_table[dest]
        else:
            dest_str = '000'

        if ';' in line:
            jump = line.split(';')[-1].strip()
            jump_str = jump_table[jump]
        else:
            jump_str = '000'

        comp = line.split('=')[-1].split(';')[0].strip()

        a = '0'
        if 'M' in comp:
            a = '1'
            comp = comp.replace('M', 'A')

        comp_str = a + comp_table[comp]

        line_processed.append('111' + comp_str + dest_str + jump_str)

    return line_processed
