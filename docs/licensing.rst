Licensing
=========

Distribution of the PeakRDL-regblock code generator tool shall adhere to the
terms outlined by the GNU GPL v3 license. For a copy of the license, see:
https://github.com/SystemRDL/PeakRDL-regblock/blob/main/LICENSE


Why GPL?
--------
GPL was chosen because my intent is to promote a thriving ecosystem of free and
open source register automation tools. GPL discourages this tool to be bundled
into some commercially sold closed-source software, as that would be contrary to
this project's philosophy.


What is covered by the GPL v3 license?
--------------------------------------
The GPL license is intended for the code generator itself. This includes all
Python sources, Jinja demplate files, as well as testcase infrastructure not
explicitly mentioned in the exemptions below.


What is exempt from the GPL v3 license?
---------------------------------------
Don't worry. Not everything that the PeakRDL-regblock project touches is
considered GPL v3 code.

The following are exempt and are free to use with no restrictions:

*   Any code that is generated using PeakRDL-regblock is 100% yours. Since it
    was derived from your regblock definition, it remains yours. You can
    distribute it freely, use it in a proprietary ASIC, sell it as part of an
    IP, whatever.
*   Any code snippets in this documentation can be freely copy/pasted. These are
    examples that are intended for this purpose.
*   The UDP definition SystemRDL file distributed in this documentation, and
    located in the repository.
*   Any example snippets within this documentation.
