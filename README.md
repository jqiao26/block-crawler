# Technical Challenge

## Running the Code

The code is run by calling main as follows: `python3 main.py https://smart-frosty-sun.quiknode.pro/<KEY>/ sqlite\\db\\database.db 18908800-18909050`.

Some additional arguments were created mainly for testing purposes including adding debug flag which cleans up the database after running and testing. Another optional argument for the number of workers was also added to speed up the processing (defaults to 2). Further discussion about the workers is in the below section.

As output, I print out the blocks that are being processed (`num_workers` blocks at a time) and print out the database `blocks` and `transactions` tables respectively with Pandas. Finally, I printed out the largest block and value transferred as a tuple with (block_number, amount_transferred).

I ran tests using `pytest`

## Service Section

In the `/src/transactions_service` file, I created a `TransactionsService` class that was responsible for fetching blocks and saving them to the database. It also contained other helper functions such as parsing dates, converting strings and hex values, and converting between wei and ether.

In the `save_transactions_by_block_range` function, I first parse the `block_range` string to get the beginning and ending block, then I create an array with each of the blocks. Since processing one block at a time was slow and there was no dependency between blocks, I created a list of `batches` of blocks to process in parallel and took advantage of `ThreadPoolExecutor` to speed up the processing of blocks. Due to limitations of being on the free tier of the QuickNode API, the max workers I could use without hitting the free tier requests per second limit was `num-workers=2`. After all the blocks are processed, the resulting `Block` objects are saved in `result` and inserted all together into the blocks table. In line 37, all of the transactions that belong to a given block are saved to the transactions table and the tables are printed at the end.

In `fetch_block_data`, I query the `eth_getBlockByNumber` method from the API using a POST call. I introduced some additional error handling and return the result JSON if successful.

For `_parse_transaction` one point of note is that I saved the value of ether directly into the transactions table so that future conversion would not be necessary.

## Data Section

In the `/data` folder, there are two files:

### `data.py`

The first file is `data.py`, which contains a `Database` class that is used throughout the project. In the `init` function, a connection is made to the SQLite database with the path provided, and the `init_tables()` function prepares all the necessary tables; `blocks` and `transactions`. In the `transactions` table, I introduced a foreign key `blockHash` from the `blocks` table so that I can relate any `transaction` back to its corresponding block.

The other functions in the file include helper functions to insert transactions and blocks to the database (both single and in batches) as well as helper functions to print the `blocks` and `transactions` tables that helped me debug and understand the data.

### `block_volume_query.py`

This file is the script necessary for Part 2, described below.

## Part 2

Part 2 was done in the `block_volume_query.py` file. It initializes a `Database` object and converts the input start and end times to hex so that they can be used to query the database (which stored the timestamp of the block in hex).

The `transaction` query selects the `block` number and sum of the `transactions` ordered by sorted values (desc) and gets the max transferred value by using limit 1. A left join was used to get the records from the `transaction`s table where the foreign key `blockHash` matched the `block`'s `hash` key. The timestamp was filtered in the `blocks` table to be between `start_hex` and `end_hex` inclusive.

After executing the SQL command, I used `cursor.fetchone()` to get the max value transferred,otherwise setting it to a default tuple `(-1, float('-inf'))`. The return type from the script is a tuple including the block number and its associated sum of transaction values (amount transferred).

## Models Section

The models section helped define the `Block` and `Transaction` objects and the properties they possessed.

## Testing

The `test_query_database.py` file tested the process of inserting `transaction`s and `block`s to the respective tables and getting the largest block volume from the test db. Transactions and block names were simplified to make the tests more readable.

The `test_transactions_service.py` file tested everything in the transactions service including helper functions, parsing and fetching blocks.

## Comments and Assumptions

- I added the converted ether value directly to the Transaction table so that conversion was not necessary afterwards
- Assumed date ranges to be processed in UTC, as standard

NOTE: The `result.txt` file contains the resulting block number and the total volume from Part 2
