import re
import pprint

serial = {'A': 'add', 'B': 'addi', 'C': 'sub', 'D': 'subi', 'E': 'and', 'F': 'andi', 'G': 'or', 'H': 'ori', 'I': 'sll', 'J': 'srl', 'K': 'nor', 'L': 'lw', 'M': 'sw', 'N': 'beq', 'O': 'bneq', 'P': 'j'}

sequence = 'KHCILNFDMPOEGBJA' 
instruction = {}

for i in range(len(sequence)):
    instruction[serial[sequence[i]]] = bin(i)[2:].zfill(4)


registers = {'$zero': '0000', '$t0': '0111', '$t1': '0001', '$t2': '0010', '$t3': '0011', '$t4': '0100', '$sp': '0110'}

R_TYPE = ['add', 'sub', 'and', 'or', 'nor']
S_TYPE = ['sll', 'srl']
I_TYPE = ['addi', 'subi', 'andi', 'ori', 'beq', 'bneq', 'lw', 'sw']
J_TYPE = ['j']

labels = {}

def generate_label_location(lines):
    changed_lines = []
    for line in lines:
        if ':' in line:
            parts = [part.strip() for part in line.split(':')]
            labels[parts[0]] = len(changed_lines)
            if parts[1] != '':
                changed_lines.append(parts[1])
        else:
            changed_lines.append(line)
    return changed_lines

def change(line_no, opcode, *args):
    if opcode not in instruction:
        return "0000000000000000"
    
    bin_instruction = instruction[opcode]
    
    if opcode in R_TYPE:
        bin_instruction += registers[args[1]] + registers[args[2]] + registers[args[0]]
    
    elif opcode in S_TYPE:
        bin_instruction += registers[args[1]] + registers[args[0]] + bin(int(args[2]))[2:].zfill(4)
    
    elif opcode in I_TYPE:
        if opcode in I_TYPE[:6]: # addi, subi, andi, ori, beq, bneq
            bin_instruction += registers[args[1]]
            if opcode in I_TYPE[:4]:
                immediate = int(args[2])
            else: # beq, bneq
                immediate = labels[args[2]] - (line_no + 1)
        else: # sw, lw
            bin_instruction += registers[args[2]]
            immediate = int(args[1])
            
        bin_instruction += registers[args[0]]
        if immediate < 0: immediate = 16 + immediate
        bin_instruction += bin(immediate & 0xF)[2:].zfill(4)
    
    elif opcode in J_TYPE:
        target = args[0]
        addr = labels[target] if target in labels else int(target)
        bin_instruction += bin(addr)[2:].zfill(8) + '0000'
    
    return bin_instruction

if __name__ == '__main__':
    print('Your Opcodes based on sequence KHCILNFDMPOEGBJA:')
    pprint.pprint(instruction)

    with open('input.asm', 'r') as file:
        lines = [line.split('//')[0].strip() for line in file if line.strip()]

    
    original_lines = lines
    lines = ['addi $sp, $zero, 15'] # Auto initialization
    for line in original_lines:
        matched = re.search(r'(push|pop)[ ]+(\$t[0-4])', line)
        if matched is None:
            lines.append(line)
        else:
            if matched.group(1) == 'push':
                lines.append(f'sw {matched.group(2)}, 0($sp)')
                lines.append('subi $sp, $sp, 1')
            else:
                lines.append('addi $sp, $sp, 1')
                lines.append(f'lw {matched.group(2)}, 0($sp)')

    lines = generate_label_location(lines)
    

    output_hex = []
    output_bin = [] 

    for i in range(len(lines)):
        parts = re.split(r'[ \t,\(\)]+', lines[i])
        bin_line = change(i, *parts)
        hex_val = hex(int(bin_line, 2))[2:].zfill(4)
        
        output_hex.append(hex_val + '\n')
        
        formatted_bin = f"{bin_line[:4]} {bin_line[4:8]} {bin_line[8:12]} {bin_line[12:]}"
        output_bin.append(f"{lines[i].ljust(25)} : {formatted_bin}\n")
        
        print(f"{lines[i].ljust(25)} : {formatted_bin} -> {hex_val}")

    
    with open('output.hex', 'w') as f:
        f.write("v2.0 raw\n")
        f.writelines(output_hex)

    
    with open('machine_code.txt', 'w') as f:
        f.writelines(output_bin)
    
    print("\nSuccess! 'output.hex' and 'machine_code.txt' have been generated.")