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

    args = parser.parse_args()
    ts = TransactionsService(args.file_path)
    # ts.save_transactions_by_block_range(args.endpoint, args.block_range)
    get_largest_block_volume(
        args.file_path, "2024-01-01 00:00:00", "2024-01-01 00:30:00"
    )
