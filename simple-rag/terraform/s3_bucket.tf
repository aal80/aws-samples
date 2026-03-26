resource "aws_s3vectors_vector_bucket" "this" {
  vector_bucket_name = "${local.project_name}"
  force_destroy = true
}

resource "aws_s3vectors_index" "this" {
    index_name = "index1"
    vector_bucket_name = aws_s3vectors_vector_bucket.this.vector_bucket_name

    data_type = "float32"
    dimension = 1024
    distance_metric = "cosine"

    metadata_configuration {
      non_filterable_metadata_keys = ["source_text"]
    }
}

resource "local_file" "s3_bucket_name" {
  content         = aws_s3vectors_vector_bucket.this.vector_bucket_name
  filename        = "${path.module}/../tmp/bucket_name.txt"
}

resource "local_file" "s3_index_name" {
  content         = aws_s3vectors_index.this.index_name
  filename        = "${path.module}/../tmp/index_name.txt"
}