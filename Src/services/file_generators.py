# This file is used to generate common code that cannot be abstracted normally and easily.
# Running this file will generate possible missing definitions and stop the ide from getting mad at missing values

def generate_file(file_name: str, imports: list[str], code_blocks: list[str]):
    with open(file_name, 'w') as f:
        f.write("# THIS FILE WAS AUTOGENERATED THROUGH file_generator.py\n\n")
        f.writelines([a + '\n' for a in imports])
        f.write("\n")
        f.writelines([a + '\n' for a in code_blocks])


def generate_generic_dataclass(name: str, fields: dict = None) -> str:
    # Generate the new class as a string to execute
    if not fields or len(fields) < 2:
        raise ValueError("fields must be defined with at least 2 pairs")

    # Class name
    cls = f"""
@dataclass
class {name}:\n
"""
    # class fields
    for k, v in fields.items():
        cls += f"    {k}: {v.__name__}\n"

    # prep names
    init_vars = "=None, ".join(fields.keys())
    cls += f"\n    def __init__(self, {init_vars}=None):\n"
    # rest of init
    cls += f"""        if not data_or_name:
            raise ValueError("No parameters given")
        elif isinstance(data_or_name, dict):
            self._load_dict(data_or_name)
        elif isinstance(data_or_name, str) and not {list(fields.keys())[1]}:
            # Assume only json string is passed
            self._load_dict(json.loads(data_or_name))
        else:\n""".replace("data_or_name", list(fields.keys())[0])  # prob need new line
    # init else section
    for a in fields.keys():
        cls += f"            self.{a} = {a}\n"
    # add load_dict
    cls += "\n    def _load_dict(self, data: dict):\n"
    for a in fields.keys():
        cls += f'        self.{a} = data["{a}"]\n'
    # final methods
    cls += """\n    def _to_dict(self):
        return dataclasses.asdict(self)

    def dumps(self):
        return json.dumps(self._to_dict())\n"""

    return cls


structures = list()
structures.append(generate_generic_dataclass("FileToken", {"file_name": str, "hash_val": str, "auth_val": str, "valid_until": int}))
structures.append(generate_generic_dataclass("FileIndex", {"file_name": str, "hash_val": str, "size": int, "lost_access": int}))
generate_file("data_structures.py", ["import dataclasses", "from dataclasses import dataclass", "import json"], structures)
