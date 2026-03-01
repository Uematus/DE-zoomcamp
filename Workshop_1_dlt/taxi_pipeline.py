import dlt
from dlt.sources.rest_api import rest_api_source
from dlt.sources.rest_api.config_setup import PageNumberPaginator

def get_taxi_source():
    return rest_api_source(
        {
            "client": {
                "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api",
            },
            "resources": [
                {
                    "name": "taxi_data",
                    "endpoint": {
                        "path": "/",
                        "params": {
                            "page_size": 1000
                        },
                        "paginator": PageNumberPaginator(
                            page_param="page",
                            base_page=1,
                            stop_after_empty_page=True,
                            total_path=None,
                        ),
                    },
                }
            ],
        }
    )

pipeline = dlt.pipeline(
    pipeline_name="taxi_pipeline",
    destination="duckdb",
    refresh="drop_sources",
    progress="log",
)

if __name__ == "__main__":
    load_info = pipeline.run(get_taxi_source())
    print(load_info)