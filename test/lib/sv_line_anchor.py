from jinja2_simple_tags import StandaloneTag

class SVLineAnchor(StandaloneTag):
    """
    Define a custom Jinja tag that emits a SystemVerilog `line directive so that
    assertion messages can get properly back-annotated
    """
    tags = {"sv_line_anchor"}
    def render(self):
        return f'`line {self.lineno + 1} "{self.template}" 0'
