import json
import requests
from data.data import Database
from models.block import Block
from models.transaction import Transaction


class TransactionsService:
    def __init__(self, file_path):
        self.db = Database(file_path)

    def save_transactions_by_block_range(self, endpoint, block_range):
        block_start, block_end = self._parse_block_range(block_range)
        for block_id in range(
            int(block_start), int(block_end) + 1
        ):  # iterate through each block
            block_hex = self._string_to_hex(str(block_id))
            block_data = self.fetch_block_data(endpoint, block_hex)
            block = self._parse_block(block_data)
            if not block:
                continue
            self.db._save_block_data(block)

            transactions = self._parse_transaction(block.transactions)
            for transaction in transactions:
                self.db._save_transaction_data(transaction)
        self.db._print_blocks()
        self.db._print_transactions()

    def fetch_block_data(self, endpoint, block_hex):
        payload = json.dumps(
            {
                "method": "eth_getBlockByNumber",
                "params": [block_hex, True],
                "jsonrpc": "2.0",
                "id": 1,
            }
        )
        headers = {"Content-Type": "application/json"}

        try:
            block_data = requests.request(
                "POST", endpoint, headers=headers, data=payload
            )
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("Unhandled", err)

        return block_data

    def _parse_block(self, block):
        block_result = block.json()["result"]
        if not block_result:
            return None
        block = Block(
            block_result["hash"],
            block_result["number"],
            block_result["timestamp"],
            block_result["transactions"],
        )
        return block

    def _parse_transaction(self, transactions) -> list[Transaction]:
        transaction_tuples = []
        for transaction in transactions:
            transaction_obj = Transaction(
                transaction["hash"],
                transaction["blockHash"],
                transaction["blockNumber"],
                transaction["from"],
                transaction["to"],
                transaction["value"],
            )
            transaction_tuples.append(transaction_obj)
        return transaction_tuples

    def _parse_block_range(self, block_range: str):
        return block_range.split("-")

    def _string_to_hex(self, a: str):
        return hex(int(a))
