import os
import aws_cdk as cdk
from aws_cdk import Stack, Duration, CfnOutput
from aws_cdk.aws_lambda import (
    DockerImageFunction,
    DockerImageCode,
    Architecture,
    FunctionUrlAuthType,
)
from constructs import Construct


class TestingLambda(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../..",
                "backend",
            )
        )
        
        docker_func = DockerImageFunction(
            scope=self,
            id="DockerTestingLambda",
            code=DockerImageCode.from_image_asset(
                directory=source_path,
                cache_disabled=True,
                asset_name="testing_lambda",
            ),
            description="Testing lambda stuff",
            function_name="testing_lambda",
            memory_size=3000,
            timeout=Duration.minutes(5),
            architecture=Architecture.X86_64,
        )

        function_url = docker_func.add_function_url(
            auth_type=FunctionUrlAuthType.NONE,
        )

        CfnOutput(
            scope=self,
            id="FunctionUrl",
            value=function_url.url,
            description="The URL of the function",
        )


app = cdk.App()

TestingLambda(app, "testing-lambda")

app.synth()
