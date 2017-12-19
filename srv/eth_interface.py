from web3 import Web3, HTTPProvider


class Rinkeby:
    def __init__(self):
        self.web3 = Web3(HTTPProvider('http://172.19.0.2:8545'))
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


if __name__ == "__main__":
    rkb = Rinkeby()
    print(rkb.create_wallet())
