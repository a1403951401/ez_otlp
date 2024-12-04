import inspect

from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from pydantic import create_model
from pydantic_settings import BaseSettings

ResourceAttributesModel = create_model(
    "ResourceAttributesModel",
    **{
        name: (str | None, None)
        for name, value in inspect.getmembers(
            ResourceAttributes, predicate=lambda obj: isinstance(obj, str)
        )
        if name not in ["SCHEMA_URL", "__module__"]
    },
)


class EZResource(ResourceAttributesModel, BaseSettings):
    """
    Construct Resource using `env`

        for example `SERVICE_NAME(service.name)`
        EZ_RESOURCE_SERVICE_NAME=ez-otlp
    """

    schema_url: str | None = None

    class Config:
        env_prefix = "EZ_RESOURCE_"
        case_sensitive = False

    def get_resource(self) -> Resource:
        return Resource.create(
            {
                getattr(ResourceAttributes, k): v
                for k, v in self.model_dump(exclude_none=True).items()
            },
            self.schema_url,
        )


ez_resource = EZResource()
default_resource: Resource = ez_resource.get_resource()

if __name__ == "__main__":
    print(ez_resource.model_dump(exclude_none=True))
    print(default_resource.to_json())
