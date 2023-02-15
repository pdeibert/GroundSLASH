from typing import Optional

# hidden package-level flag for debug mode
__debug_mode = False

def debug(use_debug: Optional[bool]=None) -> bool:
    """Package-level method for checking and setting internal debug flag."""
    # set debug mode if specified
    if use_debug is not None:
        global __debug_mode
        __debug_mode = use_debug

    # return current debug mode
    return __debug_mode