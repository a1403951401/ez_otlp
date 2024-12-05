# ez-otlp

> ez-otlp is a simple tool that enables convenient use of modern monitoring systems with minimal configuration. It helps developers streamline telemetry data collection and transmission, making it ideal for services in modern cloud-native applications and microservices architectures. It efficiently collects logs, metrics, and traces via OpenTelemetry and seamlessly integrates with existing monitoring tools and platforms like Prometheus, Grafana, Datadog, and more.

🚀 Quickly implement application performance monitoring, log management, distributed tracing, metrics and dashboards, and alerts.

🛠️ 99% of parameter configurations are resolved through environment variables, making it plug-and-play and ready to seamlessly integrate with OpenTelemetry without the need for complex parameters.

❤️ The demo uses SigNoz for an intuitive interface that showcases the power of modern monitoring systems.

### Documentation
<a href="https://github.com/a1403951401/ez_otlp/blob/main/README.md">English</a> &bull;
<a href="https://github.com/a1403951401/ez_otlp/blob/main/README.zh-cn.md">中文</a>

### Install
> pip install ez-otlp

### Usage Instructions
##### In your project
```python
# env
# EZ_ENDPOINT = http://host.docker.internal:4317/v1/traces
# EZ_RESOURCE_SERVICE_NAME = ez-otlp

from ez_otlp import EZ_OTLP

otlp = EZ_OTLP(log=["logging", "structlog"])
```
##### Run template.py
```bash
docker-compose up
```

#### locally hosted SigNoz
> http://localhost:3301/
```bash
cd signoz
docker-compose up -d
```

### Images
![img.png](docs/img.png)
![img.png](docs/img2.png)
![img.png](docs/img3.png)


### Todolist
 - logging module support -> loguru
 - Integration with other services -> Litestar, FastAPI, Starlette, Aiohttp, sqlalchemy, redis
 - Improve documentation
