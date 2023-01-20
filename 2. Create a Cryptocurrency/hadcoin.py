# Module 2 - Create a Cryptocurrency

# To be installed
# Flask==0.12.2: pip install Flask==0.12.2
# Postman HTTP Client: https://www.getpostman.com/
# requests==2.18.4: pip install requests

# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Part 1 - Building a Blockchain

class Blockchain:

  def __init__(self) -> None:
    self.chain = []
    self.transactions = []
    self.create_block(proof = 1, previous_hash = '0')
    self.nodes = set()

  def create_block(self, proof, previous_hash):
    block = { 'index': len(self.chain) + 1,
              'timestamp': str(datetime.datetime.now()),
              'proof': proof,
              'previous_hash': previous_hash,
              'transactions': self.transactions }
    self.transactions = []
    self.chain.append(block)
    return block

  def get_previous_block(self):
    return self.chain[-1]

  def proof_of_work(self, previous_proof):
    new_proof = 1
    check_proof = False
    while check_proof is False:
      hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
      if hash_operation[:4] == '0000':
        check_proof = True
      else:
        new_proof += 1
    return new_proof

  def hash(self, block):
    # hashlib 라이브러리의 sha256 메서드가 암호화할 수 있도록 문자열로 변환
    encoded_block = json.dumps(block, sort_keys = True).encode()
    return hashlib.sha256(encoded_block).hexdigest()
  
  def is_chain_valid(self, chain):
    previous_block = chain[0]
    block_index = 1
    while block_index < len(chain):
      block = chain[block_index]
      if previous_block['previous_hash'] != self.hash(block):
        return False
      previous_proof = previous_block['proof']
      proof = block['proof']
      hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
      if hash_operation[:4] != '0000':
        return False
      previous_block = block
      block_index += 1
    return True

  def add_transaction(self, sender, receiver, amount):
    self.transactions.append({ 'sender': sender,
                               'receiver': receiver,
                               'amount': amount })
    previous_block = self.get_previous_block()
    return previous_block['index'] + 1

  # address: 노드 주소
  def add_node(self, address):
    parsed_url = urlparse(address)
    self.nodes.add(parsed_url.netloc)

  # 가장 긴 체인으로 대체하는 함수
  def replace_chain(self):
    network = self.nodes
    longest_chain = None
    max_length = len(self.chain)
    for node in network:
      response = requests.get(f'http://{node}/get_chain')
      if response.status_code == 200:
        length = response.json()['length']
        chain = response.json()['chain']
        if length > max_length and self.is_chain_valid(chain):
          max_length = length
          longest_chain = chain
    if longest_chain:
      self.chain = longest_chain
      return True
    return False

# Part 2 - Mining our Blockchains

# Creating a Web App

app = Flask(__name__)

# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block
'''
1. 이전 블럭 가져오기
2. 이전 블럭의 작업 증명 가져오기 (Nonce 계산은 현 작업 증명 ** 2 - 이전 작업 증명 ** 2 하여 계산하므로 이전 블럭의 작업 증명이 필요함)
3. 이전 블럭의 작업 증명을 통해 현 블럭 작업 증명하기(골든 논스 찾기)
4. 이전 블럭을 해시화하기
5. 이전 블럭 해시와 현재의 작업 증명 + a로 블럭 만들기
'''
@app.route('/mine_block', methods = ['GET'])
def mine_block():
  # 이전 블럭이 있어야 작업 증명을 위한 연산이 가능
  previous_block = blockchain.get_previous_block()

  # 이전 블럭의 작업 증명
  previous_proof = previous_block['proof']

  # 작업 증명 획득하기
  proof = blockchain.proof_of_work(previous_proof)
  previous_hash = blockchain.hash(previous_block)
  block = blockchain.create_block(proof, previous_hash)
  response = { 'message': 'Congratulation, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'] }
  return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
  response = { 'chain': blockchain.chain,
               'length': len(blockchain.chain) }
  return jsonify(response), 200

# Checking if Block chain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
  is_valid = blockchain.is_chain_valid(blockchain.chain)
  if is_valid:
    response = { 'message': 'All good. The Blockchain is valid.' }
  else:
    response = { 'message': 'Houston, we have a problem. The Blockchain is not valid.' }
  return jsonify(response), 200

# Running the app
app.run(host = '127.0.0.1', port = 5000)