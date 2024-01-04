from typing import TYPE_CHECKING, Optional, List
import textwrap
from collections import OrderedDict

from systemrdl.walker import RDLListener, RDLWalker

from .identifier_filter import kw_filter as kwf

if TYPE_CHECKING:
    from typing import Union

    from systemrdl.node import AddrmapNode, RegfileNode, RegNode, FieldNode, Node, MemNode


class _StructBase:
    def __init__(self) -> None:
        self.children = [] # type: List[Union[str, _StructBase]]

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
    def __init__(self, type_name: str, inst_name: Optional[str] = None, array_dimensions: Optional[List[int]] = None):
        super().__init__()
        self.type_name = type_name
        self.inst_name = inst_name
        self.array_dimensions = array_dimensions

    def __str__(self) -> str:
        return (
            "typedef struct {\n"
            + super().__str__()
            + f"\n}} {self.type_name};"
        )

    @property
    def instantiation(self) -> str:
        if self.array_dimensions:
            suffix = "[" + "][".join((str(n) for n in self.array_dimensions)) + "]"
        else:
            suffix = ""

        return f"{self.type_name} {self.inst_name}{suffix};"

#-------------------------------------------------------------------------------

class StructGenerator:

    def __init__(self) -> None:
        self._struct_stack = [] # type: List[_StructBase]

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


    def start(self, type_name: str) -> None:
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
        self.push_struct(kwf(node.inst_name), node.array_dimensions)

    def exit_Addrmap(self, node: 'AddrmapNode') -> None:
        self.pop_struct()

    def enter_Regfile(self, node: 'RegfileNode') -> None:
        self.push_struct(kwf(node.inst_name), node.array_dimensions)

    def exit_Regfile(self, node: 'RegfileNode') -> None:
        self.pop_struct()

    def enter_Mem(self, node: 'MemNode') -> None:
        self.push_struct(kwf(node.inst_name), node.array_dimensions)

    def exit_Mem(self, node: 'MemNode') -> None:
        self.pop_struct()

    def enter_Reg(self, node: 'RegNode') -> None:
        self.push_struct(kwf(node.inst_name), node.array_dimensions)

    def exit_Reg(self, node: 'RegNode') -> None:
        self.pop_struct()

    def enter_Field(self, node: 'FieldNode') -> None:
        self.add_member(kwf(node.inst_name), node.width)

#-------------------------------------------------------------------------------

class FlatStructGenerator(StructGenerator):

    def __init__(self) -> None:
        super().__init__()
        self.typedefs = OrderedDict() # type: OrderedDict[str, _TypedefStruct]

    def push_struct(self, type_name: str, inst_name: str, array_dimensions: Optional[List[int]] = None) -> None: # type: ignore # pylint: disable=arguments-renamed
        s = _TypedefStruct(type_name, inst_name, array_dimensions)
        self._struct_stack.append(s)

    def pop_struct(self) -> None:
        s = self._struct_stack.pop()
        assert isinstance(s, _TypedefStruct)

        if s.children:
            # struct is not empty. Attach it to the parent
            self.current_struct.children.append(s.instantiation)

            # Add to collection of struct definitions
            if s.type_name not in self.typedefs:
                self.typedefs[s.type_name] = s

    def finish(self) -> Optional[str]:
        s = self._struct_stack.pop()
        assert isinstance(s, _TypedefStruct)
        assert not self._struct_stack

        # no children, no struct.
        if not s.children:
            return None

        # Add to collection of struct definitions
        if s.type_name not in self.typedefs:
            self.typedefs[s.type_name] = s

        all_structs = [str(s) for s in self.typedefs.values()]

        return "\n\n".join(all_structs)


class RDLFlatStructGenerator(FlatStructGenerator, RDLListener):
    """
    Struct generator that naively translates an RDL node tree into a flat list
    of typedefs

    This can be extended to add more intelligent behavior
    """

    def get_typdef_name(self, node:'Node') -> str:
        raise NotImplementedError

    def get_struct(self, node: 'Node', type_name: str) -> Optional[str]:
        self.start(type_name)

        walker = RDLWalker()
        walker.walk(node, self, skip_top=True)

        return self.finish()

    def enter_Addrmap(self, node: 'AddrmapNode') -> None:
        type_name = self.get_typdef_name(node)
        self.push_struct(type_name, kwf(node.inst_name), node.array_dimensions)

    def exit_Addrmap(self, node: 'AddrmapNode') -> None:
        self.pop_struct()

    def enter_Regfile(self, node: 'RegfileNode') -> None:
        type_name = self.get_typdef_name(node)
        self.push_struct(type_name, kwf(node.inst_name), node.array_dimensions)

    def exit_Regfile(self, node: 'RegfileNode') -> None:
        self.pop_struct()

    def enter_Mem(self, node: 'MemNode') -> None:
        type_name = self.get_typdef_name(node)
        self.push_struct(type_name, kwf(node.inst_name), node.array_dimensions)

    def exit_Mem(self, node: 'MemNode') -> None:
        self.pop_struct()

    def enter_Reg(self, node: 'RegNode') -> None:
        type_name = self.get_typdef_name(node)
        self.push_struct(type_name, kwf(node.inst_name), node.array_dimensions)

    def exit_Reg(self, node: 'RegNode') -> None:
        self.pop_struct()

    def enter_Field(self, node: 'FieldNode') -> None:
        self.add_member(kwf(node.inst_name), node.width)
