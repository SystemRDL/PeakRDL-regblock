from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..sim_testcase import SimTestCase

class Simulator:
    name = ""

    @classmethod
    def is_installed(cls) -> bool:
        raise NotImplementedError

    def __init__(self, testcase: 'SimTestCase' = None) -> None:
        self.testcase = testcase

    @property
    def tb_files(self) -> List[str]:
        files = []
        files.extend(self.testcase.cpuif.get_sim_files())
        files.extend(self.testcase.get_extra_tb_files())
        files.append("regblock_pkg.sv")
        files.append("regblock.sv")
        files.append("tb.sv")

        return files

    def compile(self) -> None:
        raise NotImplementedError

    def run(self, plusargs:List[str] = None) -> None:
        raise NotImplementedError
