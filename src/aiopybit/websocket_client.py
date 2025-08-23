import asyncio
import hmac
import json
import logging
import time
from collections.abc import Callable
from typing import Any

import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger('aiopybit')


class ByBitWebSocketClient:
    def __init__(
        self,
        url: str,
        api_key: str | None = None,
        api_secret: str | None = None,
        ping_interval: int = 20,
        ping_timeout: int = 10,
        auto_reconnect: bool = True,
    ):
        self.url = url
        self.api_key = api_key
        self.api_secret = api_secret

        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.auto_reconnect = auto_reconnect

        self.topic_handlers: dict[str, Callable[[dict[str, Any]], None]] = {}

        self.ping_task: asyncio.Task | None = None
        self.listen_task: asyncio.Task | None = None
        self.reconnect_task: asyncio.Task | None = None

        # Reconnection state
        self.reconnect_attempts = 0
        self.is_reconnecting: bool = False

        self.is_connected: bool = False
        self.ws = None

    def _generate_signature(self, expires: int) -> str:
        """
        Generate HMAC signature for private channel authentication.

        Args:
            expires (int): Expiration timestamp for the signature.

        Returns:
            str: HMAC-SHA256 signature string.

        Raises:
            ValueError: If API secret is not provided.
        """
        if not self.api_secret:
            raise ValueError('API secret required for signature generation')

        return hmac.new(
            bytes(self.api_secret, 'utf-8'),
            bytes(f'GET/realtime{expires}', 'utf-8'),
            digestmod='sha256',
        ).hexdigest()

    @property
    def expires(self) -> int:
        """
        Generate expiration timestamp for authentication.

        Returns:
            int: Current timestamp plus 1 second in milliseconds.

        Example:
            >>> client = ByBitWebSocketClient('mainnet', 'key', 'secret')
            >>> expires = client.expires
            >>> print(expires)  # 1755369176733
        """
        return int((time.time() + 1) * 1000)

    async def _authenticate(self) -> None:
        """
        Perform authentication for private channels.

        Sends authentication request with API credentials and waits for confirmation.

        Raises:
            ValueError: If API key or secret is missing.
            ConnectionError: If authentication fails or WebSocket is not connected.

        Example:
            This method is called automatically when connecting to private channels.
            No direct usage required.
        """
        if not self.api_key or not self.api_secret:
            raise ValueError('API key and secret required for authentication')

        expires = self.expires
        signature = self._generate_signature(expires)

        await self.send(op='auth', args=[self.api_key, expires, signature])

        assert self.ws
        response = await self.ws.recv()
        auth_result = json.loads(response)

        if auth_result.get('success'):
            logger.debug('Authentication for %s successful', self.url)
        else:
            raise ConnectionError('Authentication failed for %s', self.url)

    async def send(self, **kwargs) -> None:
        """
        Send a message through the WebSocket connection.

        Args:
            **kwargs: Message parameters to be JSON-encoded and sent.

        Raises:
            ConnectionError: If WebSocket is not connected.
            ConnectionClosed: If connection is closed during send.

        Example:
            >>> await client.send(op='subscribe', args=['tickers.BTCUSDT'])
            >>> await client.send(op='ping')
        """
        if not self.ws or not self.is_connected:
            raise ConnectionError('WebSocket not connected for %s', self.url)

        try:
            message = json.dumps(kwargs)
            await self.ws.send(message)
            logger.debug('Successfully sent for %s message: %s', self.url, message)
        except ConnectionClosed:
            logger.error('WebSocket connection for %s closed', self.url)
            self.is_connected = False
            raise
        except Exception as e:
            logger.error('Error sending for %s message: %s', self.url, e)
            raise

    async def connect(self) -> None:
        """
        Establish WebSocket connection to ByBit servers.

        Args:
            channel (ChannelType): Channel type - 'public', 'private', or 'trade'.
            category (ByBitCategories): Category for public channels - 'linear', 'spot', or 'option'.

        Raises:
            ValueError: If channel/category combination is invalid for the mode.
            ConnectionError: If connection establishment fails.

        Example:
            >>> client = ByBitWebSocketClient('mainnet', 'key', 'secret')
            >>> await client.connect('public', 'linear')
            >>> # Now ready to subscribe to public linear contract streams
        """
        if self.is_connected:
            logger.warning('WebSocket already connected for %s', self.url)
            return

        try:
            self.ws = await websockets.connect(self.url)
            self.is_connected = True
            logger.debug('WebSocket connection for %s established', self.url)

            if 'public' not in self.url:
                await self._authenticate()

            self.ping_task = asyncio.create_task(self._ping_handler())
            self.listen_task = asyncio.create_task(self._message_listener())

        except Exception as e:
            logger.error('Error connecting for % to WebSocket: %s', self.url, e)
            self.is_connected = False
            raise

    async def _ping_handler(self) -> None:
        """
        Handle periodic ping messages to maintain WebSocket connection.

        Sends ping messages at regular intervals defined by ping_interval.
        Automatically stops when connection is closed or an error occurs.

        Example:
            This method runs automatically in background when connected.
            No direct usage required.
        """
        while self.is_connected:
            try:
                logger.debug('Sending ping for %s', self.url)
                await self.send(op='ping')
                await asyncio.sleep(self.ping_interval)
            except ConnectionClosed:
                logger.warning(
                    'WebSocket connection for %s closed during ping', self.url
                )
                self.is_connected = False
                if self.auto_reconnect and not self.is_reconnecting:
                    logger.info(
                        'Starting automatic reconnection for %s from ping handler',
                        self.url,
                    )
                    self.reconnect_task = asyncio.create_task(self._reconnect())
                break
            except Exception as e:
                logger.error('Error during ping for %s: %s', self.url, e)
                break

    async def _message_listener(self) -> None:
        """
        Listen for incoming WebSocket messages and handle them.

        Continuously receives messages from WebSocket connection and dispatches
        them to appropriate handlers based on message type and topic.

        Example:
            This method runs automatically in background when connected.
            No direct usage required.
        """
        try:
            while self.is_connected and self.ws:
                try:
                    message = await self.ws.recv()
                    logger.debug('Received message for %s: %s', self.url, message)

                    try:
                        data = json.loads(message)
                        await self._handle_message(data)
                    except json.JSONDecodeError as e:
                        logger.error('Error decoding message for %s: %s', self.url, e)

                except ConnectionClosed:
                    logger.warning('WebSocket connection closed for %s', self.url)
                    self.is_connected = False
                    if self.auto_reconnect and not self.is_reconnecting:
                        logger.info('Starting automatic reconnection for %s', self.url)
                        self.reconnect_task = asyncio.create_task(self._reconnect())
                    break

        except Exception as e:
            logger.error('Error in message listener for %s: %s', self.url, e)
            self.is_connected = False

    async def _handle_message(self, data: dict[str, Any]) -> None:
        """
        Handle incoming WebSocket messages based on their type.

        Processes different message types including pong responses, subscription
        confirmations, and topic data messages.

        Args:
            data (dict): Parsed JSON message from WebSocket.

        Example:
            This method is called automatically by _message_listener.
            No direct usage required.
        """
        op = data.get('op')

        # Handle ping
        if op == 'pong':
            logger.debug('Received pong for %s', self.url)
            return

        # Handle op
        if op == 'subscribe':
            if data.get('success'):
                logger.debug('Successful subscription for %s: %s', self.url, data)
            else:
                logger.error('Error subscribing for %s: %s', self.url, data)
            return

        # Handle topics
        if 'topic' in data:
            topic = data.get('topic')
            if topic and topic in self.topic_handlers:
                handler = self.topic_handlers[topic]
                await asyncio.create_task(self._safe_callback(handler, data))
            else:
                logger.debug('No handler for %s topic: %s', self.url, topic)

    async def _safe_callback(self, handler: Callable, data: dict[str, Any]) -> None:
        """
        Safely execute user-provided callback functions.

        Handles both synchronous and asynchronous callback functions with
        proper error handling to prevent callback errors from crashing the client.

        Args:
            handler (Callable): User-provided callback function to execute.
            data (dict): Message data to pass to the callback.

        Example:
            This method is used internally to call user callbacks.
            No direct usage required.
        """
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(data)
            else:
                handler(data)
        except Exception as e:
            logger.error('Error in callback for %s: %s', self.url, e)

    async def _reconnect(self) -> None:
        """
        Handle automatic reconnection with exponential backoff.

        Attempts to reconnect to the WebSocket and restore all subscriptions.
        Uses exponential backoff strategy to avoid overwhelming the server.
        """
        if self.is_reconnecting:
            return

        self.is_reconnecting = True
        logger.info('Starting automatic reconnection process for %s', self.url)

        while True:
            try:
                # Calculate exponential backoff delay
                delay = 2
                logger.info(
                    'Reconnection attempt %d in %.1f seconds for %s',
                    self.reconnect_attempts + 1,
                    delay,
                    self.url,
                )
                await asyncio.sleep(delay)

                # Clean up old connection
                if self.ws:
                    try:
                        await self.ws.close()
                    finally:
                        self.ws = None

                await self.connect()

                # Restore subscriptions
                if self.topic_handlers:
                    logger.info(
                        'Restoring %s subscriptions for %s',
                        list(self.topic_handlers.keys()),
                        self.url,
                    )

                    try:
                        await self.send(
                            op='subscribe', args=[self.topic_handlers.keys()]
                        )
                        logger.debug(
                            'Restored subscription for %s to: %s',
                            self.url,
                            list(self.topic_handlers.keys()),
                        )
                    except Exception as e:
                        logger.error(
                            'Failed to restore subscription for %s: %s',
                            self.url,
                            str(e),
                        )

                logger.info('✅ Reconnection successful!')
                self.reconnect_attempts = 0
                self.is_reconnecting = False
                return

            except Exception as e:
                self.reconnect_attempts += 1
                logger.error(
                    'Reconnection attempt %d failed: %s',
                    self.reconnect_attempts,
                    str(e),
                )

    async def close(self) -> None:
        """
        Close the WebSocket connection and clean up resources.

        Cancels all running tasks (ping and message listener) and closes
        the WebSocket connection gracefully.

        Example:
            >>> await client.close()
            >>> # Connection is now closed and resources cleaned up
        """
        logger.debug('Closing WebSocket connection for %s', self.url)

        self.is_connected = False
        self.is_reconnecting = False

        # Cancel pending tasks
        if self.ping_task and not self.ping_task.done():
            self.ping_task.cancel()
            try:
                await self.ping_task
            except asyncio.CancelledError:
                pass

        if self.listen_task and not self.listen_task.done():
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                pass

        if self.reconnect_task and not self.reconnect_task.done():
            self.reconnect_task.cancel()
            try:
                await self.reconnect_task
            except asyncio.CancelledError:
                pass

        # Close WebSocket connection
        if self.ws:
            await self.ws.close()

        logger.debug('WebSocket connection closed for %s', self.url)

    async def unsubscribe(self, topic: str) -> bool:
        """
        Unsubscribe from a specific topic.

        Removes the topic handler and sends an unsubscribe message to the server.

        Args:
            topic (str): Topic name to unsubscribe from (e.g., 'tickers.BTCUSDT').

        Returns:
            bool: True if successfully unsubscribed, False if topic was not subscribed.

        Example:
            >>> success = await client.unsubscribe('tickers.BTCUSDT')
            >>> if success:
            ...     print('Successfully unsubscribed from BTCUSDT ticker')
        """
        if topic not in self.topic_handlers:
            return False
        await self.send(op='unsubscribe', args=[topic])
        del self.topic_handlers[topic]
        return True
