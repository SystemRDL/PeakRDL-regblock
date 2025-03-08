import io
import contextlib

from systemrdl.messages import RDLCompileError

from ..lib.base_testcase import BaseTestCase

class TestValidationErrors(BaseTestCase):
    def setUp(self) -> None:
        # Stub usual pre-test setup
        pass

    def tearDown(self):
        # Delete any cruft that may get generated
        self.delete_run_dir()

    def assert_validate_error(self, rdl_file: str, err_regex: str) -> None:
        self.rdl_file = rdl_file
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            with self.assertRaises(RDLCompileError):
                self.export_regblock()
        stderr = f.getvalue()
        self.assertRegex(stderr, err_regex)


    def test_unaligned_reg(self) -> None:
        self.assert_validate_error(
            "unaligned_reg.rdl",
            "Unaligned registers are not supported. Address offset of instance 'x' must be a multiple of 4",
        )

    def test_unaligned_stride(self) -> None:
        self.assert_validate_error(
            "unaligned_stride.rdl",
            "Unaligned registers are not supported. Address stride of instance array 'x' must be a multiple of 4",
        )

    def test_bad_external_ref(self) -> None:
        self.assert_validate_error(
            "external_ref.rdl",
            "Property is assigned a reference that points to a component not internal to the regblock being exported",
        )

    def test_sharedextbus_not_supported(self) -> None:
        self.assert_validate_error(
            "sharedextbus.rdl",
            "This exporter does not support enabling the 'sharedextbus' property yet",
        )

    def test_inconsistent_accesswidth(self) -> None:
        self.assert_validate_error(
            "inconsistent_accesswidth.rdl",
            r"Multi-word registers that have an accesswidth \(16\) that are inconsistent with this regblock's CPU bus width \(32\) are not supported",
        )

    def test_unbuffered_wide_w_fields(self) -> None:
        self.assert_validate_error(
            "unbuffered_wide_fields.rdl",
            "Software-writable field 'xf' shall not span"
            " multiple software-accessible subwords. Consider enabling"
            " write double-buffering",
        )

    def test_unbuffered_wide_r_fields(self) -> None:
        self.assert_validate_error(
            "unbuffered_wide_fields.rdl",
            "The field 'yf' spans multiple software-accessible"
            " subwords and is modified on-read, making it impossible to"
            " access its value correctly. Consider enabling read"
            " double-buffering.",
        )

    def test_multiple_unconditional_assigns(self) -> None:
        self.assert_validate_error(
            "multiple_unconditional_assigns.rdl",
            "Field has multiple conflicting properties that unconditionally set its state",
        )

    def test_unsynth_reset1(self) -> None:
        self.assert_validate_error(
            "unsynth_reset1.rdl",
            "A field that uses an asynchronous reset cannot use a dynamic reset value. This is not synthesizable.",
        )

    def test_unsynth_reset2(self) -> None:
        self.default_reset_async = True
        self.assert_validate_error(
            "unsynth_reset2.rdl",
            "A field that uses an asynchronous reset cannot use a dynamic reset value. This is not synthesizable.",
        )
