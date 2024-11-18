# All VHDL 2008 keywords
VHDL_KEYWORDS = {
    'abs', 'access', 'after', 'alias',
    'all', 'and', 'architecture', 'array',
    'assert', 'attribute', 'begin', 'block',
    'body', 'buffer', 'bus', 'case',
    'component', 'configuration', 'constant', 'disconnect',
    'downto', 'else', 'elsif', 'end',
    'entity', 'exit', 'file', 'for',
    'function', 'generate', 'generic', 'group',
    'guarded', 'if', 'impure', 'in',
    'inertial', 'inout', 'is', 'label',
    'library', 'linkage', 'literal', 'loop',
    'map', 'mod', 'nand', 'new',
    'next', 'nor', 'not', 'null',
    'of', 'on', 'open', 'or',
    'others', 'out', 'package', 'port',
    'postponed', 'procedure', 'process', 'pure',
    'range', 'record', 'register', 'reject',
    'rem', 'report', 'return', 'rol',
    'ror', 'select', 'severity', 'signal',
    'shared', 'sla', 'sll', 'sra',
    'srl', 'subtype', 'then', 'to',
    'transport', 'type', 'unaffected', 'units',
    'until', 'use', 'variable', 'wait',
    'when', 'while', 'with', 'xnor', 'xor'
}


def kw_filter(s: str) -> str:
    """
    Make all user identifiers 'safe' and ensure they do not collide with
    VHDL keywords.

    If an VHDL keyword is encountered, or identifier contains illegal characters,
    make it an "Extended identifier" by wrapping it in backslashes.
    """
    s = s.replace("\\", "")
    if s.lower() in VHDL_KEYWORDS or "." in s or "__" in s:
        s = "\\" + s + "\\"
    return s
