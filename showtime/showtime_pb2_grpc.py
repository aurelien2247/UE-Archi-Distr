# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import showtime_pb2 as showtime__pb2

GRPC_GENERATED_VERSION = '1.66.1'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in showtime_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ShowtimeServiceStub(object):
    """Service Showtime
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetShowtimes = channel.unary_unary(
                '/showtime.ShowtimeService/GetShowtimes',
                request_serializer=showtime__pb2.GetShowtimesRequest.SerializeToString,
                response_deserializer=showtime__pb2.GetShowtimesResponse.FromString,
                _registered_method=True)
        self.GetShowtimesByDate = channel.unary_unary(
                '/showtime.ShowtimeService/GetShowtimesByDate',
                request_serializer=showtime__pb2.GetShowtimesByDateRequest.SerializeToString,
                response_deserializer=showtime__pb2.GetShowtimesByDateResponse.FromString,
                _registered_method=True)


class ShowtimeServiceServicer(object):
    """Service Showtime
    """

    def GetShowtimes(self, request, context):
        """RPC pour récupérer tous les horaires
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetShowtimesByDate(self, request, context):
        """RPC pour récupérer les horaires par date
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ShowtimeServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetShowtimes': grpc.unary_unary_rpc_method_handler(
                    servicer.GetShowtimes,
                    request_deserializer=showtime__pb2.GetShowtimesRequest.FromString,
                    response_serializer=showtime__pb2.GetShowtimesResponse.SerializeToString,
            ),
            'GetShowtimesByDate': grpc.unary_unary_rpc_method_handler(
                    servicer.GetShowtimesByDate,
                    request_deserializer=showtime__pb2.GetShowtimesByDateRequest.FromString,
                    response_serializer=showtime__pb2.GetShowtimesByDateResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'showtime.ShowtimeService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('showtime.ShowtimeService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ShowtimeService(object):
    """Service Showtime
    """

    @staticmethod
    def GetShowtimes(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/showtime.ShowtimeService/GetShowtimes',
            showtime__pb2.GetShowtimesRequest.SerializeToString,
            showtime__pb2.GetShowtimesResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetShowtimesByDate(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/showtime.ShowtimeService/GetShowtimesByDate',
            showtime__pb2.GetShowtimesByDateRequest.SerializeToString,
            showtime__pb2.GetShowtimesByDateResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
