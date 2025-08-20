from aiopybit import ByBitClient

API_KEY = ''
API_SECRET = ''
MODE = 'demo'

client = ByBitClient(API_KEY, API_SECRET, MODE)


async def main():
	# get account info
	account_info = await client.get_account_info()
	print(account_info)

	# get instruments
	ticker = await client.get_instruments_info('linear', 'BTCUSDT')
	print(ticker)

	# get ticker
	ticker = await client.get_ticker_price('linear', 'BTCUSDT')
	print(ticker)

	# get orders
	orders = await client.get_orders('linear', 'BTCUSDT')
	print(orders)

	# set leverage
	account_info = await client.set_leverage('linear', 'BTCUSDT', 2)
	print(account_info)

	# create order
	order = await client.create_order(
		'linear', 'BTCUSDT', 'Buy', 'Market', qty=5, order_link_id='1'
	)
	print(order)

	# modify order
	order = await client.amend_order(
		'linear',
		'BTCUSDT',
		stop_loss=10,
		order_link_id='1',
	)
	print(order)

	# cancel order
	order = await client.cancel_order('linear', 'BTCUSDT', '1')
	print(order)


if __name__ == '__main__':
	import asyncio

	asyncio.run(main())
