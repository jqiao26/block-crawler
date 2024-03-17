import os
import argparse
from src.transactions_service import TransactionsService
from data.query_database import get_largest_block_volume

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="block-crawler", description="Fetch blocks and transactions"
    )
    parser.add_argument("endpoint")
    parser.add_argument("file_path")
    parser.add_argument("block_range")
    parser.add_argument("-t", "--run-part-two", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")

    args = parser.parse_args()
    try:
      ts = TransactionsService(args.file_path)
      ts.save_transactions_by_block_range(args.endpoint, args.block_range)
      if args.run_part_two:
        res = get_largest_block_volume(
            args.file_path, "2024-01-01 00:00:00", "2024-01-01 00:30:00"
        )
        print(f"Largest block volume {res}")
    except Exception as e:
      print(e)
      if args.debug:
        os.remove(args.file_path)
      
