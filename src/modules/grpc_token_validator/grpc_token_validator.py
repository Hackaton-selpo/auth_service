# auth_service_server.py
import asyncio
import logging
import threading

import grpc
from concurrent import futures

from fastapi import HTTPException

from src.modules.grpc_token_validator import auth_service_pb2
from src.modules.grpc_token_validator import auth_service_pb2_grpc
import jwt

from src.core.config import load_config
from src.modules.reg_module.jwt_module.depends import validate_access_token_payload

config = load_config()
logger = logging.getLogger(__name__)


class AuthServiceServicer(auth_service_pb2_grpc.AuthServiceServicer):
    def CheckToken(self, request, context):

        token: str = request.token
        try:
            payload: dict = jwt.decode(token, config.jwt.public_key_path, algorithms=[config.jwt.algorithm])
            asyncio.run(validate_access_token_payload(payload))
            return auth_service_pb2.TokenResponse(
                valid=True,
                claims={
                    k: str(v) if not isinstance(v, (int, float)) else str(v)
                    for k, v in payload.items()
                }
            )
        except HTTPException as e:
            return auth_service_pb2.TokenResponse(
                valid=False,
                error=str(e.detail)
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_service_pb2_grpc.add_AuthServiceServicer_to_server(AuthServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("Auth gRPC server running on port 50051...")
    server.wait_for_termination()


def run_grpc():
    grpc_thread = threading.Thread(target=serve, daemon=True)
    grpc_thread.start()
