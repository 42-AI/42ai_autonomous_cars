
from get_data.src import s3_utils
from get_data.src import es_utils
from get_data.cluster_param import ES_INDEX, ES_HOST_PORT, ES_HOST_IP


def delete_picture(picture_id, bucket_path):
    s3 = s3_utils.get_s3_resource()
    bucket, key_prefix, file_name = s3_utils.split_s3_path(bucket_path)
    s3_utils.delete_object_s3(s3, bucket, key_prefix, [picture_id])
    print(f'Picture "{picture_id}" successfully removed from s3 ({bucket_path})')
    es_utils.delete_document(ES_INDEX, picture_id, host_ip=ES_HOST_IP, port=ES_HOST_PORT)
    print(f'Picture "{picture_id}" successfully removed from ES')
