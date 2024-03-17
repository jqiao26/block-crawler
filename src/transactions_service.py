from itertools import islice
import json
import requests
from data.data import Database
from models.block import Block
from models.transaction import Transaction
from concurrent.futures import ThreadPoolExecutor


WEI_ETHER_CONVERSION = 10**-18


class TransactionsService:
    def __init__(self, file_path):
        self.db = Database(file_path)

    def save_transactions_by_block_range(self, endpoint, block_range):
        block_start, block_end = self._parse_block_range(block_range)
        self.endpoint = endpoint
        blocks = [b for b in range(int(block_start), int(block_end) + 1)]
        results = []

        # for block_id in range(
        #     int(block_start), int(block_end) + 1
        # ):  # iterate through each block
        #     print("Saving block ", block_id)
        #     block_hex = self._string_to_hex(str(block_id))
        #     raw_block_data = self.fetch_block_data(block_hex)
        #     block = self._parse_block(raw_block_data)
        #     if not block:
        #         continue
        #     self.db._save_block_data(block)
        #     transactions = self._parse_transaction(block.transactions)
        #     for transaction in transactions:
        #         self.db._save_transaction_data(transaction)

        batches = [blocks[i : i + 3] for i in range(0, len(blocks), 3)]

        with ThreadPoolExecutor(max_workers=3) as executor:
            for batch in batches:  # iterate through each block
                print(batch)
                futures = [executor.submit(self.block_fetch_helper, self._string_to_hex(str(block))) for block in batch]
                results += [future.result() for future in futures if future.result()]
        self.db._save_block_data_batch(results)
        for block_result in results:
            transactions = self._parse_transaction(block_result.transactions)
            for transaction in transactions:
                self.db._save_transaction_data(transaction)
        self.db._print_blocks()
        self.db._print_transactions()

    def block_fetch_helper(self, block_hex):
        raw_block_data = self.fetch_block_data(block_hex)
        if not raw_block_data:
            return None
        return self._parse_block(raw_block_data)

    def fetch_block_data(self, block_hex):
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
            response = requests.request("POST", self.endpoint, headers=headers, data=payload)
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("Unhandled", err)

        if 'result' not in response.json():
            print('No result found')
            return None

        return response.json()["result"]

    def _parse_block(self, raw_block_data):        
        block = Block(
            raw_block_data["hash"],
            raw_block_data["number"],
            raw_block_data["timestamp"],
            raw_block_data["transactions"],
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
                self._convert_to_ether(self._hex_to_int(transaction["value"])),
            )
            transaction_tuples.append(transaction_obj)
        return transaction_tuples

    def _parse_block_range(self, block_range: str):
        return block_range.split("-")

    def _string_to_hex(self, a: str):
        return hex(int(a))

    def _convert_to_ether(self, val: int):
        return val * WEI_ETHER_CONVERSION

    def _hex_to_int(self, h: str):
        return int(h, 16)
