from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)


CORS(app)

@app.route("/", methods=['GET'])
def get_ui():
    return send_from_directory('ui', 'node.html')

@app.route("/network", methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html')


@app.route("/wallet", methods=["POST"])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():

        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            "funds": blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Saving the keys failed"
        }
        return jsonify(response), 500

@app.route("/wallet", methods=['GET'])
def load_keys():
    if wallet.load_keys():

        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            "funds": blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Loading the keys failed"
        }
        return jsonify(response), 500       

@app.route("/balance", methods=["GET"])
def get_balance():
    balance = blockchain.get_balance()
    if balance is not None:
        response = {
            "message": "Balance was retrieved",
            "funds": balance
        }
        return jsonify(response), 200  
    else:
        response = {
            "message": "Balance not found",
            "wallet_set_up": wallet.public_key is not None
        }
        return jsonify(response), 500       

@app.route('/broadcast-transaction', methods=["POST"])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        print('No data found')
        response = {
            "message": "No data found"
        }
        return jsonify(response), 400
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(key in values for key in required):
        print('Missing keys not found')
        print(str(values))
        response = {
            "message": "Some Data is missing"
        }
        return jsonify(response), 400

    success = blockchain.add_txn(values['recipient'],values['sender'],values['signature'],values['amount'], is_receiving=True)
    if success:
        response = {
            "message": "Successfully created a transaction",
            "transaction":{
                "sender": values['sender'],
                "recipient": values['recipient'],
                "amount": values['amount'],
                "signature": values['signature']
            }
        }
        return jsonify(response), 201  
    else:
        response = {
            "message": "Creating a transaction failed",
        }
        return jsonify(response), 500

@app.route("/broadcast-block", methods=["POST"])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {
            "message": "No data found"
        }
        return jsonify(response), 400
    if 'block' not in values:
        response = {
            "message": "Block is missing in body"
        }
        return jsonify(response), 400
    block = values['block']
    if block['index'] == blockchain.get_chain()[-1].index + 1:
        if  blockchain.add_block(block):
            response = {
                "message": "Block added to chain"
            }
            return jsonify(response), 201
        else:
            response = {
                "message": "Block is invalid"
            } 
            return jsonify(response), 409

    elif block['index'] > blockchain.get_chain()[-1].index:
        response = {
            "message": "Block chain seems to differ from local blockchain "
        } 
        blockchain.resolve_conflicts = True
        return jsonify(response), 200
    else:
        response = {
            "message": "Block chain seems to be shorter, block not added"
        } 
        return jsonify(response), 409



@app.route("/transaction", methods=["POST"])
def add_transaction():
    if wallet.public_key is None:
        response = {
            "message": "No wallet setup",
        }
        return jsonify(response), 400        
    values = request.get_json()
    if not values:
        response = {
            "message": "No Json body provided",
        }
        return jsonify(response), 400
    
    required_fields = [ 'recipient', 'amount']
    # excellent usage of determining subsets with arrays
    if not all(field in values for field in required_fields):
        response = {
            "message": "Required data is missing!",
        }
        return jsonify(response), 400 
    
    recipient = values['recipient']
    amount = values['amount']
    signature = wallet.sign_transaction(wallet.public_key,recipient, amount)
    #self, recipient, sender, signature, amount=1.0
    success = blockchain.add_txn(recipient, wallet.public_key, signature, amount)
    if success:
        response = {
            "message": "Successfully created a transaction",
            "transaction":{
                "sender": wallet.public_key,
                "recipient": recipient,
                "amount": amount,
                "signature": signature
            },
            "funds": blockchain.get_balance()
        }
        return jsonify(response), 201  
    else:
        response = {
            "message": "Creating a transaction failed",
        }
        return jsonify(response), 500           


@app.route("/mine", methods=['POST'])
def mine():
    if blockchain.resolve_conflicts: 
        response = {'message': 'Resolve conflicts first, block not added'}
        return jsonify(response), 409
    mined_block = blockchain.mine_block() 
    if mined_block is not None:
        mined_block_dict  = mined_block.__dict__.copy()
        mined_block_dict['transactions']  = [txn.__dict__ for txn in mined_block_dict['transactions']]

        response = {
            "message": "Adding new block to chain",
            "block": mined_block_dict,
            "funds": blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Adding a block failed",
            "wallet_set_up": wallet.public_key is not None
        }
        return jsonify(response), 500

@app.route("/transactions", methods=["GET"] )
def get_open_transactions():
    transactions = blockchain.get_open_txns()
    dict_transactions = [txn.__dict__ for txn in transactions]

    return  jsonify(dict_transactions), 200 


@app.route("/chain", methods=["GET"])
def get_chain():
    chain_snapshot = blockchain.get_chain()
    dict_chain = [ block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [txn.__dict__ for txn in dict_block['transactions']]
    return  jsonify(dict_chain), 200 

@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached'
        }
        return jsonify(response), 400
    if 'node' not in values:
        response = {
            'message': 'No node value attached'
        }
        return jsonify(response), 400
    node = values.get('node')
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added successfully',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201

@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == '' or node_url is None:
        response ={
            'message': 'No node found'
        }
        return jsonify(response), 400
    blockchain.remove_peer_node(node_url)
    response = {
        'message': f'Node {node_url} removed successfully',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200

@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = blockchain.get_peer_nodes()
    response = {
        'all_nodes':nodes
    }
    return jsonify(response), 200


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)

    blockchain = Blockchain(wallet.public_key, port)
    app.run(host="0.0.0.0", port=port)
