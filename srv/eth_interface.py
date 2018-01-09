import json

from web3 import Web3, HTTPProvider, TestRPCProvider
from solc import compile_source
from web3.contract import ConciseContract


class Rinkeby:
    def __init__(self):
        # self.web3 = Web3(HTTPProvider('http://172.19.0.2:8545'))
        self.contractPC = self.web3.eth.contract(self.abiPC, self.contractPC_address)

    def create_wallet(self):
        return self.web3.personal.newAccount("KuqYeU59NZ4vKsN7egho")

    def save_answer(self):
        # eth_account = 0x405d64654553b3c907fb3c9ce42aac34295aa314
        wallet = "0x405d64654553b3c907fb3c9ce42aac34295aa314"
        address = "0x405be7fEed8E8EcBE996FeD76Cb6bF74Ed90bb31"

        return self.web3.personal.signAndSendTransaction(
            {
                'from': wallet,
                'to': address,
                'value': 1

            },
            "my-very-secret-word"
        )


def convert_to_str(json_list):
    res = json.dumps(json_list)
    return res


def convert_back(json_str):
    return json.loads(json_str)


if __name__ == "__main__":

    web3 = Web3(HTTPProvider("http://localhost:8545"))
    # web3 = Web3(TestRPCProvider())
    contract_src = '''
pragma solidity ^0.4.17;

contract QuestionaryStorage {
    string public test;

    function QuestionaryStorage() {
        test = 'Test String';
    }
    modifier onlyBy(address _account)
    {
        require(msg.sender == _account);
        _;
    }

    address public owner;
    mapping (address => string) public answers;

    function saveAnswers(string _voteAnswers) public
    {
        answers[msg.sender] = _voteAnswers;
    }

    function getAnswers() constant returns (string) {
        return test;
    }
}
'''
#     contract_src = '''
# pragma solidity ^0.4.17;
#
# contract Greeter {
#     string public greeting;
#
#     function Greeter() {
#         greeting = 'Hello';
#     }
#
#     function setGreeting(string _greeting) public {
#         greeting = _greeting;
#     }
#
#     function greet() constant returns (string) {
#         return greeting;
#     }
# }
# '''
    compiled_sol = compile_source(contract_src)  # Compiled source code
    contract_interface = compiled_sol['<stdin>:QuestionaryStorage']
    # contract_interface = compiled_sol['<stdin>:Greeter']

    # Instantiate and deploy contract
    contract = web3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

    # Get transaction hash from deployed contract
    tx_hash = contract.deploy(transaction={'from': web3.eth.accounts[0], 'gas': 410000})

    # Get tx receipt to get contract address
    tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
    contract_address = tx_receipt['contractAddress']

    # Contract instance in concise mode
    contract_instance = web3.eth.contract(contract_interface['abi'], contract_address,
                                          ContractFactoryClass=ConciseContract)
    ll = [
        {
            'q': 'как дела?',
            'a': 'хорошо'
        },
        {
            'q': 'точно?',
            'a': 'нет'
        }
    ]
    dump = convert_to_str(ll)
    print('Contract value: {}'.format(contract_instance.transact({'from': web3.eth.accounts[0]}).getAnswers()))
    # print('Contract value: {}'.format(contract_instance.greet()))
    # contract_instance.setGreeting('Nihao', transact={'from': web3.eth.accounts[0]})
    # print('Setting value to: Nihao')
    # print('Contract value: {}'.format(contract_instance.greet()))
    # print(dump)
    # print(convert_back(dump))
