from abc import ABC, abstractmethod


class LittleManComputer(ABC):
    RAM_SIZE = 100

    def __init__(self):
        self._ram = [0 for _ in range(self.RAM_SIZE)]
        self._program_counter = 0
        self._accumulator = 0
        self._instruction_register = 0
        self._address_register = 0

    @abstractmethod
    def assemble(self, program: str):
        pass

    def run(self):
        while True:
            instruction_address = self._program_counter
            self._program_counter += 1
            instruction = self._fetch(instruction_address)
            operation, operand = self.__decode_instruction(instruction)
            try:
                self._execute_instruction(operation, operand)
            except self.ProgramHalt:
                break

    def _fetch(self, address: int):
        return self._ram[address]

    def _write(self, address: int, content: int):
        self._ram[address] = content

    def __decode_instruction(self, instruction: int):
        return instruction // 100, instruction % 100

    @abstractmethod
    def _execute_instruction(self, operation, operand):
        pass

    class InvalidInstructionException(Exception):
        pass

    class ProgramHalt(Exception):
        pass


class LmcImplementation(LittleManComputer):
    class MnemonicsParser:
        mnemonic_dict = {
            'ADD': 1,
            'SUB': 2,
            'STA': 3,
            'LDA': 5,
            'BRA': 6,
            'BRZ': 7,
            'BRP': 8,
            'INP': 901,
            'OUT': 902,
            'HLT': 0
        }

        def __init__(self):
            self.code = ''
            self.lines = []
            self.label_map = {}

        def parse(self, code: str):
            self.lines = code.split('\n')
            self.lines = [self.__split_tokens(line) for line in self.lines if line]
            self.__remove_comments()
            self.__extract_labels()
            return self.__decode_mnemonics()

        @staticmethod
        def __split_tokens(line):
            return [token for token in line.split(' ') if token != '']

        def __remove_comments(self):
            return [tokens for tokens in self.lines if not tokens[0].startswith('#')]

        def __extract_labels(self):
            for address in range(len(self.lines)):
                tokens = self.lines[address]
                if len(tokens) < 2:
                    continue
                first_token = tokens[0]
                if first_token not in self.mnemonic_dict:
                    self.label_map[first_token] = address
                    self.lines[address] = tokens[1:]

        def __decode_mnemonics(self):
            machine_code = []
            for tokens in self.lines:
                first_token = tokens[0]
                if first_token == 'DAT':
                    machine_code.append(int(tokens[1]) if len(tokens) == 2 else 0)
                    continue
                opcode = self.mnemonic_dict[first_token]
                if len(tokens) == 1:
                    machine_code.append(opcode)
                elif len(tokens) == 2:
                    operand = tokens[1]
                    try:
                        operand_address = int(operand)
                    except ValueError:
                        operand_address = self.label_map[operand]
                    machine_code.append(opcode * 100 + operand_address)
            return machine_code

    def assemble(self, program: str):
        parser = self.MnemonicsParser()
        machine_code = parser.parse(program)
        self._ram[:len(machine_code)] = machine_code

    def _execute_instruction(self, operation, operand):
        self.instruction_map[operation](self, operand)

    def __impl_addition(self, operand):
        self._accumulator += self._fetch(operand)

    def __impl_subtraction(self, operand):
        self._accumulator -= self._fetch(operand)

    def __impl_store(self, operand):
        self._write(operand, self._accumulator)

    def __impl_load(self, operand):
        self._accumulator = self._fetch(operand)

    def __impl_branch(self, operand):
        self._program_counter = operand

    def __impl_branch_zero(self, operand):
        if self._accumulator == 0:
            self._program_counter = operand

    def __impl_branch_positive(self, operand):
        if self._accumulator > 0:
            self._program_counter = operand

    def __impl_io(self, operand):
        if operand == 1:
            self.__impl_input()
        elif operand == 2:
            self.__impl_output()
        else:
            raise self.InvalidInstructionException

    def __impl_input(self):
        self._accumulator = int(input('Input required:'))

    def __impl_output(self):
        print('Output: ', self._accumulator)

    def __impl_halt(self, operand):
        if operand == 0:
            raise self.ProgramHalt
        else:
            raise self.InvalidInstructionException

    instruction_map = {
        0: __impl_halt,
        1: __impl_addition,
        2: __impl_subtraction,
        3: __impl_store,
        5: __impl_load,
        6: __impl_branch,
        7: __impl_branch_zero,
        8: __impl_branch_positive,
        9: __impl_io
    }
