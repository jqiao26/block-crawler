import pytest
import os 

from data.data import Database
from models.block import Block
from models.transaction import Transaction
from data.query_database import get_largest_block_volume

@pytest.fixture
def db_path():
  yield "test.db"
  os.remove("test.db")

@pytest.fixture
def setup_teardown_db(db_path):
    db = Database(db_path)
    blocks = [
      Block(
        "block1_hash",
        "1",
        "0x659207ff",
        ["transaction1"]
      ),
      Block(
        "block2_hash",
        "2",
        "0x6592080b",
        ["transaction2"]
      ),
      Block(
        "block3_hash",
        "3",
        "0x65920878",
        ["transaction3", "transaction4"]
      ),
    ]
    for block in blocks:
      db._save_block_data(
        block
      )

    transactions = [
      Transaction(
          "transaction1",
          "block1_hash",
          "1",
          "to1",
          "from1",
          "1",
        ),
        Transaction(
          "transaction2",
          "block2_hash",
          "2",
          "to2",
          "from2",
          "2",
        ),
        Transaction(
          "transaction3",
          "block3_hash",
          "3",
          "to3",
          "from3",
          "0.5",
        ),
        Transaction(
          "transaction4",
          "block3_hash",
          "3",
          "to4",
          "from4",
          "1.7",
        )

    ]
    for transaction in transactions:
      db._save_transaction_data(
        transaction
      )
    yield

def test_get_largest_block_volume(db_path, setup_teardown_db):
  start_date = "2024-01-01 00:30:00"
  end_date = "2024-01-01 00:35:00"
  block_number, max_value = get_largest_block_volume(db_path, start_date, end_date)
  assert block_number == 3
  assert max_value == 2.2