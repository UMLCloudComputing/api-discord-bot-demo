from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    Duration,
    aws_dynamodb as dynamodb,
)
from constructs import Construct
import os

from dotenv import load_dotenv
load_dotenv()

class CdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        dockerFunc = _lambda.DockerImageFunction(
            scope=self,
            id=f"Lambda-{construct_id}",
            function_name=construct_id,
            environment= {
                "DISCORD_PUBLIC_KEY" : os.getenv('DISCORD_PUBLIC_KEY'),
                "DISCORD_ID" : os.getenv('DISCORD_ID'),
            },            
            code=_lambda.DockerImageCode.from_image_asset(
                directory="src"
            ),
            timeout=Duration.seconds(300),
            memory_size=256,
        )

        api = apigateway.LambdaRestApi(self, f"API-{construct_id}",
            handler=dockerFunc,
            proxy=True,
        )