"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256                   # Create memory
        self.reg = [0] * 8                     # Create registers
        self.pc = 0                            # Program counter for reading instructions
        self.SP = 7                            # register location for top of stack
        self.fl = 0b00000000   # 00000LGE      # Flag for CMP instruction
        self.reg[self.SP] = len(self.ram) - 1  # store top of stack in register 7
        self.branchtable = {}                  # Create storage for Instruction Handlers
        self.running = False                   # Create CPU state


    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self, program):
        """Load a program into memory."""
        address = 0

        if len(program) != 2:   # check for second argument from command line
            print('need proper filename passed')
            sys.exit(1)

        filename = program[1]

        with open(filename) as f:
            for line in f:
                # print(line)
                if line == '\n' or line == '':    # skip empty lines
                    continue
                if line[0] == '#':  # skip lines that are comments
                    continue
                
                comment_split = line.split('#')  # everything before (#) and everything after

                num = comment_split[0].strip()   # save everything before (#) to num variable

                self.ram[address] = int(num,2)   # convert binary to int, and save to memory
                # print(int(num,2))
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'CMP':
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001                    # E flag
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010                    # G flag
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100                    # L flag
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()



    def handle_LDI(self, op_a, op_b):
        self.reg[op_a] = op_b                         # Save the value at given address
        self.pc += 3

    def handle_PRN(self, op_a, op_b):
        value = self.reg[op_a]
        print(value)                                  # Print from given address
        self.pc += 2

    def handle_MUL(self, op_a, op_b):
        self.alu('MUL', op_a, op_b)
        self.pc += 3

    def handle_ADD(self, op_a, op_b):
        self.alu('ADD', op_a, op_b)
        self.pc += 3

    def handle_CMP(self, op_a, op_b):
        self.alu('CMP', op_a, op_b)
        self.pc += 3

    def handle_HLT(self, op_a, op_b):
        self.running = False                          # Stop the loop/end program
        self.pc += 1

    def handle_PUSH(self, op_a, op_b):
        self.reg[self.SP] -= 1                        # decrement the Stack Pointer
        reg_value = self.reg[op_a]                    # Save the value of given register
        self.ram[self.reg[self.SP]] = reg_value       # Add the given value to the stack
        self.pc += 2

    def handle_POP(self, op_a, op_b):
        reg_value = self.ram[self.reg[self.SP]]       # POP value in stack at SP
        self.reg[op_a] = reg_value                    # Store value in given register
        self.reg[self.SP] += 1                        # increment the Stack Pointer
        self.pc += 2

    def handle_CALL(self, op_a, op_b):
        self.reg[self.SP] -= 1                        # decrement the SP
        self.ram[self.reg[self.SP]] = self.pc + 2     # store, on to the Stack, the instruction to return to after the CALL
        self.pc = self.reg[op_a]                      # set the PC to the given value

    def handle_RET(self, op_a, op_b):
        return_address = self.ram[self.reg[self.SP]]  # Retrieve the instruction to return to, from the Stack
        self.reg[self.SP] += 1                        # Increment the SP
        self.pc = return_address                      # Set PC to the return address

    def handle_JMP(self, op_a, op_b):
        self.pc = self.reg[op_a]                      # set the PC to the value at given address

    def handle_JEQ(self, op_a, op_b):
        if self.fl == 0b00000001:                     # if flag is set to Equal
            self.pc = self.reg[op_a]                  # set the PC to the value at given address
        else:
            self.pc += 2



    def run(self):
        """Run the CPU."""
        self.running = True

        HLT =  1      # Halt
        RET =  17     # Retrun Instruction
        PUSH = 69     # PUSH to stack
        POP =  70     # POP off stack
        PRN =  71     # Print Instruction
        CALL = 80     # Call Instruction
        JMP =  84     # Jump Instruction
        JEQ =  85     # Jump if Equal Instruction
        LDI =  130    # Load Instruction
        ADD =  160    # Add Instruction
        MUL =  162    # Multiply Instruction
        CMP =  167    # Compare Instruction

        self.branchtable[LDI] = self.handle_LDI   ###\
        self.branchtable[PUSH] = self.handle_PUSH    #\
        self.branchtable[POP] = self.handle_POP       #\
        self.branchtable[PRN] = self.handle_PRN        #\    
        self.branchtable[ADD] = self.handle_ADD         #\
        self.branchtable[CMP] = self.handle_CMP            #----- Set handlers to corresponding Instruction call
        self.branchtable[MUL] = self.handle_MUL          #/
        self.branchtable[HLT] = self.handle_HLT         #/
        self.branchtable[JMP] = self.handle_JMP        #/
        self.branchtable[JEQ] = self.handle_JEQ       #/
        self.branchtable[CALL] = self.handle_CALL    #/
        self.branchtable[RET] = self.handle_RET   ###/

        while self.running:
            # break

            IR = self.ram_read(self.pc)             # Instruction Register
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)

            if IR in self.branchtable:              # If the instruction is in branchtable, call the handler
                self.branchtable[IR](operand_a, operand_b)

            else:
                # if command is not recognizable
                print(f"Unknown instruction {IR}")
                sys.exit(1)    # Terminate program with error
