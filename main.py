# Nomes da ABI para os 32 registros inteiros
ABI_NAMES = [
    "zero",
    "ra",
    "sp",
    "gp",
    "tp",
    "t0",
    "t1",
    "t2",
    "s0",
    "s1",
    "a0",
    "a1",
    "a2",
    "a3",
    "a4",
    "a5",
    "a6",
    "a7",
    "s2",
    "s3",
    "s4",
    "s5",
    "s6",
    "s7",
    "s8",
    "s9",
    "s10",
    "s11",
    "t3",
    "t4",
    "t5",
    "t6",
]

# Tabela de CPI padrão (pode ser alterada conforme necessário)
CPI_TABLE = {"R": 1.0, "I": 1.0, "S": 2.0, "B": 3.0, "U": 1.0, "J": 2.0}


def sign_extend(value, bits):
    # Aplica extensão de sinal a um valor com uma quantidade específica de bits.
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)


def decode_instruction(word, pc):
    # Decodifica uma única palavra de instrução de 32 bits.
    opcode = word & 0x7F
    rd = (word >> 7) & 0x1F
    funct3 = (word >> 12) & 0x7
    rs1 = (word >> 15) & 0x1F
    rs2 = (word >> 20) & 0x1F
    funct7 = (word >> 25) & 0x7F

    fmt = "Desconhecido"
    mnemonic = "inválido"
    fields = {}
    assembly = "Instrução inválida"

    rd_abi = ABI_NAMES[rd]
    rs1_abi = ABI_NAMES[rs1]
    rs2_abi = ABI_NAMES[rs2]

    # Identificação dos formatos e mnemônicos
    if opcode == 0x33:  # Tipo R
        fmt = "R"
        fields = {"rd": rd, "rs1": rs1, "rs2": rs2, "f3": funct3, "f7": funct7}

        if funct3 == 0x0 and funct7 == 0x00:
            mnemonic = "add"
        elif funct3 == 0x0 and funct7 == 0x20:
            mnemonic = "sub"
        elif funct3 == 0x1 and funct7 == 0x00:
            mnemonic = "sll"
        elif funct3 == 0x2 and funct7 == 0x00:
            mnemonic = "slt"
        elif funct3 == 0x3 and funct7 == 0x00:
            mnemonic = "sltu"
        elif funct3 == 0x4 and funct7 == 0x00:
            mnemonic = "xor"
        elif funct3 == 0x5 and funct7 == 0x00:
            mnemonic = "srl"
        elif funct3 == 0x5 and funct7 == 0x20:
            mnemonic = "sra"
        elif funct3 == 0x6 and funct7 == 0x00:
            mnemonic = "or"
        elif funct3 == 0x7 and funct7 == 0x00:
            mnemonic = "and"

        assembly = f"{mnemonic} {rd_abi}, {rs1_abi}, {rs2_abi}"

    elif opcode in [0x13, 0x03, 0x67]:  # Tipo I
        fmt = "I"
        imm = sign_extend((word >> 20) & 0xFFF, 12)

        fields = {"rd": rd, "rs1": rs1, "imm": imm, "f3": funct3}

        if opcode == 0x13:  # OP-IMM
            if funct3 == 0x0:
                mnemonic = "addi"
            elif funct3 == 0x2:
                mnemonic = "slti"
            elif funct3 == 0x3:
                mnemonic = "sltiu"
            elif funct3 == 0x4:
                mnemonic = "xori"
            elif funct3 == 0x6:
                mnemonic = "ori"
            elif funct3 == 0x7:
                mnemonic = "andi"
            elif funct3 == 0x1:
                mnemonic = "slli"
                fields["imm"] = imm & 0x1F
            elif funct3 == 0x5:
                mnemonic = "srli" if funct7 == 0x00 else "srai"
                fields["imm"] = imm & 0x1F

            assembly = f"{mnemonic} {rd_abi}, {rs1_abi}, {fields['imm']}"

            # Pseudoinstrução: nop
            if mnemonic == "addi" and rd == 0 and rs1 == 0 and imm == 0:
                assembly = "nop"

        elif opcode == 0x03:  # Instruções de carregamento
            if funct3 == 0x0:
                mnemonic = "lb"
            elif funct3 == 0x1:
                mnemonic = "lh"
            elif funct3 == 0x2:
                mnemonic = "lw"
            elif funct3 == 0x4:
                mnemonic = "lbu"
            elif funct3 == 0x5:
                mnemonic = "lhu"

            assembly = f"{mnemonic} {rd_abi}, {imm}({rs1_abi})"

        elif opcode == 0x67:  # JALR
            mnemonic = "jalr"

            target = (pc + imm) if rs1 == 0 else "abs_depende_reg"

            assembly = f"jalr {rd_abi}, {imm}({rs1_abi})"

            # Pseudoinstrução: ret
            if rd == 0 and rs1 == 1 and imm == 0:
                assembly = "ret"

    elif opcode == 0x23:  # Tipo S
        fmt = "S"

        imm = sign_extend(((word >> 25) << 5) | ((word >> 7) & 0x1F), 12)

        fields = {"rs1": rs1, "rs2": rs2, "imm": imm, "f3": funct3}

        if funct3 == 0x0:
            mnemonic = "sb"
        elif funct3 == 0x1:
            mnemonic = "sh"
        elif funct3 == 0x2:
            mnemonic = "sw"

        assembly = f"{mnemonic} {rs2_abi}, {imm}({rs1_abi})"

    elif opcode == 0x63:  # Tipo B
        fmt = "B"

        imm = ((word >> 31) & 0x1) << 12
        imm |= ((word >> 7) & 0x1) << 11
        imm |= ((word >> 25) & 0x3F) << 5
        imm |= ((word >> 8) & 0xF) << 1
        imm = sign_extend(imm, 13)

        fields = {"rs1": rs1, "rs2": rs2, "imm": imm, "f3": funct3}

        if funct3 == 0x0:
            mnemonic = "beq"
        elif funct3 == 0x1:
            mnemonic = "bne"
        elif funct3 == 0x4:
            mnemonic = "blt"
        elif funct3 == 0x5:
            mnemonic = "bge"
        elif funct3 == 0x6:
            mnemonic = "bltu"
        elif funct3 == 0x7:
            mnemonic = "bgeu"

        target = pc + imm
        assembly = f"{mnemonic} {rs1_abi}, {rs2_abi}, {hex(target)}"

    elif opcode in [0x37, 0x17]:  # Tipo U
        fmt = "U"

        imm = sign_extend(word & 0xFFFFF000, 32)

        fields = {"rd": rd, "imm": imm}

        mnemonic = "lui" if opcode == 0x37 else "auipc"

        assembly = f"{mnemonic} {rd_abi}, {hex((word >> 12) & 0xFFFFF)}"

    elif opcode == 0x6F:  # Tipo J
        fmt = "J"

        imm = ((word >> 31) & 0x1) << 20
        imm |= ((word >> 12) & 0xFF) << 12
        imm |= ((word >> 20) & 0x1) << 11
        imm |= ((word >> 21) & 0x3FF) << 1
        imm = sign_extend(imm, 21)

        fields = {"rd": rd, "imm": imm}

        mnemonic = "jal"

        target = pc + imm
        assembly = f"jal {rd_abi}, {hex(target)}"

        # Pseudoinstrução: j
        if rd == 0:
            assembly = f"j {hex(target)}"

    return {
        "word": word,
        "fmt": fmt,
        "mnemonic": mnemonic,
        "fields": fields,
        "assembly": assembly,
        "is_valid": fmt != "Desconhecido",
    }


