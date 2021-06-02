
"""
- Signal References
    Collect any references to signals that lie outside of the hierarchy
    These will be added as top-level signals
- top-level interrupts


Validate:
    - Error if a property references a non-signal component, or property reference from
        outside the export hierarchy
    - No Mem components allowed
    - Uniform regwidth, accesswidth, etc.
"""
