"""Guard the public API surface and typed signatures."""

import inspect

import aiopybit
from aiopybit.http_methods.order_methods import OrderMixin


def test_typed_names_are_exported():
	for name in (
		'ByBitResponse',
		'OrderSide',
		'OrderType',
		'TimeInForce',
		'ByBitCategories',
		'AccountType',
	):
		assert name in aiopybit.__all__
		assert hasattr(aiopybit, name)


def test_create_order_uses_literal_annotations():
	sig = inspect.signature(OrderMixin.create_order)
	# side/order_type should be Literal enums, not bare str.
	assert 'Buy' in str(sig.parameters['side'].annotation)
	assert 'Limit' in str(sig.parameters['order_type'].annotation)
	assert sig.return_annotation is aiopybit.ByBitResponse
