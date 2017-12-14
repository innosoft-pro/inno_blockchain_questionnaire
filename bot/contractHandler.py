from time import sleep
from web3 import Web3, RPCProvider
from os import path
import requests
import json
import base64


class ContractHandler:
    def __init__(self):
        # Load contract configuration
        self.web3 = Web3(RPCProvider(host='localhost', port='8545'))
        dir_path = path.dirname(path.realpath(__file__))
        with open(str(path.join(dir_path, 'configuration.txt')), 'r') as configuration:
            for line in configuration:
                if line.startswith('contractPollingCenter='):
                    self.contractPC_address = line.split('=')[1].rstrip('\n')
                if line.startswith('contractCryptoRF='):
                    self.contractPoll_address = line.split('=')[1].rstrip('\n')
                if line.startswith('main_account='):
                    self.main_account = line.split('=')[1].rstrip('\n')
                if line.startswith('main_password='):
                    self.main_password = line.split('=')[1].rstrip('\n')
        with open(str(path.join(dir_path, 'PollingCenter.json')), 'r') as abi_definition:
            self.abiPC = json.load(abi_definition)
        with open(str(path.join(dir_path, 'Poll.json')), 'r') as abi_definition:
            self.abiPoll = json.load(abi_definition)
        self.web3.personal.unlockAccount(self.main_account, self.main_password)
        self.contractPC = self.web3.eth.contract(self.abiPC, self.contractPC_address)
        self.contractPoll = self.web3.eth.contract(self.abiPoll, self.contractPoll_address)
        print(self.contractPC_address)
        print(self.contractPoll_address)
        self.polls = dict()
        self.polls['CryptoRF'] = self.contractPoll
        newPollFilter = self.contractPC.on('PollCreated',
                                           {'address': self.contractPC_address },
                                           self.pollCreated)

    def pollCreated(self, eventLog):
        print(eventLog['args'][''])
        self.polls[eventLog['args']['']] = self.web3.eth.contract(self.abiPoll, eventLog['args'][''])

    def createPoll(self, pollName):
        balance = self.web3.eth.getBalance(self.main_account)
        print(balance)
        print(self.web3.eth.coinbase)
        print(self.main_account)
        self.web3.personal.unlockAccount(self.main_account, self.main_password)
        newPollTx = self.contractPC.transact({'from': self.main_account}).createPoll(pollName)
        print(pollName)


    def recordAnswers(self, pollName, id, answer):
        self.web3.personal.unlockAccount(self.main_account, self.main_password)
        ansb64 = base64.b64encode(bytearray(answer, encoding='utf-8'))
        txAddress = self.polls[pollName].transact({'from': self.main_account}).recordAnswers(id, ansb64)
        return "https://kovan.etherscan.io/tx/" + str(txAddress)


    def getAnswersById(self, pollName, id):
        self.web3.personal.unlockAccount(self.main_account, self.main_password)
        ansb64 = self.polls[pollName].call({'from': self.main_account}).getAnswersById(id)

        return base64.b64decode(ansb64).decode('utf-8')


if __name__ == "__main__":
    contractHandler = ContractHandler()
    #contractHandler.createPoll("CryptoRF")
    print(contractHandler.recordAnswers("CryptoRF", "787897", "2;34324;ааап"))
    sleep(10)
    print(contractHandler.getAnswersById("CryptoRF", "787897"))
