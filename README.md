# Technical Challenge

## Running the Code

The code is run by calling main as follows: `python3 main.py https://smart-frosty-sun.quiknode.pro/413ba230cbf8c88dd6e2bfd9ecb0a8d645f6d801/ sqlite\\db\\database.db 18908800-18909050`.

Some additional arguments were created mainly for testing purposes including optionally running part 2 or adding debug which helped clean up the database after running and testing.`

I ran tests using `pytest`

## Service Section

In the `/src/transactions_service` file, I created a `TransactionsService` class that was responsible for fetching blocks and saving them to database. It also contained other helper functions such as parsing dates, converting strings and hex values, and converting between wei and ether.

In the `save_transactions_by_block_range` function, I first parse the `block_range` string to get the beginning and ending block then I create an array with each of the blocks. Since processing one block at a time was slow and there was no dependency between blocks, I created a `batches` list of block lists and took advantage of `ThreadPoolExecutor` to speed up the processing of blocks. Due to limitations of being on the free tier of the QuickNode API, the max workers I could use without hitting the requests per second limit was `NUM_WORKERS=2`. After all the blocks are processed, the resulting `Block` objects are saved in `result` and inserted altogether into the blocks table. In line 37, all of the transactions that belong to a given block are saved to the transactions table and the tables are printed at the end.

In `fetch_block_data`, I query the `eth_getBlockByNumber` method from the API using a POST call. I introduced some additional error handling and return the result JSON if successful.

For `_parse_transaction` one point of note is that I saved the value of ether directly into the transactions table so that future conversion would not be necessary.

## Data Section

In the `/data` folder, there are two files:

### `data.py`

First file is the `data.py` file that contains a Database class that is used throughout the project. In the init, a connection is made to the SQLite database with the path provided and the `init_tables()` function prepares all the necessary tables `blocks` and `transactions`. In the `transactions` table, I introduced a foreign key blockHash from the `blocks` table so that I can relate any transaction back to it's corresponding block.

The other functions in the file include helper functions to insert transactions and blocks to the database (and in batches) as well as helper functions to print the blocks and transactions tables that helped me debug and understand the data.

### `block_volume_query.py`

Next file is the script necessary for Part 2, described below...

## Part 2

Part 2 was done in the `block_volume_query.py` file. It initialized a `Database` object and converts the input start and end times to hex so that they can be used to query the database (which stored the timestamp of the block in hex).

The transaction query selects the block number and sum of the transactions ordered by sorted values (desc) and gets the max transferred value by using limit 1. Left join was used to get the records from the transactions table where the foreign key `blockHash` matched the blocks `hash` key. The timestamp was filtered in the blocks table to be between `start_hex` and `end_hex` inclusive.

After executing the SQL command, I used `cursor.fetchone()` to get the max value transferred (otherwise setting it to -1). The return type from the script is a tuple including the block number and it's associated sum of transaction values (amount transferred).

## Models Section

The models section helped define the `Block` and `Transaction` objects and the properties they possessed.

## Testing

The `test_query_database.py` file tested the process of inserting transactions and blocks to the respective tables and getting the largest block volume from the test db. Transactions and block names were simplified to make the tests more readable.

The `test_transactions_service.py` file tested everything in the transactions service including helper functions, parsing and fetching blocks.

## Comments and Assumptions

- I added the converted ether value directly to the Transaction table so that conversion was not necessary afterwards
- Assumed date ranges to be processed in UTC, as standard

NOTE: The `result.txt` file contains the resulting block number and the total volume from Part 2
