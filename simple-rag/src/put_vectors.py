import boto3
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from mypy_boto3_s3vectors import S3VectorsClient
import json

bedrock: BedrockRuntimeClient = boto3.client("bedrock-runtime")
s3vectors: S3VectorsClient = boto3.client("s3vectors")

bucket_name = open("./../tmp/bucket_name.txt").read().strip()
index_name = open("./../tmp/index_name.txt").read().strip()

print(f"bucket_name={bucket_name}")
print(f"index_name={index_name}")

source_texts = {
    "Star Wars": "Star Wars: A farm boy joins rebels to fight an evil empire in space",
    "Jurassic Park": "Jurassic Park: Scientists create dinosaurs in a theme park that goes wrong",
    "Finding Nemo": "Finding Nemo: A father fish searches the ocean to find his lost son",
}

embeddings = []
vectors = []

for title, description in source_texts.items():
    input_text_body = json.dumps({"inputText": description})
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0", body=input_text_body
    )

    response_code = response["ResponseMetadata"]["HTTPStatusCode"]
    response_body = response["body"].read()
    response_json = json.loads(response_body)
    embedding = response_json["embedding"]
    embeddings.append(embedding)
    print(f"HTTP={response_code} title='{title}' embedding_size={len(embedding)}")

    vectors.append(
        {
            "key": title,
            "data": {"float32": embedding},
            "metadata": {"source_text": description, "genre": "scifi"},
        }
    )

print(f"injecting {len(vectors)} vectors into S3....")

s3vectors.put_vectors(
    vectorBucketName=bucket_name,
    indexName=index_name,
    vectors=vectors
)

print("All done!")