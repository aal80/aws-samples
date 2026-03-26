import boto3
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from mypy_boto3_s3vectors import S3VectorsClient
import json
import logging
logging.basicConfig(
    level=logging.INFO, 
    format="[%(levelname)s] %(filename)s:%(lineno)d:%(funcName)s - %(message)s"
)
l = logging.getLogger(__name__)

bedrock: BedrockRuntimeClient = boto3.client("bedrock-runtime")
s3vectors: S3VectorsClient = boto3.client("s3vectors")

bucket_name = open("./../tmp/bucket_name.txt").read().strip()
index_name = open("./../tmp/index_name.txt").read().strip()

l.info(f"bucket_name={bucket_name}")
l.info(f"index_name={index_name}")

def query(query_text: str):
    l.info(f"Generating embedding for query_text={query_text}")
    input_text = json.dumps({"inputText": query_text})
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0", body=input_text
    )

    response_code = response["ResponseMetadata"]["HTTPStatusCode"]
    response_body = response["body"].read()
    response_json = json.loads(response_body)
    embedding = response_json["embedding"]
    l.info(f"HTTP={response_code} embedding_size={len(embedding)}")

    l.info(f"Querying vector index...")
    response = s3vectors.query_vectors(
        vectorBucketName=bucket_name,
        indexName=index_name,
        queryVector={"float32": embedding},
        topK=10,
        # filter={"genre": "scifi"},  # optional
        returnDistance=True,
        returnMetadata=True,
    )


    vectors = response["vectors"]
    l.info(f"Retrieved {len(vectors)} results")

    sources = []
    for vector in vectors:
        sources.append(vector["metadata"]["source_text"])

    # l.info(sources)
    return sources

if __name__ == "__main__":
    l.info("> main")
    query("star wars")