from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from systemrdl import SignalNode

class SignalBase:

    @property
    def is_async(self) -> bool:
        raise NotImplementedError()

    @property
    def is_activehigh(self) -> bool:
        raise NotImplementedError()

    @property
    def width(self) -> int:
        raise NotImplementedError()

    @property
    def identifier(self) -> str:
        raise NotImplementedError()

    @property
    def activehigh_identifier(self) -> str:
        """
        Normalizes the identifier reference to be active-high logic
        """
        if not self.is_activehigh:
            return "~%s" % self.identifier
        return self.identifier

    @property
    def port_declaration(self) -> str:
        """
        Returns the port delcaration text for this signal.
        In the context of this exporter, all signal objects happen to be inputs.
        """
        if self.width > 1:
            return "input wire [%d:0] %s" % (self.width - 1, self.identifier)
        return "input wire %s" % self.identifier


class RDLSignal(SignalBase):
    """
    Wrapper around a SystemRDL signal object
    """
    def __init__(self, rdl_signal:'SignalNode'):
        self.rdl_signal = rdl_signal

    @property
    def is_async(self) -> bool:
        return self.rdl_signal.get_property('async')

    @property
    def is_activehigh(self) -> bool:
        return self.rdl_signal.get_property('activehigh')

    @property
    def width(self) -> int:
        return self.rdl_signal.width

    @property
    def identifier(self) -> str:
        # TODO: uniquify this somehow
        # TODO: Deal with different hierarchies
        return "TODO_%s" % self.rdl_signal.inst_name


class InferredSignal(SignalBase):
    def __init__(self, identifier:str, width:int=1, is_async:bool=False, is_activehigh=True):
        self._identifier = identifier
        self._width = width
        self._is_async = is_async
        self._is_activehigh = is_activehigh

    @property
    def is_async(self) -> bool:
        return self._is_async

    @property
    def is_activehigh(self) -> bool:
        return self._is_activehigh

    @property
    def width(self) -> int:
        return self._width

    @property
    def identifier(self) -> str:
        return self._identifier
