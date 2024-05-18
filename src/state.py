from array import array


class State:
    def __init__(self):
        # Immutable
        self.pc = 0
        self.orig = 0
        self.verbose = True
        self.swap = True

        # Mutable
        self.memory = array("H", [0] * (1 << 16))
        self.labels_def_address = dict()
        self.labels_usage_address = dict()
        self.regs = dict(("R%1i" % r, r) for r in range(8))
