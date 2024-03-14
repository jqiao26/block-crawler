import sqlite3
from data.data import Database
from datetime import datetime
import time


WEI_ETHER_CONVERSION = 10**-18


def get_largest_block_volume(file_path, start_date: str, end_date: str):
    db = Database(file_path)
    db._print_blocks()

    start_dt = _convert_str_to_datetime(start_date)
    end_dt = _convert_str_to_datetime(end_date)
    start_hex = _convert_datetime_to_hex(start_dt)
    end_hex = _convert_datetime_to_hex(end_dt)

    # query = f"""
    #     # SELECT hash from blocks WHERE timestamp >= {start_hex} AND timestamp <= {end_hex};
    # """

    query = f"""
        SELECT hash from blocks WHERE timestamp >= "0x6591fc3b" AND timestamp <= "0x6591fc47";
    """
    cursor = db.conn.execute(query)
    blocks_in_date_range = cursor.fetchall()

    max_volume = float("-inf")
    for block_hash in blocks_in_date_range:
        transaction_query = f"""
            SELECT value from transactions WHERE blockHash = "{block_hash[0]}";
        """
        cursor = db.conn.execute(transaction_query)
        transactions_in_block = cursor.fetchall()
        transaction_run_sum = 0
        for transaction in transactions_in_block:
            transaction_run_sum += _convert_hex_to_int(transaction[0])
        max_volume = max(max_volume, transaction_run_sum)
    print(max_volume * WEI_ETHER_CONVERSION)
    return max_volume * WEI_ETHER_CONVERSION if max_volume != float("-inf") else -1


def _convert_str_to_datetime(s: str):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def _convert_datetime_to_hex(d: datetime):
    printunixtime = time.mktime(d.timetuple())
    return hex(int(printunixtime))


def _convert_hex_to_int(h: str):
    return int(h, 16)
