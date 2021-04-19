import os
import shutil
import zipfile
import argparse
from pathlib2 import Path
from utils import *
import geopandas as gpd
import osmnx as ox
import networkx as nx
import numpy as np

def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return Path(path).resolve(strict=False)

def extract(place, target, epsg_standard, force_clear=False):
    hti_graph = ox.graph_from_place(place, network_type='drive')
    edges = ox.graph_to_gdfs(hti_graph, nodes=False, edges=True)
    edges.reset_index(inplace=True)
    edges.drop(['u','v','key'],axis=1, inplace=True)
    for c in ['osmid','name','highway','oneway','length']:
        edges[c] = edges[c].map(lambda x: x[0] if type(x)==list else '')
    rawdata = edges[['osmid','name','geometry','highway','oneway','length']]
    rawdata.replace("",np.nan, inplace=True)
    newdata = reproject(rawdata, epsg_standard=epsg_standard)
    profile(newdata, target)
    newdata.to_file("{}/data.shp".format(target), index=False)    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='data extraction from OSMNX')
    parser.add_argument('-b', '--base_path',
                        help='directory to base data', default='../../data')
    parser.add_argument(
        '-p', '--place', help='place name to extract from OSM Data', default='Haiti')  # noqa: E501
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
    check_dir(target_file)

    print('Acquiring shapefile...')
    extract(str(args.place), target_file, args.epsg)
    
    print('writing dataset to {}'.format(target_file))
