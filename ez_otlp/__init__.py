import logging
from typing import Union, Type, Optional, Dict, List

from grpc import ChannelCredentials
from opentelemetry import _logs
from opentelemetry import metrics
from opentelemetry import trace
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
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs._internal.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal.aggregation import Aggregation
from opentelemetry.sdk.metrics.export import AggregationTemporality
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
)

from ez_otlp.open_telemetry.env_exporter import Exporter
from ez_otlp.open_telemetry.env_resource import EZResource

SpanProcessor = Union[
    SimpleSpanProcessor,
    BatchSpanProcessor,
]


class EZBase:
    exporter: Exporter = None
    resource: Resource = None

    def __init__(
        self,
        exporter: Exporter = None,
        resource: Resource | EZResource = None,
        credentials: Optional[ChannelCredentials] = None,
    ):
        if not self.exporter:
            if not exporter:
                exporter = Exporter(credentials=credentials)
            self.exporter = exporter

        if not self.resource:
            if not resource:
                resource = EZResource()
            if isinstance(resource, EZResource):
                resource: Resource = resource.get_resource()
            self.resource = resource


class EZTracer(EZBase):
    tracer_provider: TracerProvider

    def __init__(
        self,
        exporter: Exporter = None,
        resource: Resource | EZResource = None,
        credentials: Optional[ChannelCredentials] = None,
        /,
        set_tracer_provider: bool = True,
        span_processor_cls: Type[SpanProcessor] = BatchSpanProcessor,
        span_exporter_cls: Union[gRPCTraceExporter | HttpTraceExporter] = None,
    ):
        EZBase.__init__(self, exporter, resource, credentials)

        self.tracer_provider = TracerProvider(resource=self.resource)
        if set_tracer_provider:
            trace.set_tracer_provider(self.tracer_provider)
        self.tracer_provider.add_span_processor(
            span_processor_cls(
                span_exporter=self.exporter.get_span_exporter(
                    span_exporter_cls=span_exporter_cls
                )
            )
        )


class EZMetric(EZBase):
    meter_provider: MeterProvider

    def __init__(
        self,
        exporter: Exporter = None,
        resource: Resource | EZResource = None,
        credentials: Optional[ChannelCredentials] = None,
        /,
        metric_exporter_cls: Union[gRPCMetricExporter, HttpMetricExporter] = None,
        preferred_temporality: Dict[type, AggregationTemporality] = None,
        preferred_aggregation: Dict[type, Aggregation] = None,
        max_export_batch_size: Optional[int] = None,
        set_meter_provider: bool = True,
    ):
        EZBase.__init__(self, exporter, resource, credentials)
        metric_exporter = self.exporter.get_metric_exporter(
            metric_exporter_cls=metric_exporter_cls,
            preferred_temporality=preferred_temporality,
            preferred_aggregation=preferred_aggregation,
            max_export_batch_size=max_export_batch_size,
        )
        self.meter_provider = MeterProvider(
            resource=self.resource,
            metric_readers=[
                PeriodicExportingMetricReader(
                    exporter=metric_exporter,
                ),
            ],
            views=[],
        )
        if set_meter_provider:
            metrics.set_meter_provider(self.meter_provider)


class EZLog(EZBase):
    logger_provider: LoggerProvider

    def __init__(
        self,
        exporter: Exporter = None,
        resource: Resource | EZResource = None,
        credentials: Optional[ChannelCredentials] = None,
        /,
        log: str | List[str] = "logging",
        log_lever: int = logging.DEBUG,
        log_exporter_cls: gRPCLogExporter | HttpLogExporter = None,
        set_logger_provider: bool = True,
    ):
        EZBase.__init__(self, exporter, resource, credentials)

        # 配置日志跟踪
        self.logger_provider = LoggerProvider(resource=self.resource)
        if set_logger_provider:
            _logs.set_logger_provider(self.logger_provider)
        self.logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(
                exporter=self.exporter.get_log_export(log_exporter_cls=log_exporter_cls)
            )
        )
        if isinstance(log, str):
            log = [log]
        if "logging" in log:
            from opentelemetry.sdk._logs import LoggingHandler

            logging.getLogger().addHandler(
                LoggingHandler(level=log_lever, logger_provider=self.logger_provider)
            )
        if "structlog" in log:
            from ez_otlp.log.structlog_config import get_struct_logging_config

            config = get_struct_logging_config(
                log_lever=log_lever, logger_provider=self.logger_provider
            )
            config.configure()


class EZ_OTLP(EZLog, EZMetric, EZTracer, EZBase):
    def __init__(
        self,
        exporter: Exporter = None,
        resource: Resource | EZResource = None,
        credentials: Optional[ChannelCredentials] = None,
        /,
        set_tracer_provider: bool = True,
        span_processor_cls: Type[SpanProcessor] = BatchSpanProcessor,
        span_exporter_cls: Union[gRPCTraceExporter | HttpTraceExporter] = None,
        metric_exporter_cls: Union[gRPCMetricExporter, HttpMetricExporter] = None,
        preferred_temporality: Dict[type, AggregationTemporality] = None,
        preferred_aggregation: Dict[type, Aggregation] = None,
        max_export_batch_size: Optional[int] = None,
        set_meter_provider: bool = True,
        log: str | List[str] = "logging",
        log_lever: int = logging.DEBUG,
        log_exporter_cls: gRPCLogExporter | HttpLogExporter = None,
        set_logger_provider: bool = True,
    ):
        EZBase.__init__(self, exporter, resource, credentials)
        EZTracer.__init__(
            self,
            set_tracer_provider=set_tracer_provider,
            span_processor_cls=span_processor_cls,
            span_exporter_cls=span_exporter_cls,
        )

        EZMetric.__init__(
            self,
            metric_exporter_cls=metric_exporter_cls,
            preferred_temporality=preferred_temporality,
            preferred_aggregation=preferred_aggregation,
            max_export_batch_size=max_export_batch_size,
            set_meter_provider=set_meter_provider,
        )

        EZLog.__init__(
            self,
            log=log,
            log_lever=log_lever,
            log_exporter_cls=log_exporter_cls,
            set_logger_provider=set_logger_provider,
        )
