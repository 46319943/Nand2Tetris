import sys
import os
import glob
from syntax_analyzer import tokenize, parse

if __name__ == '__main__':
    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        dir_path = input_path
        dir_name = os.path.basename(dir_path)

        file_path_list = [file_path for file_path in glob.glob(dir_path + '/*.jack')]

        for file_path in file_path_list:
            file_name = os.path.basename(file_path)
            file_base_name = file_name.rstrip('.jack')

            f = open(file_path)
            lines = f.readlines()
            f.close()

            # TODO: newline required
            ele_tree = tokenize(lines)
            ele_tree.write(
                file_path.replace('.jack', 'TT.xml')
            )

            parse(ele_tree).write(
                file_path.replace('.jack', 'TTT.xml')
            )

    else:
        file_path = input_path

        file_name = os.path.basename(file_path)
        file_base_name = file_name.rstrip('.jack')

        f = open(file_path)
        lines = f.readlines()
        f.close()

        ele_tree = tokenize(lines)

        ele_tree.write(file_path.replace('.jack', 'TT.xml'))

        parse(ele_tree).write(
            file_path.replace('.jack', 'TTT.xml')
        )
