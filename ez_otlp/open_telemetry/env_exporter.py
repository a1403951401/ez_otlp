from typing import Optional, Sequence, Union, Tuple, Dict, Literal

from grpc import ChannelCredentials, Compression
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter as gRPCLogExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter as gRPCMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as gRPCTraceExporter,
)
from opentelemetry.exporter.otlp.proto.http._log_exporter import (
    OTLPLogExporter as HttpLogExporter,
)
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter as HttpMetricExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as HttpTraceExporter,
)
from opentelemetry.sdk._logs.export import LogExporter
from opentelemetry.sdk.metrics._internal.aggregation import Aggregation
from opentelemetry.sdk.metrics.export import AggregationTemporality
from opentelemetry.sdk.metrics.export import MetricExporter
from opentelemetry.sdk.trace.export import SpanExporter
from pydantic_settings import BaseSettings


class Exporter(BaseSettings):
    endpoint: Optional[str] = None
    gRPC: bool = True
    # TODO<Martin>: credentials compatible env settings
    credentials: Optional[ChannelCredentials] = None
    headers: Optional[Union[Sequence[Tuple[str, str]], Dict[str, str], str]] = None
    timeout: Optional[int] = None
    compression: Literal[0, 1, 2] = 0  # 0 NoCompression 1 Deflate 2 Gzip

    class Config:
        env_prefix = "EZ_"
        case_sensitive = False

    def get_span_exporter(
        self, span_exporter_cls: Union[gRPCTraceExporter | HttpTraceExporter] = None
    ) -> SpanExporter:
        self.compression: Compression
        if span_exporter_cls is None:
            span_exporter_cls = gRPCTraceExporter if self.gRPC else HttpTraceExporter
        return span_exporter_cls(
            endpoint=self.endpoint,
            headers=self.headers,
            timeout=self.timeout,
            compression=self.compression,
        )

    def get_log_export(
        self, log_exporter_cls: gRPCLogExporter | HttpLogExporter = None
    ) -> LogExporter:
        self.compression: Compression
        if log_exporter_cls is None:
            log_exporter_cls = gRPCLogExporter if self.gRPC else HttpLogExporter
        return log_exporter_cls(
            endpoint=self.endpoint,
            headers=self.headers,
            timeout=self.timeout,
            compression=self.compression,
        )

    def get_metric_exporter(
        self,
        metric_exporter_cls: Union[gRPCMetricExporter, HttpMetricExporter] = None,
        preferred_temporality: Dict[type, AggregationTemporality] = None,
        preferred_aggregation: Dict[type, Aggregation] = None,
        max_export_batch_size: Optional[int] = None,
    ) -> MetricExporter:
        self.compression: Compression
        if metric_exporter_cls is None:
            metric_exporter_cls = (
                gRPCMetricExporter if self.gRPC else HttpMetricExporter
            )
        return metric_exporter_cls(
            endpoint=self.endpoint,
            headers=self.headers,
            timeout=self.timeout,
            compression=self.compression,
            preferred_temporality=preferred_temporality,
            preferred_aggregation=preferred_aggregation,
        )


if __name__ == "__main__":
    print(Exporter(credentials=ChannelCredentials("test")).model_dump())
