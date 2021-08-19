from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.wrappers import response
from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)

wallet = Wallet()

blockchain = Blockchain(wallet.public_key)
CORS(app)


@app.route("/wallet", methods=["POST"])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key
        }
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        return jsonify(response), 201
    else:
        response = {
            "message": "Saving the keys failed"
        }
        return jsonify(response), 500

@app.route("/wallet", methods=['GET'])
def load_keys():
    if wallet.load_keys():
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key
        }
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        return jsonify(response), 201
    else:
        response = {
            "message": "Loading the keys failed"
        }
        return jsonify(response), 500       

@app.route("/", methods=['GET'])
def get_ui():
    return 'This works'


@app.route("/mine", methods=['POST'])
def mine():
    mined_block = blockchain.mine_block() 
    if mined_block is not None:
        mined_block_dict  = mined_block.__dict__.copy()
        mined_block_dict['transactions']  = [txn.__dict__ for txn in mined_block_dict['transactions']]

        response = {
            "message": "Adding a block failed",
            "block": mined_block_dict
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Adding a block failed",
            "wallet_set_up": wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route("/chain", methods=["GET"])
def get_chain():
    chain_snapshot = blockchain.get_chain()
    dict_chain = [ block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [txn.__dict__ for txn in dict_block['transactions']]
    return  jsonify(dict_chain), 200 


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
