from lmc import LmcImplementation as LittleManComputer

if __name__ == '__main__':
    with open('assembly_program.s', 'r') as f:
        program = f.read()

    computer = LittleManComputer()
    computer.assemble(program)
    computer.run()

