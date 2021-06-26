import functools
from collections import OrderedDict
import json
from block import Block

from hash_util import hash_block, hash_string_256

MINING_REWARD = 10
owner = 'Henry'
participants = {'Henry'}


# GLOBAL VARS
blockchain = []
open_txns = []


def load_data():
    global blockchain
    global open_txns
    try:
        with open('blockchain.txt', mode='r') as f:
            file_contents = f.readlines()
            blockchain = json.loads(file_contents[0][:-1])
            for block in blockchain:
                updated_blockchain = []

                converted_txns = [OrderedDict(
                    [('sender', txn['sender']), ('recipient', txn['recipient']),
                     ('amount', txn['amount'])]) for txn in block['transactions']]

                updated_block = Block(
                    block['index'], block['previous_hash'], converted_txns,
                    block['proof'], block['timestamp'])

                print('updatedBlock', updated_block)
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain

            open_txns = json.loads(file_contents[1])
            updated_open_txns = []
            for txn in open_txns:
                updated_open_txn = OrderedDict(
                    [('sender', txn['sender']), ('recipient', txn["recipient"]), ('amount', txn["amount"])])
                updated_open_txns.append(updated_open_txn)
            open_txns = updated_open_txns
    except (IOError, IndexError):
        genisis_block = Block(0, '', [], 666, 0)

        blockchain = [genisis_block]
        open_txns = []


load_data()


def save_data():

    try:
        with open('blockchain.txt', mode='w') as f:
            saveable_chain = [block.__dict__ for block in blockchain]
            f.write(json.dumps(saveable_chain))
            f.write("\n")
            f.write(json.dumps(open_txns))
    except IOError:
        print("SAVVING FAILED")


def get_last_blockchain_value():
    if(len(blockchain) < 1):
        return None
    return blockchain[-1]


def verify_txn(txn):
    sender_balance = get_balance(txn['sender'])
    return sender_balance >= txn['amount']


def add_txn(recipient, sender=owner,  amount=1.0):

    txn = OrderedDict(
        [('sender', sender), ('recipient', recipient), ('amount', amount)])

    if verify_txn(txn):
        open_txns.append(txn)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False


def get_txn_value():
    txn_recipient = input("Enter the recipient of the transaction:")
    txn_amnt = float(input('Your transaction amount please:\n'))
    return (txn_recipient, txn_amnt)


def get_user_choice():
    user_input = input('Your choice:\n')
    return user_input


def print_blockchain_elements():
    for block in blockchain:
        print("outputting block")
        print(block)


def verify_chain():
    for (idx, block) in enumerate(blockchain):
        if(idx == 0):
            continue
        if(block.previous_hash != hash_block(blockchain[idx - 1])):
            return False
        if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
            print("Proof of work is invalid")
            return False
    return True


def verify_txns():
    return all([verify_txn[txn] for txn in open_txns])


def valid_proof(txns, last_hash, proof):
    guess = (str(txns) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    print(guess_hash)
    return guess_hash[0:2] == "00"


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_txns, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):
    txn_sender = [[txn['amount'] for txn in block.transactions if txn['sender'] == participant]
                  for block in blockchain]
    open_txn_sender = [txn['amount']
                       for txn in open_txns if txn['sender'] == participant]
    txn_sender.append(open_txn_sender)
    amount_sent = functools.reduce(
        lambda txn_sum, txn_amnt: txn_sum + sum(txn_amnt) if len(txn_amnt) > 0 else txn_sum + 0, txn_sender, 0)

    txn_recipient = [[txn['amount'] for txn in block.transactions if txn['recipient'] == participant]
                     for block in blockchain]

    amount_received = functools.reduce(
        lambda txn_sum, txn_amnt: txn_sum + sum(txn_amnt) if len(txn_amnt) > 0 else txn_sum + 0, txn_recipient, 0)

    return amount_received - amount_sent


def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    proof = proof_of_work()

    reward_txn = OrderedDict(
        [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])

    copied_txns = open_txns[:]
    copied_txns.append(reward_txn)
    print(f'hashed_block {hashed_block}')
    block = Block(len(blockchain), hashed_block, copied_txns, proof)

    # open_txns.clear()
    blockchain.append(block)
    save_data()

    return True


waiting_for_input = True

while waiting_for_input:
    print("Please choose")
    print("1: Add a new transaction value")
    print("2: Mine Block")
    print("3: Output block chain")
    print("4: Output participants")
    print("5: Check Transaction validity")
    print("q: quit")

    use_choice = get_user_choice()

    if(use_choice == "1"):
        txn_data = get_txn_value()
        recipient, amount = txn_data
        if(add_txn(recipient, amount=amount)):
            print('added transaction!')
        else:
            print('transaction failed')
    elif(use_choice == "2"):
        if(mine_block()):
            open_txns = []
    elif(use_choice == "3"):
        print_blockchain_elements()
    elif(use_choice == "4"):
        print(participants)
    elif(use_choice == "5"):
        verify_txns()
    elif(use_choice == "q"):
        waiting_for_input = False
    else:
        print("invalid input, please try again")
        continue
    if(not verify_chain()):
        print("invalid blockchain")
        print_blockchain_elements()
        waiting_for_input = False
    print('Balance amount')
    print(f'Balance of {get_balance("Henry"):6.2f}')


print_blockchain_elements()
print("Done!")
# This is the price
