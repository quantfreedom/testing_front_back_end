import os
from aws_cdk import Stack, RemovalPolicy
from constructs import Construct
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess, BucketEncryption, ObjectOwnership
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
from aws_cdk.aws_route53 import HostedZone, ARecord, RecordTarget
from aws_cdk.aws_route53_targets import CloudFrontTarget
from aws_cdk.aws_certificatemanager import DnsValidatedCertificate, Certificate
from aws_cdk.aws_iam import PolicyStatement, CanonicalUserPrincipal
from aws_cdk.aws_cloudfront import (
    OriginAccessIdentity,
    ViewerProtocolPolicy,
    SecurityPolicyProtocol,
    CloudFrontWebDistribution,
    ViewerCertificate,
    SSLMethod,
    SourceConfiguration,
    S3OriginConfig,
    CfnDistribution,
    Behavior,
    CloudFrontAllowedMethods,
)


class WWWTest(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        zone_domain_name = "quantfreedom.com"
        sub_domain = "www.test.quantfreedom.com"

        allow_public_access = BlockPublicAccess(
            block_public_acls=False,
            ignore_public_acls=False,
            block_public_policy=False,
            restrict_public_buckets=False,
        )

        s3_bucket_src = Bucket(
            scope=self,
            id="www-test-quantfreedom",
            bucket_name="www.test.quantfreedom.com",
            public_read_access=True,
            block_public_access=allow_public_access,
            encryption=BucketEncryption.S3_MANAGED,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            object_ownership=ObjectOwnership.BUCKET_OWNER_PREFERRED,
            website_error_document="error.html",
            website_index_document="index.html",
        )

        source_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../..",
                "frontend/dist/frontend/browser",
            )
        )
        
        BucketDeployment(
            scope=self,
            id="www-test-deploy",
            sources=[Source.asset(source_path)],
            destination_bucket=s3_bucket_src,
        )

        hosted_zone = HostedZone.from_lookup(
            scope=self,
            id="www-test-zone",
            domain_name=zone_domain_name,
        )

        certificate_arn = DnsValidatedCertificate(
            scope=self,
            id="www-test-cert",
            domain_name=sub_domain,
            hosted_zone=hosted_zone,
            region="us-east-1",
        ).certificate_arn

        identity = OriginAccessIdentity(
            scope=self,
            id="www-test-origin-access-identity",
            comment="Connects CF with S3",
        )

        principal = CanonicalUserPrincipal(
            canonical_user_id=identity.cloud_front_origin_access_identity_s3_canonical_user_id,
        )

        policy = PolicyStatement(
            actions=["s3:GetObject"],
            resources=[f"{s3_bucket_src.bucket_arn}/*"],
            principals=[principal],
        )

        s3_bucket_src.add_to_resource_policy(permission=policy)

        behavior = Behavior(
            allowed_methods=CloudFrontAllowedMethods.GET_HEAD,
            viewer_protocol_policy=ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            compress=True,
            is_default_behavior=True,
        )

        certificate = Certificate.from_certificate_arn(
            scope=self,
            id="www-test-certificate",
            certificate_arn=certificate_arn,
        )

        viewer_certificate = ViewerCertificate.from_acm_certificate(
            certificate=certificate,
            aliases=[sub_domain],
            security_policy=SecurityPolicyProtocol.TLS_V1_2_2021,
            ssl_method=SSLMethod.SNI,
        )

        s3_orgin_config = S3OriginConfig(
            s3_bucket_source=s3_bucket_src,
            origin_access_identity=identity,
        )

        source_config = SourceConfiguration(
            s3_origin_source=s3_orgin_config,
            behaviors=[behavior],
        )

        error_response = CfnDistribution.CustomErrorResponseProperty(
            error_code=404,
            error_caching_min_ttl=0,
            response_code=200,
            response_page_path="/error.html",
        )

        distribution = CloudFrontWebDistribution(
            scope=self,
            id="www-test-distribution",
            origin_configs=[source_config],
            viewer_certificate=viewer_certificate,
            default_root_object="index.html",
            error_configurations=[error_response],
        )

        cloudfront_target = CloudFrontTarget(distribution)
        the_target = RecordTarget.from_alias(alias_target=cloudfront_target)

        ARecord(
            scope=self,
            id="www-test-record",
            record_name=sub_domain,
            zone=hosted_zone,
            target=the_target,
        )
