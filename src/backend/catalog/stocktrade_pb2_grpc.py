# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import stocktrade_pb2 as stocktrade__pb2


class CatalogServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Lookup = channel.unary_unary(
                '/CatalogService/Lookup',
                request_serializer=stocktrade__pb2.LookupRequest.SerializeToString,
                response_deserializer=stocktrade__pb2.LookupResponse.FromString,
                )
        self.Update = channel.unary_unary(
                '/CatalogService/Update',
                request_serializer=stocktrade__pb2.UpdateRequest.SerializeToString,
                response_deserializer=stocktrade__pb2.UpdateResponse.FromString,
                )


class CatalogServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Lookup(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Update(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CatalogServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Lookup': grpc.unary_unary_rpc_method_handler(
                    servicer.Lookup,
                    request_deserializer=stocktrade__pb2.LookupRequest.FromString,
                    response_serializer=stocktrade__pb2.LookupResponse.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=stocktrade__pb2.UpdateRequest.FromString,
                    response_serializer=stocktrade__pb2.UpdateResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'CatalogService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class CatalogService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Lookup(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/CatalogService/Lookup',
            stocktrade__pb2.LookupRequest.SerializeToString,
            stocktrade__pb2.LookupResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Update(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/CatalogService/Update',
            stocktrade__pb2.UpdateRequest.SerializeToString,
            stocktrade__pb2.UpdateResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class OrderServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Trade = channel.unary_unary(
                '/OrderService/Trade',
                request_serializer=stocktrade__pb2.TradeRequest.SerializeToString,
                response_deserializer=stocktrade__pb2.TradeResponse.FromString,
                )
        self.OrderLookup = channel.unary_unary(
                '/OrderService/OrderLookup',
                request_serializer=stocktrade__pb2.OrderLookupRequest.SerializeToString,
                response_deserializer=stocktrade__pb2.OrderLookupResponse.FromString,
                )
        self.StreamDBUpdates = channel.unary_stream(
                '/OrderService/StreamDBUpdates',
                request_serializer=stocktrade__pb2.Empty.SerializeToString,
                response_deserializer=stocktrade__pb2.CacheInvalidateRequest.FromString,
                )
        self.Save = channel.unary_unary(
                '/OrderService/Save',
                request_serializer=stocktrade__pb2.Empty.SerializeToString,
                response_deserializer=stocktrade__pb2.Empty.FromString,
                )
        self.IsAlive = channel.unary_unary(
                '/OrderService/IsAlive',
                request_serializer=stocktrade__pb2.Empty.SerializeToString,
                response_deserializer=stocktrade__pb2.AliveResponse.FromString,
                )
        self.SyncOrderRequest = channel.unary_unary(
                '/OrderService/SyncOrderRequest',
                request_serializer=stocktrade__pb2.OrderDBItem.SerializeToString,
                response_deserializer=stocktrade__pb2.Empty.FromString,
                )
        self.SyncOrderDB = channel.unary_stream(
                '/OrderService/SyncOrderDB',
                request_serializer=stocktrade__pb2.SyncRequest.SerializeToString,
                response_deserializer=stocktrade__pb2.OrderDBItem.FromString,
                )
        self.SetLeader = channel.unary_unary(
                '/OrderService/SetLeader',
                request_serializer=stocktrade__pb2.SetLeaderRequest.SerializeToString,
                response_deserializer=stocktrade__pb2.Empty.FromString,
                )
        self.GetLeader = channel.unary_unary(
                '/OrderService/GetLeader',
                request_serializer=stocktrade__pb2.Empty.SerializeToString,
                response_deserializer=stocktrade__pb2.GetLeaderResponse.FromString,
                )


class OrderServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Trade(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def OrderLookup(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StreamDBUpdates(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Save(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def IsAlive(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SyncOrderRequest(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SyncOrderDB(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetLeader(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetLeader(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OrderServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Trade': grpc.unary_unary_rpc_method_handler(
                    servicer.Trade,
                    request_deserializer=stocktrade__pb2.TradeRequest.FromString,
                    response_serializer=stocktrade__pb2.TradeResponse.SerializeToString,
            ),
            'OrderLookup': grpc.unary_unary_rpc_method_handler(
                    servicer.OrderLookup,
                    request_deserializer=stocktrade__pb2.OrderLookupRequest.FromString,
                    response_serializer=stocktrade__pb2.OrderLookupResponse.SerializeToString,
            ),
            'StreamDBUpdates': grpc.unary_stream_rpc_method_handler(
                    servicer.StreamDBUpdates,
                    request_deserializer=stocktrade__pb2.Empty.FromString,
                    response_serializer=stocktrade__pb2.CacheInvalidateRequest.SerializeToString,
            ),
            'Save': grpc.unary_unary_rpc_method_handler(
                    servicer.Save,
                    request_deserializer=stocktrade__pb2.Empty.FromString,
                    response_serializer=stocktrade__pb2.Empty.SerializeToString,
            ),
            'IsAlive': grpc.unary_unary_rpc_method_handler(
                    servicer.IsAlive,
                    request_deserializer=stocktrade__pb2.Empty.FromString,
                    response_serializer=stocktrade__pb2.AliveResponse.SerializeToString,
            ),
            'SyncOrderRequest': grpc.unary_unary_rpc_method_handler(
                    servicer.SyncOrderRequest,
                    request_deserializer=stocktrade__pb2.OrderDBItem.FromString,
                    response_serializer=stocktrade__pb2.Empty.SerializeToString,
            ),
            'SyncOrderDB': grpc.unary_stream_rpc_method_handler(
                    servicer.SyncOrderDB,
                    request_deserializer=stocktrade__pb2.SyncRequest.FromString,
                    response_serializer=stocktrade__pb2.OrderDBItem.SerializeToString,
            ),
            'SetLeader': grpc.unary_unary_rpc_method_handler(
                    servicer.SetLeader,
                    request_deserializer=stocktrade__pb2.SetLeaderRequest.FromString,
                    response_serializer=stocktrade__pb2.Empty.SerializeToString,
            ),
            'GetLeader': grpc.unary_unary_rpc_method_handler(
                    servicer.GetLeader,
                    request_deserializer=stocktrade__pb2.Empty.FromString,
                    response_serializer=stocktrade__pb2.GetLeaderResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'OrderService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class OrderService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Trade(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/OrderService/Trade',
            stocktrade__pb2.TradeRequest.SerializeToString,
            stocktrade__pb2.TradeResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def OrderLookup(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/OrderService/OrderLookup',
            stocktrade__pb2.OrderLookupRequest.SerializeToString,
            stocktrade__pb2.OrderLookupResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def StreamDBUpdates(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/OrderService/StreamDBUpdates',
            stocktrade__pb2.Empty.SerializeToString,
            stocktrade__pb2.CacheInvalidateRequest.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Save(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/OrderService/Save',
            stocktrade__pb2.Empty.SerializeToString,
            stocktrade__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def IsAlive(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/OrderService/IsAlive',
            stocktrade__pb2.Empty.SerializeToString,
            stocktrade__pb2.AliveResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SyncOrderRequest(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/OrderService/SyncOrderRequest',
            stocktrade__pb2.OrderDBItem.SerializeToString,
            stocktrade__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SyncOrderDB(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/OrderService/SyncOrderDB',
            stocktrade__pb2.SyncRequest.SerializeToString,
            stocktrade__pb2.OrderDBItem.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetLeader(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/OrderService/SetLeader',
            stocktrade__pb2.SetLeaderRequest.SerializeToString,
            stocktrade__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetLeader(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/OrderService/GetLeader',
            stocktrade__pb2.Empty.SerializeToString,
            stocktrade__pb2.GetLeaderResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
