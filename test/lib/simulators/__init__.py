from typing import Type, TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..regblock_testcase import RegblockTestCase

class Simulator:

    def __init__(self, testcase_cls: 'Type[RegblockTestCase]' = None, testcase_cls_inst: 'RegblockTestCase' = None) -> None:
        self.testcase_cls = testcase_cls
        self.testcase_cls_inst = testcase_cls_inst

    @property
    def tb_files(self) -> List[str]:
        files = []
        files.extend(self.testcase_cls.cpuif.get_tb_files())
        files.append("regblock_pkg.sv")
        files.append("regblock.sv")
        files.append("tb.sv")

        return files

    def compile(self) -> None:
        raise NotImplementedError

    def run(self, plusargs:List[str] = None) -> None:
        raise NotImplementedError