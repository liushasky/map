import os, uuid, sys
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core._match_conditions import MatchConditions
from azure.storage.filedatalake._models import ContentSettings
import shutil
import zipfile
import argparse
from pathlib2 import Path

def compress(source_file):
    shutil.make_archive(source_file, 'zip', source_file)

def ingest(storage_account_name, storage_account_key, file_system, file_path, file_name, source_file):
    service_client = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format(
            "https", storage_account_name), credential=storage_account_key)
    file_system_client = service_client.get_file_system_client(file_system=file_system)
    directory_client = file_system_client.get_directory_client(file_path)
    file_client = directory_client.get_file_client(file_name)
    local_file = open(source_file,'r',encoding='ISO8859-1')
    file_contents = local_file.read()
    file_client.upload_data(file_contents, overwrite=True)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='data ingestion')
    parser.add_argument('-b', '--base_path',
                        help='directory to base data', default='../../data')
    parser.add_argument(
        '-s', '--source', help='source shapefiles', default='merged_data')  # noqa: E501
    parser.add_argument(
        '-t', '--target', help='target ingestion location ', default='pitcrewstorage/bc-data-mart/shapefiles/merged_data.zip')  # noqa: E501
    parser.add_argument(
        '-p', '--provider', help='storage provider', default='azure')  # noqa: E501
    parser.add_argument(
        '-k', '--key', help='storage account secret', default='')  # noqa: E501
    parser.add_argument('-f', '--force',
                        help='force clear all data', default=False, action='store_true')  # noqa: E501
    args = parser.parse_args()
    print(args)
    base_path = Path(args.base_path).resolve(strict=False)
    print('Base Path:  {}'.format(base_path))
    source_file = Path(base_path).resolve(strict=False).joinpath(args.source)
    print('Source File: {}'.format(source_file))
    
    print('Acquiring & Compress shapefile...')
    compress(source_file)
    
    storage_account_name = args.target.split("/")[0]
    file_system = args.target.split("/")[1]
    file_path = "/".join(args.target.split("/")[2:-1])
    file_name = args.target.split("/")[-1]
    ingest(storage_account_name, str(args.key), file_system, file_path, file_name, "{}.zip".format(source_file))
    print('Writing shapefile to {}://{}.dfs.core.windows.net/{}/{}/{}'.format(
            "https", storage_account_name,file_system, file_path, file_name))
    
