import sys
import os
import glob
from vm_translator import parse, booting

if __name__ == '__main__':
    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        dir_path = input_path
        dir_name = os.path.basename(dir_path)

        file_path_list = [file_path for file_path in glob.glob(dir_path + '/*.vm')]
        lines_parsed_total = booting()

        for file_path in file_path_list:
            file_name = os.path.basename(file_path)
            file_base_name = file_name.rstrip('.vm')

            f = open(file_path)
            lines = f.readlines()
            f.close()

            lines_parsed = parse(lines, file_base_name)
            lines_parsed_total.extend(lines_parsed)

        f = open(os.path.join(dir_path, dir_name + '.asm'), 'w')
        f.write('\n'.join(lines_parsed_total))
        f.close()

    else:
        file_path = input_path

        file_name = os.path.basename(file_path)
        file_base_name = file_name.rstrip('.vm')

        f = open(file_path)
        lines = f.readlines()
        f.close()

        lines_parsed = parse(lines, file_base_name)

        f = open(file_path.replace('.vm', '.asm'), 'w')
        f.write('\n'.join(lines_parsed))
        f.close()
