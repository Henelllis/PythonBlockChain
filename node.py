class Node:

    def __init__(self):
        self.blockchain = []

    def get_txn_value(self):
        txn_recipient = input("Enter the recipient of the transaction:")
        txn_amnt = float(input('Your transaction amount please:\n'))
        return (txn_recipient, txn_amnt)

    def print_blockchain_elements(self):
        for block in self.blockchain:
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
            print("4: Output participants")
            print("5: Check Transaction validity")
            print("q: quit")

            use_choice = self.get_user_choice()

            if(use_choice == "1"):
                txn_data = self.get_txn_value()
                recipient, amount = txn_data
                if(add_txn(recipient, amount=amount)):
                    print('added transaction!')
                else:
                    print('transaction failed')
            elif(use_choice == "2"):
                if(mine_block()):
                    open_txns = []
            elif(use_choice == "3"):
                self.print_blockchain_elements(self.blockchain)
            elif(use_choice == "4"):
                print(participants)
            elif(use_choice == "5"):
                verifier = Verification()
                verifier.verify_txns(open_txns, get_balance)
            elif(use_choice == "q"):
                waiting_for_input = False
            else:
                print("invalid input, please try again")
                continue
            verifier = Verification()
            if(not verifier.verify_chain(blockchain)):
                print("invalid blockchain")
                self.print_blockchain_elements(self.blockchain)
                waiting_for_input = False
            print('Balance amount')
            print(f'Balance of {get_balance("Henry"):6.2f}')


        print_blockchain_elements()
        print("Done!")