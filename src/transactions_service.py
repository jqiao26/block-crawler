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

    def save_transactions_by_block_range(self, endpoint, block_range, num_workers):
        block_start, block_end = self._parse_block_range(block_range)
        self.endpoint = endpoint

        blocks = [b for b in range(int(block_start), int(block_end) + 1)]
        batches = [
            blocks[i : i + num_workers] for i in range(0, len(blocks), num_workers)
        ]
        results: list[Block] = []
        print(f"Starting processing with {num_workers} workers")
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            for batch in batches:
                print("Processing blocks: ", batch)
                futures = [
                    executor.submit(
                        self.block_fetch_helper, self._string_to_hex(str(block))
                    )
                    for block in batch
                ]
                results += [future.result() for future in futures if future.result()]
        self.db._save_block_data_batch(results)
        for block_result in results:
            transactions = self._parse_transaction(block_result.transactions)
            self.db._save_transaction_data_batch(transactions)
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
            response = requests.request(
                "POST", self.endpoint, headers=headers, data=payload
            )
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
            raise err
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
            raise err
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
            raise err
        except requests.exceptions.RequestException as err:
            print("Unhandled Error", err)
            raise err

        if "result" not in response.json():
            print(response.json(), "No result found")
            raise err

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