def process_file(filepath, base_pc=0x00000000):
    # Lê o arquivo, remove formatações desnecessárias e processa as instruções.
    instructions = []

    stats = {"R": 0, "I": 0, "S": 0, "B": 0, "U": 0, "J": 0}

    valid_count = 0
    pc = base_pc

    with open(filepath, "r") as f:
        for line in f:
            original_line = line.split("#")[0].split("//")[0].strip()

            if not original_line:
                continue

            clean_line = original_line.lower().replace("0x", "")

            # Detecta automaticamente se o valor está em binário ou hexadecimal.
            if all(c in "01" for c in clean_line) and len(clean_line) > 8:
                word = int(clean_line, 2)
            else:
                word = int(clean_line, 16)

            dec = decode_instruction(word, pc)
            instructions.append((pc, dec))

            if dec["is_valid"]:
                stats[dec["fmt"]] += 1
                valid_count += 1

            pc += 4

    # Impressão da saída R4
    print(
        f"{'Endereço':<10} | "
        f"{'Instrução':<10} | "
        f"{'Fmt':<3} | "
        f"{'Mnemônico':<10} | "
        f"{'Campos Extraídos':<35} | "
        f"Assembly"
    )

    print("-" * 100)

    for pc, dec in instructions:
        word_hex = f"0x{dec['word']:08X}"

        if not dec["is_valid"]:
            print(
                f"0x{pc:08X} | "
                f"{word_hex:<10} | "
                f"INV | "
                f"{'-':<10} | "
                f"{'-':<35} | "
                f"Instrução inválida"
            )
            continue

        fields_str = " ".join([f"{k}={v}" for k, v in dec["fields"].items()])

        print(
            f"0x{pc:08X} | "
            f"{word_hex:<10} | "
            f"{dec['fmt']:<3} | "
            f"{dec['mnemonic']:<10} | "
            f"{fields_str:<35} | "
            f"{dec['assembly']}"
        )

    # Impressão do relatório estatístico e cálculo do CPI
    print("\n" + "=" * 50)
    print("RELATÓRIO ESTATÍSTICO")
    print("=" * 50)

    total_cycles = 0.0

    if valid_count > 0:
        for fmt, count in stats.items():
            perc = (count / valid_count) * 100

            total_cycles += count * CPI_TABLE.get(fmt, 1.0)

            print(f"Formato {fmt}: " f"{count} instruções ({perc:.1f}%)")

        cpi_medio = total_cycles / valid_count

        print(f"\nCPI Médio Estimado: {cpi_medio:.2f}")

    else:
        print("Nenhuma instrução válida encontrada no arquivo.")


arquivo = "instructions.txt"
process_file(arquivo, base_pc=0x00000000)
