from aws_cdk import (
    Stack,
    CfnOutput,
    aws_s3 as s3,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as cloudfront_origins,
    aws_route53_targets as targets,
    aws_s3_deployment as s3deploy
)

import aws_cdk as core
from constructs import Construct
from . import parameters
class HostAppAwsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        s3_block_public_access = s3.BlockPublicAccess(
            block_public_acls=False,
            ignore_public_acls=False,
            block_public_policy=False,
            restrict_public_buckets=False
        )
        
        s3_bucket_src = s3.Bucket(self, "s3_bucket_src",
            bucket_name = "hex.netsolcloudservices.com", ## cloudexpert.com
            public_read_access=True,
            block_public_access=s3_block_public_access,
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            removal_policy=core.RemovalPolicy.DESTROY,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
            website_error_document="error.html",
            website_index_document="index.html"
        )

        s3_bucket_redirect = s3.Bucket(self, "s3_bucket_redirect",
            bucket_name = "xeh.netsolcloudservices.com", #dev.cloudexpert.com
            public_read_access=True,
            block_public_access=s3_block_public_access,
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            removal_policy=core.RemovalPolicy.DESTROY,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
            website_redirect=s3.RedirectTarget(
                host_name=s3_bucket_src.bucket_website_domain_name,
                protocol=s3.RedirectProtocol.HTTPS
            )
        )
    
        hosted_zone = route53.HostedZone.from_lookup(self, "MyZone",
            domain_name="netsolcloudservices.com" #cloudexpert.com
        )

        certificate_dns_validation = acm.DnsValidatedCertificate(self, "Certificate",
            domain_name="hex.netsolcloudservices.com", #cloudexpert.com
            hosted_zone=hosted_zone,
            region="us-east-1"
        )

        certificate_dns_validation_redirect = acm.DnsValidatedCertificate(self, "Redirect_Certificate",
            domain_name="xeh.netsolcloudservices.com", #*.cloudexpert.com
            hosted_zone=hosted_zone,
            region="us-east-1"
        )

        distribution = cloudfront.Distribution(self, "cloudFrontDistribution",
            certificate=certificate_dns_validation,
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            enable_logging=True,
            default_behavior=cloudfront.BehaviorOptions(
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                origin=cloudfront_origins.S3Origin(s3_bucket_src),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            domain_names=["hex.netsolcloudservices.com"], #cloudexpert.com
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_page_path="/index.html",
                    ttl=core.Duration.seconds(amount=0),
                    response_http_status=200,
                )
            ],
        )
        
        route53record = route53.ARecord(self, "a-record", 
            record_name = "hex", ## Remove this line 
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(distribution))
        )

        redirect_distribution = cloudfront.Distribution(self, "redirect_cloudFrontDistribution",
            certificate=certificate_dns_validation_redirect,
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            enable_logging=True,
            default_behavior=cloudfront.BehaviorOptions(
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                origin=cloudfront_origins.S3Origin(s3_bucket_src),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            domain_names=["xeh.netsolcloudservices.com"], #dev.cloudexpert.com
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_page_path="/index.html",
                    ttl=core.Duration.seconds(amount=0),
                    response_http_status=200,
                )
            ],
        )
        
        redirect_route53record = route53.ARecord(self, "redirect-a-record", 
            record_name = "xeh", #dev
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(redirect_distribution))
        )

        oai = cloudfront.OriginAccessIdentity(self, "OAI", 
            comment="Connects CF with S3"
        )
        s3_bucket_src.grant_read(oai)
        s3_bucket_src.grant_read_write(oai)

        redirect_oai = cloudfront.OriginAccessIdentity(self, "redirect-OAI", 
            comment="Connects CF with S3"
        )
        s3_bucket_src.grant_read(redirect_oai)
        s3_bucket_src.grant_read_write(redirect_oai)

        # s3_deploy = s3deploy.BucketDeployment(self, "deployWebsite",
        #     sources=[s3deploy.Source.asset("./host_app_aws/website/")],
        #     destination_bucket=s3_bucket_src
        # )

        CfnOutput(self, "s3BucketName",
            value=s3_bucket_src.bucket_name,
            export_name="s3BucketName")
        CfnOutput(self, "s3BucketArn",
            value=s3_bucket_src.bucket_arn,
            export_name="s3BucketArn")
        CfnOutput(self, "s3BucketDomainName",
            value=s3_bucket_src.bucket_domain_name,
            export_name="s3BucketDomainName")
        CfnOutput(self, "s3BucketWebsiteDomainName",
            value=s3_bucket_src.bucket_website_domain_name,
            export_name="s3BucketWebsiteDomainName")
        CfnOutput(self, "s3BucketWebsiteUrl",
            value=s3_bucket_src.bucket_website_url,
            export_name="s3BucketWebsiteUrl")