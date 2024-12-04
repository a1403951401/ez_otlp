if __name__ == "__main__":
    import time
    from opentelemetry import trace
    import logging
    import structlog

    from ez_otlp import EZ_OTLP

    otlp = EZ_OTLP(log=["logging", "structlog"])
    print(otlp.exporter.model_dump())
    print(otlp.resource.to_json())

    logging.getLogger().addHandler(logging.StreamHandler())
    logging_logger = logging.getLogger("otlp.logging")

    structlog_logger = structlog.get_logger("otlp.structlog")

    tracer = trace.get_tracer(__name__)
    for index in range(60):
        with tracer.start_as_current_span(f"tracer {index}"):
            logging_logger.error("Hello from OpenTelemetry! (logging)")
            structlog_logger.error("Hello from OpenTelemetry! (structlog)", index=index)
        time.sleep(0.5)
