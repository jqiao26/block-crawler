import sqlite3
from sqlite3 import Error
import pandas as pd

from models.block import Block
from models.transaction import Transaction


class Database:
    def __init__(self, file_path):
        self.conn = self.create_connection(file_path)
        self.init_tables()

    def _save_block_data(self, block: Block):
        sql = f"""INSERT INTO blocks(hash, number, timestamp) 
                VALUES(?,?,?)
        """
        block_tup = (block.hash, block.number, block.timestamp)
        cur = self.conn.cursor()
        cur.execute(sql, block_tup)
        self.conn.commit()

    def _save_block_data_batch(self, blocks: list[Block]):
        sql = f"""INSERT INTO blocks(hash, number, timestamp) 
                VALUES(?,?,?)
        """
        block_tups = []
        for block in blocks:
            block_tups.append((block.hash, block.number, block.timestamp))
        cur = self.conn.cursor()
        cur.executemany(sql, block_tups)
        self.conn.commit()

    def _save_transaction_data(self, transaction: Transaction):
        sql = f"""INSERT INTO transactions(hash, blockHash, blockNumber, t_from, t_to, value) 
                VALUES(?,?,?,?,?,?)
        """
        transaction_tup = (
            transaction.hash,
            transaction.block_hash,
            transaction.block_number,
            transaction.t_from,
            transaction.t_to,
            transaction.value,
        )
        cur = self.conn.cursor()
        cur.execute(sql, transaction_tup)
        self.conn.commit()

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)

    def _create_table(self, sql_command):
        try:
            c = self.conn.cursor()
            c.execute(sql_command)
        except Error as e:
            print(e)

    def init_tables(self):
        blocks_sql_command = """
        CREATE TABLE IF NOT EXISTS blocks (
            hash text PRIMARY KEY,
            number text,
            timestamp text
        );"""

        transactions_sql_command = """
        CREATE TABLE IF NOT EXISTS transactions (
            hash int PRIMARY KEY,
            blockHash int,
            blockNumber int,
            t_from int,
            t_to int,
            value int,
            FOREIGN KEY (blockHash) REFERENCES blocks (hash)
        );"""

        self._create_table(blocks_sql_command)
        self._create_table(transactions_sql_command)

    def _print_transactions(self):
        pd.set_option('display.max_columns', None)
        # print(pd.read_sql_query("SELECT * FROM transactions", self.conn))
        print(pd.read_sql_query("SELECT * FROM transactions", self.conn))

    def _print_blocks(self):
        print(pd.read_sql_query("SELECT * FROM blocks ORDER BY timestamp", self.conn))
