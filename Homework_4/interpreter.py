import yaml


def get_command_info_by_number(cmd_num):
    if cmd_num == 32:
        return "CONST", [6, 26, 16], 6
    elif cmd_num == 51:
        return "READ", [6, 8, 26, 26], 9
    elif cmd_num == 56:
        return "WRITE", [6, 26, 26], 8
    elif cmd_num == 54:
        return "DIV", [6, 26, 26, 8, 26], 12
    else:
        raise ValueError(f"Unknown command number: {cmd_num}")


def extract_parts(file, byte):
    cmd_num = int.from_bytes(byte) >> 2
    _, layout, size = get_command_info_by_number(cmd_num)
    command = int.from_bytes(byte) << ((size - 1) * 8)
    command |= int.from_bytes(file.read(size - 1))
    shift = 0
    result = []
    for field_size in layout:
        shift += field_size
        result.append((command >> (size * 8 - shift)) & (2 ** field_size - 1))
    return result


def run(input_path, output_path):
    memory = {}
    with open(input_path, 'rb') as file:
        byte = file.read(1)
        while byte:
            parts = extract_parts(file, byte)
            if parts:
                cmd_name, _, _ = get_command_info_by_number(parts[0])
                if cmd_name == "CONST":
                    memory[parts[1]] = parts[2]
                elif cmd_name == "READ":
                    memory[parts[3]] = memory.get(memory[parts[2]] + parts[1], 0)
                elif cmd_name == "WRITE":
                    memory[parts[1]] = memory.get(parts[2], 0)
                elif cmd_name == "DIV":
                    memory[parts[1]] = memory.get(parts[4], 0) // memory.get(memory.get(parts[2], 0) + parts[3], 1)
                else:
                    raise Exception("Unknown command")
            else:
                raise Exception("Bad instruction")
            byte = file.read(1)
    with open(output_path, 'w') as result_file:
        yaml.dump(memory, result_file)


if __name__ == "__main__":
    run("p.bin", "out.yaml")
