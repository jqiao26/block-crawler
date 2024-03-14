class Transaction:
    def __init__(self, hash, block_hash, block_number, t_from, t_to, value):
        self.hash = hash
        self.block_hash = block_hash
        self.block_number = block_number
        self.t_from = t_from
        self.t_to = t_to
        self.value = value
