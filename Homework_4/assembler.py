import yaml


def get_command_info(command):
    if command == "CONST":
        return 32, [6, 26, 16], 6
    elif command == "READ":
        return 51, [6, 8, 26, 26], 9
    elif command == "WRITE":
        return 56, [6, 26, 26], 8
    elif command == "DIV":
        return 54, [6, 26, 26, 8, 26], 12
    else:
        raise ValueError(f"Unknown command: {command}")


def encode_instruction(command, params):
    cmd_number, layout, size = get_command_info(command)
    shift = 8 * size
    instruction = 0
    for index, value in enumerate([cmd_number, *params]):
        shift -= layout[index]
        if value >= 2 ** layout[index]:
            raise ValueError("Value too large")
        instruction |= (value << shift)
    return instruction.to_bytes(size, byteorder='big')


def format_instruction_log(command, params):
    cmd_number, _, _ = get_command_info(command)
    return ", ".join(f"{name}={param}" for name, param in zip("ABCDEF", [cmd_number, *params]))


def process_file(input_path, output_path, log_path):
    instructions = []
    log_entries = []
    with open(input_path, 'r') as infile:
        for line in infile:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            command = parts[0]
            params = [int(pair.split("=")[1]) for pair in parts[1:]]
            instructions.append(encode_instruction(command, params))
            log_entries.append(format_instruction_log(command, params))
    with open(output_path, 'wb') as bin_file:
        bin_file.write(b''.join(instructions))
    with open(log_path, 'w') as log_file:
        yaml.dump(log_entries, log_file)


if __name__ == "__main__":
    process_file("in.txt", "p.bin", "log.yaml")
