"""Main pipeline file"""
from kubernetes import client as k8s_client
import kfp.dsl as dsl
import kfp.compiler as compiler

@dsl.pipeline(
  name='GeoMerger',
  description='Geospatial Data Merging'
)

def geo_merger_pipeline(
    standard_data='osm',
    source_data='https://data.humdata.org/dataset/3b39f85b-12cf-49cd-aa00-ee3ac04ce61f/resource/9cf4a82d-6292-44b1-aa3f-1f9666322081/download/hti_polbndl_rd_cnigs.zip',
    epsg=4326,
    radius_neighbors=0.0004,
    n_neighbors=1,
    ingest_to='azure-data-lake'
):
    """Pipeline steps"""
    
    operations = {}
    persistent_volume_path = '/mnt/azure'
    epsg = 4326
    source_dataset = 'supplementary_data'
    target_dataset = 'standard_data'
    merged_dataset = 'merged_data'
    
    # preprocess data
    data_download = 'https://data.humdata.org/dataset/3b39f85b-12cf-49cd-aa00-ee3ac04ce61f/resource/9cf4a82d-6292-44b1-aa3f-1f9666322081/download/hti_polbndl_rd_cnigs.zip'
    operations['preprocess_source_data'] = dsl.ContainerOp(
        name='Download and Clean Source Data',
        image='pitcrewacr.azurecr.io/kubeflow/nga-demo-pipeline/preprocessing:latest',
        command=['python'],
        arguments=[
          '/scripts/data.py',
          '--base_path', persistent_volume_path,
          '--source', data_download,
          '--target', source_dataset,
          '--epsg', epsg,
        ]
      )
    
    # preprocess data
    place = 'Haiti'
    operations['extract_target_data'] = dsl.ContainerOp(
        name='Extract Target Data',
        image='pitcrewacr.azurecr.io/kubeflow/nga-demo-pipeline/extracting:latest',
        command=['python'],
        arguments=[
          '/scripts/data.py',
          '--base_path', persistent_volume_path,
          '--place', place,
          '--target', target_dataset,
          '--epsg', epsg,
        ]
      )
      
    # merging data
    radius_neighbors = 0.0004
    n_neighbors = 1
    operations['merge'] = dsl.ContainerOp(
        name='K-Nearest Neighbors Merge',
        image='pitcrewacr.azurecr.io/kubeflow/nga-demo-pipeline/merging:latest',
        command=['python'],
        arguments=[
          '/scripts/merge.py',
          '--base_path', persistent_volume_path,
          '--source', source_dataset,
          '--target', target_dataset,
          '--merged', merged_dataset,
          '--n_neighbors', n_neighbors,
          '--radius_neighbors',radius_neighbors,
        ]
      )
    operations['merge'].after(operations['preprocess_source_data'],operations['extract_target_data'])
    
    # ingesting data
    data_lake_path = "pitcrewstorage/bc-data-mart/shapefiles/merged_data.zip"
    provider = 'azure'
    key = 'hB8d+muYJy4yUey6P4fWLEhi/iexF20seH2AIWGbw0jNq89amrbyAfYegTuTWWlXKVVGEqWpFysQJfpuOHsJbA=='
    operations['ingest'] = dsl.ContainerOp(
        name='Ingest Shapefile to Data Lake',
        image='pitcrewacr.azurecr.io/kubeflow/nga-demo-pipeline/ingesting:latest',
        command=['python'],
        arguments=[
          '/scripts/data.py',
          '--base_path', persistent_volume_path,
          '--source', merged_dataset,
          '--target', data_lake_path,
          '--provider', provider,
          '--key',key,
        ]
      )
    operations['ingest'].after(operations['merge'])
    
    for _, op_1 in operations.items():
        op_1.container.set_image_pull_policy("Always")
        op_1.add_volume(
          k8s_client.V1Volume(
            name='v-nga-demo-pipeline',
            persistent_volume_claim=k8s_client.V1PersistentVolumeClaimVolumeSource(
              claim_name='pvc-nga-demo-pipeline')
          )
        ).add_volume_mount(k8s_client.V1VolumeMount(
          mount_path='/mnt/azure', name='v-nga-demo-pipeline'))

if __name__ == '__main__':
    pipeline_conf = dsl.PipelineConf()
    pipeline_conf.set_default_pod_node_selector('dedicate.pool','pipelinepool')
    compiler.Compiler().compile(pipeline_func=geo_merger_pipeline, package_path=__file__ + '.tar.gz',pipeline_conf=pipeline_conf)
