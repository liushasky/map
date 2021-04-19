import os
import shutil
import zipfile
import argparse
from pathlib2 import Path
from geometry_join import LineStringJoin
import geopandas as gpd

def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return Path(path).resolve(strict=False)

def merge(source, target, columns_mapper, n_neighbors, radius_neighbors):
    sourcedata = gpd.read_file(source)
    targetdata = gpd.read_file(target)
    GJ = LineStringJoin(n_neighbors=n_neighbors, radius_neighbors=radius_neighbors)
    data_join = GJ.join(targetdata, sourcedata, columns_mapper)
    return data_join
    
def write_to(data_join, join_file):
    data_join.to_file(join_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='data download')
    parser.add_argument('-b', '--base_path',
                        help='directory to base data', default='../../data')
    parser.add_argument(
        '-s', '--source', help='source shapefiles', default='supplementary_data')  # noqa: E501
    parser.add_argument(
        '-t', '--target', help='target file to receive attribute from source data ', default='standard_data')  # noqa: E501
    parser.add_argument(
        '-m', '--merged', help='output file name to store the merged data', default='merged_data')  # noqa: E501
    parser.add_argument(
        '-n', '--n_neighbors', help='Number of Neighbors to consider when mergeing geo-points', default=1, type=int)  # noqa: E501
    parser.add_argument(
        '-r', '--radius_neighbors', help='Maxmium Radius between Neighbors to consider when mergeing geo-points', default=0.0004, type=float)  # noqa: E501
    parser.add_argument('-f', '--force',
                        help='force clear all data', default=False, action='store_true')  # noqa: E501
    args = parser.parse_args()
    print(args)
    base_path = Path(args.base_path).resolve(strict=False)
    print('Base Path:  {}'.format(base_path))
    target_file = Path(base_path).resolve(strict=False).joinpath(args.target)
    print('Target File: {}'.format(target_file))
    source_file = Path(base_path).resolve(strict=False).joinpath(args.source)
    print('Source File: {}'.format(source_file))
    merged_file = Path(base_path).resolve(strict=False).joinpath(args.merged)
    print('Merged File: {}'.format(merged_file))
    check_dir(merged_file)

    print('Acquiring shapefile...')
    print('Perform merging on the following attributes: (Targe attribute <-: Source attribute)...')
    columns_mapper = {
        'geometry':'geometry',
        'name':'nom_sec',
        'osmid':'cod_tronc',
    }
    print(columns_mapper)
    
    print('Merge shapefile...')
    data_join = merge(os.path.join(source_file,'data.shp'), os.path.join(target_file,'data.shp'), columns_mapper, int(args.n_neighbors), float(args.radius_neighbors))
    
    print('Writing dataset to {}'.format(merged_file))
    write_to(data_join, os.path.join(merged_file,'data.shp'))
