"""Sanity tests"""

# global handler
from pjdata.util import gl_config, ls_gl_config
print(ls_gl_config())
print(ls_gl_config(True))
gl_config(pretty_printing=False, does_nothing=True)
print(ls_gl_config(True))
