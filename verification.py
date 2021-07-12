from hash_util import hash_block, hash_string_256

class Verification:
    @staticmethod
    def valid_proof( txns, last_hash, proof):
        guess = (str([txn.to_ordered_dict() for txn in txns]) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        print(guess_hash)
        return guess_hash[0:2] == "00"
    @classmethod
    def verify_chain(cls, blockchain):
        for (idx, block) in enumerate(blockchain):
            if(idx == 0):
                continue
            if(block.previous_hash != hash_block(blockchain[idx - 1])):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print("Proof of work is invalid")
                return False
        return True
    @staticmethod
    def verify_txn( txn, get_balance):
        sender_balance = get_balance()
        return sender_balance >= txn.amount
    @classmethod
    def verify_txns(cls, open_txns, get_balance):
        return all([cls.verify_txn(txn, get_balance) for txn in open_txns])