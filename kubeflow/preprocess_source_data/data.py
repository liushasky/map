import os
import shutil
import zipfile
import argparse
from pathlib2 import Path
import wget
from utils import *
import geopandas as gpd

def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return Path(path).resolve(strict=False)


def download(source, target, force_clear=False):
    if force_clear and os.path.exists(target):
        print('Removing {}...'.format(target))
        shutil.rmtree(target)

    check_dir(target)

    targt_file = str(Path(target).joinpath('data.zip'))
    if os.path.exists(targt_file) and not force_clear:
        print('data already exists, skipping download')
        return

    if source.startswith('http'):
        print("Downloading from {} to {}".format(source, target))
        wget.download(source, targt_file)
        print("Done!")
    else:
        print("Copying from {} to {}".format(source, target))
        shutil.copyfile(source, targt_file)
        

def reproject_data(source, target, epsg_standard=4326):
    rawdata = gpd.read_file(source)
    newdata = reproject(rawdata, epsg_standard=epsg_standard)
    profile(newdata, target)
    newdata.to_file("{}/data.shp".format(target), index=False)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='data download')
    parser.add_argument('-b', '--base_path',
                        help='directory to base data', default='../../data')
    parser.add_argument(
        '-s', '--source', help='source shapefiles URL', default='https://data.humdata.org/dataset/3b39f85b-12cf-49cd-aa00-ee3ac04ce61f/resource/9cf4a82d-6292-44b1-aa3f-1f9666322081/download/hti_polbndl_rd_cnigs.zip')  # noqa: E501
    parser.add_argument(
        '-t', '--target', help='target file to hold preprocessed shapefiles', default='standard_data')  # noqa: E501
    parser.add_argument(
        '-i', '--epsg', help='target EPSG standard to reproject', default=4326, type=int)  # noqa: E501
    parser.add_argument('-f', '--force',
                        help='force clear all data', default=False, action='store_true')  # noqa: E501
    args = parser.parse_args()
    print(args)

    base_path = Path(args.base_path).resolve(strict=False)
    print('Base Path:  {}'.format(base_path))
    target_file = Path(base_path).resolve(strict=False).joinpath(args.target)
    print('Input File: {}'.format(target_file))
    source_file = args.source
    check_dir(target_file)

    print('Acquiring shapefile...')
    download(str(source_file),
             str(base_path), args.force)
    
    print('Reproject shapefile...')
    reproject_data("{}/data.zip!hti_polbndl_rd_CNIGS".format(base_path), target_file, epsg_standard=args.epsg)
    
    print('writing dataset to {}'.format(target_file))
