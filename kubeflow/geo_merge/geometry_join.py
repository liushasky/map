import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.neighbors import KDTree, NearestNeighbors
from shapely.geometry.linestring import LineString
from shapely.geometry.multilinestring import MultiLineString


## Boardcast linestring geometry to lat & lon
def explode_geometry(x):
    if isinstance(x.geometry, LineString):
        coords = x.geometry.xy
        exp_data = np.zeros((len(coords[0]), 2))
        exp_data[:, 0] = coords[0]
        exp_data[:, 1] = coords[1]
        return exp_data
    elif isinstance(x.geometry, MultiLineString):
        exp_datas = []
        for line in x.geometry:
            coords = line.xy
            exp_data = np.zeros((len(coords[0]), 2))
            exp_data[:, 0] = coords[0]
            exp_data[:, 1] = coords[1]
            exp_datas.append(exp_data)
        return np.concatenate(exp_datas, axis=0)
    
## Create linestring from lat & lon
def createLineString(x):
    geometry_array = [[x.lon_org,x.lat_org],[x.lon, x.lat]]
    return LineString(geometry_array)

## Majority voting approach to determine the best attribute on a geometry
def majority_voting(x):
    try:
        return x.value_counts().index[0]
    except IndexError:
        return np.nan

def first_voting(x):
    return x.values[0]
    
