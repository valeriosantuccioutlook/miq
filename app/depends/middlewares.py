from datetime import datetime, timedelta
from typing import Any, Callable, Dict

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from app.settings import settings


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests based on client IP address.

    Args:
        :app: The FastAPI application instance.

    Description:
        This middleware limits the number of requests from each client IP address
        within a specified duration. If a client exceeds the allowed number of requests
        within the duration, subsequent requests from that client receive a 429 Too Many Requests
        response until the duration expires.

    Attributes:
        :request_counts (Dict): A dictionary to store request counts for each client IP address.
            The keys are client IP addresses, and the values are tuples containing the request count
            and the timestamp of the last request from that client.

    Methods:
        :dispatch(request: Request, call_next: Callable) -> JSONResponse | Response:
            Override of the dispatch method to perform rate limiting checks on incoming requests.
            Increments the request count for each request and blocks requests that exceed the rate limit.
    """

    def __init__(self, app) -> None:
        super().__init__(app=app)
        # store request counts for each IP
        self.request_counts: Dict[Any, Any] = {}

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> JSONResponse | Response:
        # get the client's IP address
        client_ip: str = request.client.host
        # check if IP is already present in request_counts
        request_count, last_request = self.request_counts.get(
            client_ip, (0, datetime.min)
        )
        # calculate the time elapsed since the last request
        elapsed_time: Any | timedelta = datetime.now() - last_request

        if elapsed_time > settings.RATE_LIMIT_DURATION:
            request_count = 1
        else:
            if request_count >= settings.RATE_LIMIT_REQUESTS:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"message": "Rate limit exceeded. Please try again later"},
                )
            request_count += 1

        # Update the request count and last request timestamp for the IP
        self.request_counts[client_ip] = (request_count, datetime.now())

        response: Response = await call_next(request)
        return response
