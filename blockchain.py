import functools
from collections import OrderedDict
import json
from block import Block
from transaction import Transaction 
from hash_util import hash_block
from verification import Verification

MINING_REWARD = 10
participants = {'Henry'}


class Blockchain:
    def __init__(self):
        genisis_block = Block(0, '', [], 666, 0)

        self.chain = [genisis_block]
        self.open_txns = [] 
        self.load_data()
        # Potentially there but not there , if that makes sense
        # self.owner = "Henry"

    def load_data(self):
        try:
            with open('blockchain.txt', mode='r') as f:
                file_contents = f.readlines()
                blockchain = json.loads(file_contents[0][:-1])
                for block in blockchain:
                    updated_blockchain = []
                    converted_txns = [Transaction(txn['sender'],txn['recipient'],txn['amount'] ) for txn in block['transactions']]
                    # converted_txns = [OrderedDict(
                    #     [('sender', txn['sender']), ('recipient', txn['recipient']),
                    #      ('amount', txn['amount'])]) for txn in block['transactions']]

                    updated_block = Block(
                        block['index'], block['previous_hash'], converted_txns,
                        block['proof'], block['timestamp'])

                    print('updatedBlock', updated_block)
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain

                open_txns = json.loads(file_contents[1])
                updated_open_txns = []
                for txn in open_txns:
                    print("Txn Type from saved file")
                    print(type(txn))
                    updated_open_txn = Transaction(txn['sender'],txn["recipient"],txn["amount"])
                    # updated_open_txn = OrderedDict(
                    #     [('sender', txn['sender']), ('recipient', txn["recipient"]), ('amount', txn["amount"])])
                    updated_open_txns.append(updated_open_txn)
                self.open_txns = updated_open_txns
        except (IOError, IndexError):
            print("handled exception case...")



    def save_data(self):

        try:
            with open('blockchain.txt', mode='w') as f:
                saveable_chain = [block.__dict__ for block in  
                    [ Block(block_el.index, block_el.previous_hash, [txn.__dict__ for txn in block_el.transactions],
                    block_el.proof, block_el.timestamp) for block_el in self.chain] ]
                f.write(json.dumps(saveable_chain))
                f.write("\n")
                saveable_txn = [ txn.__dict__ for txn in self.open_txns ]
                f.write(json.dumps(saveable_txn))
        except IOError:
            print("SAVING FAILED")


    def proof_of_work(self):
        last_block = self.chain[-1]
        last_hash = hash_block(last_block)
        proof = 0

        verifier = Verification()
        while not verifier.valid_proof(self.open_txns, last_hash, proof):
            proof += 1
        return proof


    def get_balance(self, participant):
        txn_sender = [[txn.amount for txn in block.transactions if txn.sender == participant]
                    for block in self.chain]
        open_txn_sender = [txn.amount
                        for txn in self.open_txns if txn.sender == participant]
        txn_sender.append(open_txn_sender)
        amount_sent = functools.reduce(
            lambda txn_sum, txn_amnt: txn_sum + sum(txn_amnt) if len(txn_amnt) > 0 else txn_sum + 0, txn_sender, 0)

        txn_recipient = [[txn.amount for txn in block.transactions if txn.recipient == participant]
                        for block in self]

        amount_received = functools.reduce(
            lambda txn_sum, txn_amnt: txn_sum + sum(txn_amnt) if len(txn_amnt) > 0 else txn_sum + 0, txn_recipient, 0)

        return amount_received - amount_sent

            
    def get_last_blockchain_value(self):
        if(len(self.chain) < 1):
            return None
        return self.chain[-1]


    def add_txn(self, recipient, sender,  amount=1.0):

        txn = Transaction(sender, recipient,amount)
        verifier = Verification()

        if verifier.verify_txn(txn, self.get_balance):
            self.open_txns.append(txn)
            self.save_data()
            return True
        return False


    def mine_block(self, node):
        last_block = self.chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()

        reward_txn = Transaction('MINING', node ,MINING_REWARD )

        copied_txns = self.open_txns[:]
        copied_txns.append(reward_txn)
        print(f'hashed_block {hashed_block}')
        block = Block(len(self.chain), hashed_block, copied_txns, proof)

        # open_txns.clear()
        self.chain.append(block)
        self.save_data()

        return True



# This is the price