class LineStringJoin(object):
    
    def __init__(self, n_neighbors=1, radius_neighbors=0.0004):
        self.n_neighbors = n_neighbors
        self.radius_neighbors = radius_neighbors
        self.knn = NearestNeighbors(n_neighbors=self.n_neighbors, algorithm='kd_tree', n_jobs=-1)

    def _preprocessing(self, standard_data, supplementary_data):
        ## Explode standard_data
        standard_data_cp = standard_data[~pd.isnull(standard_data['geometry'])]
        standard_data_cp['geo_linestring_id'] = range(0, standard_data_cp.shape[0])
        standard_data_cp['coords'] = standard_data_cp.apply(explode_geometry, axis=1)
        standard_data_cp['label'] = 'standard'
        standard_data_cp['geo_linestring_id'] = standard_data_cp['label']+'-'+standard_data_cp['geo_linestring_id'].astype(str)
        standard_data_exp = standard_data_cp.explode('coords')
        standard_data_exp[['lon','lat']] = standard_data_exp.coords.to_list()
        standard_data_exp['geo_point_id'] = range(0, standard_data_exp.shape[0])
        ## Explode supplementary_data
        supplementary_data_cp = supplementary_data[~pd.isnull(supplementary_data['geometry'])]
        supplementary_data_cp['geo_linestring_id'] = range(0, supplementary_data_cp.shape[0])
        supplementary_data_cp['coords'] = supplementary_data_cp.apply(explode_geometry, axis=1)
        supplementary_data_cp['label'] = 'supplementary'
        supplementary_data_cp['geo_linestring_id'] = supplementary_data_cp['label']+'-'+supplementary_data_cp['geo_linestring_id'].astype(str)
        supplementary_data_exp = supplementary_data_cp.explode('coords')
        supplementary_data_exp[['lon','lat']] = supplementary_data_exp.coords.to_list()
        supplementary_data_exp['geo_point_id'] = range(0, supplementary_data_exp.shape[0])
        ## Set Index
        standard_data_exp.reset_index(inplace=True)
        standard_data_exp.drop(['index'],axis=1,inplace=True)
        supplementary_data_exp.reset_index(inplace=True)
        supplementary_data_exp.drop(['index'],axis=1,inplace=True)
        return standard_data_exp, supplementary_data_exp
        
    def _fit(self, standard_data_exp, supplementary_data_exp):
        
        self.knn.fit(standard_data_exp[['lon','lat']])
        supplementary_data_exp['dist_match_point'], supplementary_data_exp['geo_point_id_match_point'] = self.knn.kneighbors(supplementary_data_exp[['lon','lat']], return_distance=True, n_neighbors=self.n_neighbors)
        supplementary_data_exp['geo_point_id_match_point'] = np.where(supplementary_data_exp['dist_match_point']>self.radius_neighbors, np.nan, supplementary_data_exp['geo_point_id_match_point'])
        supplementary_data_exp['dist_match_point'] = np.where(supplementary_data_exp['dist_match_point']>self.radius_neighbors, np.nan, supplementary_data_exp['dist_match_point'])
        return supplementary_data_exp
    
    
    def join(self, standard_data, supplementary_data, columns_mapper, on='geometry', how='outer'):
        standard_cols = standard_data.columns.values
        supplementary_cols = supplementary_data.columns.values
        ### Preprocess 
        standard_data_exp, supplementary_data_exp = self._preprocessing(standard_data, supplementary_data)
        ### Fit the model
        supplementary_data_exp = self._fit(standard_data_exp, supplementary_data_exp)
        
        standard_data_exp_join = standard_data_exp.merge(supplementary_data_exp, left_on='geo_point_id', right_on='geo_point_id_match_point', how=how, suffixes=['','_B'])
        standard_data_exp_join['point_matched'] = np.where(~pd.isnull(standard_data_exp_join['geo_point_id']) & ~pd.isnull(standard_data_exp_join['geo_point_id_B']), 1, 0)
        linestring_matched_B = standard_data_exp_join.groupby('geo_linestring_id_B')['point_matched'].apply(majority_voting).rename('linestring_matched_B').reset_index()
        standard_data_exp_join = standard_data_exp_join.merge(linestring_matched_B, on='geo_linestring_id_B', how='left')
        standard_data_exp_join['linestring_matched_B'].fillna(0, inplace=True)
        standard_data_exp_join = standard_data_exp_join[ ((standard_data_exp_join['linestring_matched_B']>0) & (standard_data_exp_join['point_matched']>0)) 
                                               | ((standard_data_exp_join['linestring_matched_B']<1) )]
        
        mapper = {
                    'geo_linestring_id': 'geo_linestring_id_B',
                    'label':'label_B'
                 }
        
        for k, v in mapper.items():
            standard_data_exp_join[k] = np.where(pd.isnull(standard_data_exp_join[k]) & ~pd.isnull(standard_data_exp_join[v]), 
                                                   standard_data_exp_join[v],standard_data_exp_join[k])
        
        for k, v in columns_mapper.items():
            if k == v:
                v = "{}_B".format(v)
            standard_data_exp_join[k] = np.where(pd.isnull(standard_data_exp_join[k]) & ~pd.isnull(standard_data_exp_join[v]), 
                                                   standard_data_exp_join[v],standard_data_exp_join[k])
        
        aggcols = set(standard_cols) | set(supplementary_cols) | set({'label'})
        for k, v in columns_mapper.items():
            if v in aggcols:
                aggcols.remove(v)
                aggcols.add(k)
        aggcols = list(aggcols)   
        print("Output will contain the following attributes: {}".format(aggcols))
        aggfuncs = {}
        for c in aggcols:
            if c == on:
                aggfuncs[c] = first_voting
            else:
                aggfuncs[c] = majority_voting
        standard_data_join = standard_data_exp_join.groupby('geo_linestring_id').agg(aggfuncs)
        standard_data_join['geometry'] = standard_data_join['geometry'].astype('geometry')
        standard_data_join.reset_index(inplace=True)
        standard_data_join = gpd.GeoDataFrame(standard_data_join, geometry='geometry')
        
        mr = float(100*supplementary_data_exp[~pd.isnull(supplementary_data_exp['geo_point_id_match_point'])].geo_linestring_id.nunique())/supplementary_data_exp.geo_linestring_id.nunique()
        print("Overlapp Rate: {}".format(mr))
        add_road = standard_data_join[standard_data_join['label']=='supplementary'].shape[0]
        print("Add {} geometries to Standard Data".format(add_road))
        
        return standard_data_join


class PointJoin(object):
    
    def __init__(self):
        raise NotImplementedError("This method is not implemented yet...")


class PolygonJoin(object):
    
    def __init__(self):
        raise NotImplementedError("This method is not implemented yet...")
