import glob
import os
import re
import sys
from xml.etree.ElementTree import Element, tostring

from syntax_analyzer import tokenize, parse


def write_element_to_file(file_path: str, element: Element):
    '''
    以XML输出Element
    标签之前正则添加换行
    '''
    with open(file_path, "w") as f:
        f.write(
            re.sub(
                r'><',
                '>\n<',
                tostring(
                    element,
                    encoding='unicode',
                    short_empty_elements=False
                )
            )
        )


def compile_file(file_path: str):
    file_name = os.path.basename(file_path)
    file_base_name = file_name.rstrip('.jack')

    f = open(file_path)
    lines = f.readlines()
    f.close()

    token_root = tokenize(lines)
    write_element_to_file(
        file_path.replace('.jack', 'Token.xml'),
        token_root
    )

    parse_element, vm_code = parse(token_root)

    write_element_to_file(
        file_path.replace('.jack', 'Complete.xml'),
        parse_element
    )

    with open(file_path.replace('.jack', '.vm'), "w") as f:
        f.write('\n'.join(vm_code))


if __name__ == '__main__':
    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        dir_path = input_path
        dir_name = os.path.basename(dir_path)

        file_path_list = [file_path for file_path in glob.glob(dir_path + '/*.jack')]

        for file_path in file_path_list:
            compile_file(file_path)
    else:
        file_path = input_path
        compile_file(file_path)
