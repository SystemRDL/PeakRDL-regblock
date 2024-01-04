def pytest_addoption(parser):
    parser.addoption(
        "--sim-tool",
        choices=["questa", "xsim", "stub", "skip", "auto"],
        default="auto",
        help="""
        Select the simulator to use.

        stub: run the testcase using a no-op simulator stub
        skip: skip all the simulation tests
        auto: choose the best simulator based on what is installed
        """
    )

    parser.addoption(
        "--gui",
        default=False,
        action="store_true",
        help=""",
        Launch sim tool in GUI mode

        Only use this option when running a single test
        """
    )


    parser.addoption(
        "--rerun",
        default=False,
        action="store_true",
        help=""",
        Re-run simulation in-place without re-exporting regblock

        Useful if hand-editing a testcase interactively.
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
