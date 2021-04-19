######## Utilities #########
import geopandas as gpd
import pandas as pd
import numpy as np
    
## Reprojecting a shapefile
def reproject(geodf, epsg_standard=4326):
    geodf = geodf[~pd.isnull(geodf['geometry'])]
    print("Original projection : {}".format(geodf.crs))
    geodf = geodf.to_crs(epsg=epsg_standard)
    print("New projection: {}".format(geodf.crs))
    return geodf

## Simple Profiling
def profile(geodf, name):
    geodf[geodf==''] = np.nan
    print("{} contains {} records and {} attributes".format(name, geodf.shape[0], geodf.shape[1]))
    completeness = 1-geodf.isna().sum()/geodf.shape[0]
    print("Completeness by Attribute: {}".format(completeness))
    overall_completeness = completeness.mean()
    print("Overall Completeness {}".format(overall_completeness))
    
