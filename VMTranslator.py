import sys
import os
from vm_translator import parse

if __name__ == '__main__':
    file_name = sys.argv[1]

    f = open(file_name)
    lines = f.readlines()
    f.close()

    lines_parsed = parse(lines, os.path.basename(file_name).rstrip('.vm'))

    f = open(file_name.replace('.vm', '.asm'), 'w')
    f.write('\n'.join(lines_parsed))
    f.close()
