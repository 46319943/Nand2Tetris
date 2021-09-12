from assembler import parse


def main():
    f = open(r'C:\Users\PiaoYang\Desktop\nand2tetris\projects\06\max\Max.asm')
    lines = f.readlines()
    f.close()

    lines_parsed = parse(lines)
    f = open(r'C:\Users\PiaoYang\Desktop\nand2tetris\projects\06\max\Max.hack', 'w')
    f.write('\n'.join(lines_parsed))
    f.close()


if __name__ == '__main__':
    main()
