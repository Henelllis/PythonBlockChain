import hashlib as hl
import json


def hash_string_256(string):
    return hl.sha256(string).hexdigest()


def hash_block(block):
    # Get copy of block from blockchain
    hashable_block = block.__dict__.copy()
    #Convert each transaction object into an Ordered Dictionary
    hashable_block['transactions'] = [ txn.to_ordered_dict() for txn in hashable_block['transactions']] 
    # Hash the json dumps of the hashable blocks
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())
