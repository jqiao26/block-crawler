import os
import argparse
from src.transactions_service import TransactionsService
from data.block_volume_query import get_largest_block_volume


def main(args=None):
    try:
        ts = TransactionsService(args.file_path)
        try:
            num_workers = int(args.num_workers)
            if num_workers <= 0 or num_workers > 10:
                raise Exception("Number of workers invalid number")
        except:
            print("Invalid number of workers passed in; using default of 2 workers")
            num_workers = 2
        ts.save_transactions_by_block_range(
            args.endpoint, args.block_range, num_workers
        )
        res = get_largest_block_volume(
            args.file_path, "2024-01-01 00:00:00", "2024-01-01 00:30:00"
        )
        print(f"Largest block and value transferred {res}")
    except Exception as e:
        print(e)
    if args.debug:
        os.remove(args.file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="block-crawler", description="Fetch blocks and transactions"
    )
    parser.add_argument("endpoint")
    parser.add_argument("file_path")
    parser.add_argument("block_range")
    parser.add_argument("-n", "--num-workers", default=2)
    parser.add_argument("-d", "--debug", action="store_true")

    args = parser.parse_args()

    main(args)
