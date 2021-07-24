from blockchain import Blockchain
from uuid import uuid4
from utility.verification import Verification
from wallet import Wallet
class Node:

    def __init__(self):
        # self.wallet.public_key = str(uuid4())
        self.wallet = Wallet()
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_txn_value(self):
        txn_recipient = input("Enter the recipient of the transaction:")
        txn_amnt = float(input('Your transaction amount please:\n'))
        return (txn_recipient, txn_amnt)

    def print_blockchain_elements(self):
        for block in self.blockchain.get_chain():
            print("outputting block")
            print(block)


    def get_user_choice(self):
        user_input = input('Your choice:\n')
        return user_input

    def listen_for_input(self):
        waiting_for_input = True

        while waiting_for_input:
            print("Please choose")
            print("1: Add a new transaction value")
            print("2: Mine Block")
            print("3: Output block chain")
            print("4: Check Transaction validity")
            print("5: Create Wallet")
            print("6: Load Wallet")
            print("7: save Keys")
            print("8: get Balance")
            print("q: quit")

            use_choice = self.get_user_choice()

            if(use_choice == "1"):
                txn_data = self.get_txn_value()
                recipient, amount = txn_data
                signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)
                if(self.blockchain.add_txn(recipient, self.wallet.public_key, signature, amount=amount)):
                    print('added transaction!')
                else:
                    print('transaction failed')
            elif(use_choice == "2"):
                if not self.blockchain.mine_block(self.wallet.public_key):
                    print('Mining Failed, no wallet found')
            elif(use_choice == "3"):
                self.print_blockchain_elements()
            elif(use_choice == "4"):
                Verification.verify_txns(self.blockchain.get_open_txns(), self.blockchain.get_balance)
            elif(use_choice == "5"):
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif(use_choice == "6"):
                self.wallet.load_keys()
                print("I hace extracted this public key :: ", self.wallet.public_key)
                self.blockchain = Blockchain(self.wallet.public_key)
            elif(use_choice == "7"):
                self.wallet.save_keys()
            elif(use_choice == "8"):
                self.blockchain.get_balance()
            elif(use_choice == "q"):
                waiting_for_input = False
            else:
                print("invalid input, please try again")
                continue
            if(not Verification.verify_chain(self.blockchain.get_chain())):
                print("invalid blockchain")
                self.print_blockchain_elements(self.blockchain)
                waiting_for_input = False
            print('Balance amount')
            print(f'Balance of {self.blockchain.get_balance():6.2f}')


        self.print_blockchain_elements()
        self.blockchain.save_data()
        print("Done!")

if __name__ == '__main__':
    node = Node()
    node.listen_for_input()