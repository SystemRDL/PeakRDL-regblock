def pytest_addoption(parser):
    parser.addoption(
        "--sim-tool",
        choices=["questa", "xilinx", "stub", "skip", "auto"],
        default="auto",
        help="""
        Select the simulator to use.

        stub: run the testcase using a no-op simulator stub
        skip: skip all the simulation tests
        auto: choose the best simulator based on what is installed
        """
    )

    parser.addoption(
        "--synth-tool",
        choices=["vivado", "skip", "auto"],
        default="auto",
        help="""
        Select the synthesis tool to use.

        skip: skip all the simulation tests
        auto: choose the best tool based on what is installed
        """
    )
