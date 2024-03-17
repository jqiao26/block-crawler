from data.data import Database
from datetime import datetime, timezone
import time


WEI_ETHER_CONVERSION = 10**-18


def get_largest_block_volume(file_path, start_date: str, end_date: str):
    db = Database(file_path)
    # db._print_blocks()
    db._print_transactions()
    start_dt = _convert_str_to_datetime(start_date)
    end_dt = _convert_str_to_datetime(end_date)
    start_hex = _convert_datetime_to_hex(start_dt)
    end_hex = _convert_datetime_to_hex(end_dt)

    # query = f"""
    #     # SELECT hash from blocks WHERE timestamp >= {start_hex} AND timestamp <= {end_hex};
    # """

    # query = f"""
    #     SELECT hash from blocks WHERE timestamp >= "0x6591fc3b" AND timestamp <= "0x6591fc47";
    # """
    # cursor = db.conn.execute(query)

    # transaction_query = f"""
    #     select
    #     a.number
    #     ,sum(b.value)

    #     from
    #     blocks as a
    #     left join transactions as b
    #     on a.hash=b.blockHash
    #     where a.timestamp >= "0x6591fc3b" AND a.timestamp <= "0x6591fc47"
    #     group by a.hash

    #     order by value asc
    #     limit 1
    # """
    print(start_hex, end_hex)
    transaction_query = f"""
        select
        blocks.number
        ,sum(transactions.value) as value

        from
        blocks
        left join transactions
        on blocks.hash=transactions.blockHash
        where blocks.timestamp >= "{start_hex}" AND blocks.timestamp <= "{end_hex}"
        group by blocks.hash

        order by value desc
        limit 1
    """
        # where blocks.timestamp >= "0x6591fc3b" AND blocks.timestamp <= "0x6591fc47"
    cursor = db.conn.execute(transaction_query)
    maximum_transaction = cursor.fetchone()
    if not maximum_transaction:
        return -1
    block_number, max_value = (
        _convert_hex_to_int(maximum_transaction[0]),
        maximum_transaction[1],
    )
    print(block_number, max_value)
    return (block_number, max_value)


def _convert_str_to_datetime(s: str):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def _convert_datetime_to_hex(d: datetime):
    printunixtime = d.timestamp()
    return hex(int(printunixtime))


def _convert_hex_to_int(h: str):
    return int(h, 16)
