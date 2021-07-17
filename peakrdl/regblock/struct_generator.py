from typing import TYPE_CHECKING, Optional, List
import textwrap

from systemrdl.walker import RDLListener, RDLWalker

if TYPE_CHECKING:
    from typing import Union

    from systemrdl.node import AddrmapNode, RegfileNode, RegNode, FieldNode, Node


class _StructBase:
    def __init__(self):
        self.children = [] # type: Union[str, _StructBase]

    def __str__(self) -> str:
        s = '\n'.join((str(x) for x in self.children))
        return textwrap.indent(s, "    ")


class _AnonymousStruct(_StructBase):
    def __init__(self, inst_name: str, array_dimensions: Optional[List[int]] = None):
        super().__init__()
        self.inst_name = inst_name
        self.array_dimensions = array_dimensions

    def __str__(self) -> str:
        if self.array_dimensions:
            suffix = "[" + "][".join((str(n) for n in self.array_dimensions)) + "]"
        else:
            suffix = ""

        return (
            "struct {\n"
            + super().__str__()
            + f"\n}} {self.inst_name}{suffix};"
        )


class _TypedefStruct(_StructBase):
    def __init__(self, type_name: str):
        super().__init__()
        self.type_name = type_name

    def __str__(self) -> str:
        return (
            "typedef struct {\n"
            + super().__str__()
            + f"\n}} {self.type_name};"
        )


class StructGenerator:

    def __init__(self):
        self._struct_stack = []

    @property
    def current_struct(self) -> _StructBase:
        return self._struct_stack[-1]


    def push_struct(self, inst_name: str, array_dimensions: Optional[List[int]] = None) -> None:
        s = _AnonymousStruct(inst_name, array_dimensions)
        self._struct_stack.append(s)


    def add_member(self, name: str, width: int = 1, array_dimensions: Optional[List[int]] = None) -> None:
        if array_dimensions:
            suffix = "[" + "][".join((str(n) for n in array_dimensions)) + "]"
        else:
            suffix = ""

        if width == 1:
            m = f"logic {name}{suffix};"
        else:
            m = f"logic [{width-1}:0] {name}{suffix};"
        self.current_struct.children.append(m)


    def pop_struct(self) -> None:
        s = self._struct_stack.pop()

        if s.children:
            # struct is not empty. Attach it to the parent
            self.current_struct.children.append(s)


    def start(self, type_name: str):
        assert not self._struct_stack
        s = _TypedefStruct(type_name)
        self._struct_stack.append(s)

    def finish(self) -> Optional[str]:
        s = self._struct_stack.pop()
        assert not self._struct_stack

        if not s.children:
            return None
        return str(s)


class RDLStructGenerator(StructGenerator, RDLListener):
    """
    Struct generator that naively translates an RDL node tree into a single
    struct typedef containing nested anonymous structs

    This can be extended to add more intelligent behavior
    """

    def get_struct(self, node: 'Node', type_name: str) -> Optional[str]:
        self.start(type_name)

        walker = RDLWalker()
        walker.walk(node, self, skip_top=True)

        return self.finish()


    def enter_Addrmap(self, node: 'AddrmapNode') -> None:
        self.push_struct(node.inst_name, node.array_dimensions)

    def exit_Addrmap(self, node: 'AddrmapNode') -> None:
        self.pop_struct()

    def enter_Regfile(self, node: 'RegfileNode') -> None:
        self.push_struct(node.inst_name, node.array_dimensions)

    def exit_Regfile(self, node: 'RegfileNode') -> None:
        self.pop_struct()

    def enter_Reg(self, node: 'RegNode') -> None:
        self.push_struct(node.inst_name, node.array_dimensions)

    def exit_Reg(self, node: 'RegNode') -> None:
        self.pop_struct()

    def enter_Field(self, node: 'FieldNode') -> None:
        self.add_member(node.inst_name, node.width)
