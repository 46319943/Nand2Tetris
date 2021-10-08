import glob
import os
import re
import sys
from xml.etree import ElementTree

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
                file_path.replace('.jack', 'Token.xml'),
                short_empty_elements=False
            )

            parse(ele_tree).write(
                file_path.replace('.jack', 'Complete.xml'),
                short_empty_elements=False
            )

            # 正则添加换行
            with open(file_path.replace('.jack', '.xml'), "w") as f:
                f.write(
                    re.sub(
                        r'><',
                        '>\n<',
                        ElementTree.tostring(
                            parse(ele_tree).getroot(),
                            encoding='unicode',
                            short_empty_elements=False
                        )
                    )
                )

            # TODO: do not close empty element
            # xmlstr = minidom.parseString(
            #     ET.tostring(parse(ele_tree).getroot(), short_empty_elements=False)
            # ).childNodes[0].toprettyxml(indent="   ")
            # with open(file_path.replace('.jack', 'TTTT.xml'), "w") as f:
            #     f.write(xmlstr)

    else:
        file_path = input_path

        file_name = os.path.basename(file_path)
        file_base_name = file_name.rstrip('.jack')

        f = open(file_path)
        lines = f.readlines()
        f.close()

        ele_tree = tokenize(lines)

        ele_tree.write(
            file_path.replace('.jack', 'Token.xml'),
            short_empty_elements=False
        )

        parse(ele_tree).write(
            file_path.replace('.jack', 'Complete.xml'),
            short_empty_elements=False
        )

        # 正则添加换行
        with open(file_path.replace('.jack', '.xml'), "w") as f:
            f.write(
                re.sub(
                    r'><',
                    '>\n<',
                    ElementTree.tostring(
                        parse(ele_tree).getroot(),
                        encoding='unicode',
                        short_empty_elements=False
                    )
                )
            )
