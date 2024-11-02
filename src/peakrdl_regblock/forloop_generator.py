from typing import TYPE_CHECKING, Optional, List, Union
import textwrap

from systemrdl.walker import RDLListener, RDLWalker

if TYPE_CHECKING:
    from systemrdl.node import AddressableNode, Node

class Body:

    def __init__(self) -> None:
        self.children = [] # type: List[Union[str, Body]]

    def __str__(self) -> str:
        s = '\n'.join((str(x) for x in self.children))
        return s

class LoopBody(Body):
    def __init__(self, dim: int, iterator: str, loop_type: str, label: Union[str, None] = None) -> None:
        super().__init__()
        self.dim = dim
        self.iterator = iterator
        self.loop_type = loop_type
        self.label = label
        if self.loop_type.lower() == "generate" and not label:
            raise ValueError("generate block must have a label")

    def __str__(self) -> str:
        s = super().__str__()
        if self.label is None:
            label = ""
        else:
            label = self.label + ": "
        return (
            f"{label}for {self.iterator} in 0 to {self.dim-1} {self.loop_type}\n"
            + textwrap.indent(s, "    ")
            + f"\nend {self.loop_type};"
        )


class ForLoopGenerator:
    loop_type = "loop"
    loop_body_cls = LoopBody

    def __init__(self) -> None:
        self._loop_level = 0
        self._stack = [] # type: List[Body]

    @property
    def current_loop(self) -> Body:
        return self._stack[-1]

    def push_loop(self, dim: int, label: Union[str | None] = None) -> None:
        i = f"i{self._loop_level}"
        b = self.loop_body_cls(dim, i, self.loop_type, label)
        self._stack.append(b)
        self._loop_level += 1

    def add_content(self, s: str) -> None:
        self.current_loop.children.append(s)

    def pop_loop(self) -> None:
        b = self._stack.pop()

        if b.children:
            # Loop body is not empty. Attach it to the parent
            self.current_loop.children.append(b)
        self._loop_level -= 1

    def start(self) -> None:
        assert not self._stack
        b = Body()
        self._stack.append(b)

    def finish(self) -> Optional[str]:
        b = self._stack.pop()
        assert not self._stack

        if not b.children:
            return None
        return str(b)

class RDLForLoopGenerator(ForLoopGenerator, RDLListener):

    def __init__(self, label_prefix: str = ""):
        """label_prefix: if specified, produce loop labels using the node name and dimension along with this prefix"""
        super().__init__()
        self.label_prefix = label_prefix

    def get_content(self, node: 'Node') -> Optional[str]:
        self.start()
        walker = RDLWalker()
        walker.walk(node, self, skip_top=True)
        return self.finish()

    def enter_AddressableComponent(self, node: 'AddressableNode') -> None:
        if not node.is_array:
            return

        for i, dim in enumerate(node.array_dimensions):
            if self.label_prefix:
                # all but the top-level
                path = "_".join(node.get_path_segments(
                    array_suffix="",
                    empty_array_suffix="",
                )[1:])
                label = self.label_prefix + path + "_dim" + str(i)
            else:
                label = None
            self.push_loop(dim, label)

    def exit_AddressableComponent(self, node: 'AddressableNode') -> None:
        if not node.is_array:
            return

        for _ in node.array_dimensions:
            self.pop_loop()
