import functools
import json
from block import Block
import requests
from transaction import Transaction 
from utility.hash_util import hash_block
from utility.verification import Verification
from wallet import Wallet


MINING_REWARD = 10


class Blockchain:
    def __init__(self, public_key, node_id):
        genisis_block = Block(0, '', [], 666, 0)

        self.__chain = [genisis_block]
        self.__open_txns = []
        self.__peer_nodes = set()
        self.public_key = public_key
        self.node_id = node_id
        self.resolve_conflicts = False
        self.load_data()



    def get_chain(self):
        return self.__chain[:]

        
    def get_open_txns(self):
        return self.__open_txns[:]


    def load_data(self):
        try:
            with open(f'blockchain-{self.node_id}.txt', mode='r') as f:
                file_contents = f.readlines()
                blockchain = json.loads(file_contents[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_txns = [Transaction(txn['sender'],txn['recipient'],txn['amount'],txn['signature'] ) for txn in block['transactions']]
                    # converted_txns = [OrderedDict(
                    #     [('sender', txn['sender']), ('recipient', txn['recipient']),
                    #      ('amount', txn['amount'])]) for txn in block['transactions']]

                    updated_block = Block(
                        block['index'], block['previous_hash'], converted_txns,
                        block['proof'], block['timestamp'])

                    updated_blockchain.append(updated_block)
                self.__chain = updated_blockchain

                open_txns = json.loads(file_contents[1][:-1])
                updated_open_txns = []
                for txn in open_txns:
                    print("Txn Type from saved file")
                    print(type(txn))
                    updated_open_txn = Transaction(txn['sender'],txn["recipient"],txn["amount"],txn['signature'])
                    # updated_open_txn = OrderedDict(
                    #     [('sender', txn['sender']), ('recipient', txn["recipient"]), ('amount', txn["amount"])])
                    updated_open_txns.append(updated_open_txn)
                self.__open_txns = updated_open_txns
                peer_nodes = json.loads(file_contents[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError):
            print("handled exception case...")



    def save_data(self):

        try:
            with open(f'blockchain-{self.node_id}.txt', mode='w') as f:
                saveable_chain = [block.__dict__ for block in  
                    [ Block(block_el.index, block_el.previous_hash, [txn.__dict__ for txn in block_el.transactions],
                    block_el.proof, block_el.timestamp) for block_el in self.__chain] ]
                f.write(json.dumps(saveable_chain))
                f.write("\n")
                saveable_txn = [ txn.__dict__ for txn in self.__open_txns ]
                f.write(json.dumps(saveable_txn))
                f.write("\n")
                f.write(json.dumps(list(self.__peer_nodes)))

        except IOError:
            print("SAVING FAILED")


    def proof_of_work(self):
        #Get last block
        last_block = self.__chain[-1]
        #Hash last block
        last_hash = hash_block(last_block)
        #Nonce is set to zero
        proof = 0
        #Valid Proof
        while not Verification.valid_proof(self.__open_txns, last_hash, proof):
            proof += 1
        return proof


    def get_balance(self, sender=None):

        if sender is None:
            if self.public_key is None:
                return None
            participant = self.public_key
        else:
            participant = sender

        txn_sender = [[txn.amount for txn in block.transactions if txn.sender == participant]
                    for block in self.__chain]
        open_txn_sender = [txn.amount
                        for txn in self.__open_txns if txn.sender == participant]
        txn_sender.append(open_txn_sender)
        amount_sent = functools.reduce(
            lambda txn_sum, txn_amnt: txn_sum + sum(txn_amnt) if len(txn_amnt) > 0 else txn_sum + 0, txn_sender, 0)

        txn_recipient = [[txn.amount for txn in block.transactions if txn.recipient == participant]
                        for block in self.__chain]

        amount_received = functools.reduce(
            lambda txn_sum, txn_amnt: txn_sum + sum(txn_amnt) if len(txn_amnt) > 0 else txn_sum + 0, txn_recipient, 0)

        return amount_received - amount_sent

            
    def get_last_blockchain_value(self):
        if(len(self.__chain) < 1):
            return None
        return self.__chain[-1]


    def add_txn(self, recipient, sender, signature, amount=1.0, is_receiving=False):


        txn = Transaction(sender, recipient, amount, signature)

        if Verification.verify_txn(txn, self.get_balance):
            self.__open_txns.append(txn)
            self.save_data()
            if not is_receiving:
                for peer in self.__peer_nodes:
                    url = f'http://{peer}/broadcast-transaction'

                    try:
                        response = requests.post(url, json={'sender': sender, 'recipient': recipient, 
                                                'amount':amount, 'signature':signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print('transaction declined, please resolve')
                    except requests.exceptions.ConnectionError:
                        continue
    
            return True
        return False

    def add_block(self, block):
        transactions = [Transaction(txn['sender'], txn['recipient'],  txn['amount'], txn['signature']) for txn in block['transactions']]
        proof_is_valid = Verification.valid_proof(transactions[:-1], block['previous_hash'], block['proof'])
        hash_match = hash_block(self.__chain[-1]) == block['previous_hash']
        if  not proof_is_valid or not hash_match:
            print('proof_is_valid:',proof_is_valid)
            print('hash_match:',hash_match)

            return False
        converted_block = Block(block['index'], block['previous_hash'], transactions, block['proof'], block['timestamp'] )

        stored_transactions = self.__open_txns[:]
        for incoming_txn in block['transactions']:
            for open_txn in stored_transactions:
                if open_txn.sender == incoming_txn['sender'] and open_txn.recipient == incoming_txn['recipient'] \
                    and open_txn.amount == incoming_txn['amount'] and open_txn.signature == incoming_txn['signature']:
                    try:
                        self.__open_txns.remove(open_txn)
                    except ValueError:
                        print("item was already removed")

        self.save_data()
        self.__chain.append(converted_block)
        return True

    def resolve(self):
        winner_chain = self.__chain
        replace = False
        for peer_node in self.__peer_nodes:
            url = f"http://{peer_node}/chain"
            try:
                response = requests.get(url)
                peer_node_chain = response.json()
                peer_node_chain = [Block(block['index'], block["previous_hash"], 
                    [ Transaction(txn['sender'], txn['recipient'], txn['amount'], txn['signature']) for txn in block['transactions']], 
                    block['proof'], block["timestamp"]) for block in peer_node_chain]
                node_chain_length = len(peer_node_chain)
                local_chain_length = len(winner_chain)
                if node_chain_length > local_chain_length and Verification.verify_chain(peer_node_chain):
                    winner_chain = peer_node_chain
                    replace = True
            except requests.ConnectionError:
                continue
        self.resolve_conflicts = False
        self.__chain = winner_chain

        if replace:
            self.__open_txns = []
        self.save_data()
        return replace



    def mine_block(self):

        if self.public_key is None:
            return None
        # Get last block  
        last_block = self.__chain[-1]
        #Get sha of block
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()

        reward_txn = Transaction('MINING', self.public_key , MINING_REWARD, '' )

        copied_txns = self.__open_txns[:]
        for txn in copied_txns:
            if not Wallet.verify_transaction(txn):
                return None
        copied_txns.append(reward_txn)
        # print(f'hashed_block {hashed_block}')
        block = Block(len(self.__chain), hashed_block, copied_txns, proof)

        # open_txns.clear()
        self.__chain.append(block)
        self.save_data()
        self.__open_txns = []
        self.save_data()

        for peer_node in self.__peer_nodes:
            url = f'http://{peer_node}/broadcast-block'
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [txn.__dict__ for txn in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block':converted_block })
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined, please resolve')
                elif response.status_code == 409:
                    self.resolve_conflicts = True

            except requests.exceptions.ConnectionError:
                continue
        return block

    def add_peer_node(self, node):
        """Adds a new node to the peer node set
            Arguments:
                :node: The node URL which should be added
        """
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        """Removes node to the peer node set
            Arguments:
                :node: The node URL which should be removed
        """
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_peer_nodes(self):
        """Return a list of all connected peer nodes"""
        return list(self.__peer_nodes)
# This is the price
