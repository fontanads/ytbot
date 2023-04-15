from google.cloud import bigquery
import pandas as pd
from google.api_core.exceptions import NotFound
from src.helpers.logs import log_message


class BigQueryClient:

    def __init__(self, project_id):
        self.project_id = project_id
        self.client = bigquery.Client(project=self.project_id)

    def get_table_schema(self, dataset_id, table_id):
        dataset_ref = bigquery.DatasetReference(project=self.project_id, dataset_id=dataset_id)
        table_ref = bigquery.TableReference(dataset_ref=dataset_ref, table_id=table_id)
        return self.client.get_table(table_ref).schema

    @log_message(start_message="Uploading data to BigQuery...", end_message="Data uploaded successfully.")
    def upload_dataframe(self, dataset_id, table_id, df, overwrite_partition=True, delete_table=False, partition_field=None):
        dataset_ref = bigquery.DatasetReference(project=self.project_id, dataset_id=dataset_id)
        table_ref = bigquery.TableReference(dataset_ref=dataset_ref, table_id=table_id)
        table_schema = None
        # If the overwrite flag is set, delete the table
        if delete_table:
            self.client.delete_table(table_ref, not_found_ok=True)
        #  Check schema and overwrite partitions
        else:
            try:
                table = self.client.get_table(table_ref)
                table_schema = table.schema
                # Check if the dataframe columns match the table schema
                if list(df.columns) != [col.name for col in table_schema]:
                    raise ValueError('Dataframe columns do not match the table schema')

                if overwrite_partition:
                    self._delete_partition_data(table_ref, df, partition_field=partition_field)

            except NotFound:
                print("Table not found. If necessary, table will be created when writing data.")

        #  prepare data for upload

        if not table_schema:
            table_schema = self.generate_schema_from_dataframe(columns=df.columns, dtypes=df.dtypes)

        # Serialize datetime objects to ISO format
        # Convert the dataframe to a list of dictionaries
        df = self.covert_dataframe_timestamp_columns_to_isoformat(df)
        rows = df.to_dict('records')

        # Find the timestamp field to use for partitioning
        if partition_field:
            timestamp_field = partition_field
        else:
            timestamp_field = self.return_first_timestamp_field(table.schema)

        # truncate date to day
        timestamp_field = timestamp_field.replace(hour=0, minute=0, second=0, microsecond=0)

        # Insert the data into the table
        job_config = bigquery.LoadJobConfig(
            create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema=table_schema,
            time_partitioning=bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=timestamp_field,
            ) if timestamp_field else None
        )
        self.client.load_table_from_json(rows, destination=table_ref, job_config=job_config).result()

    def download_table(self, dataset_id, table_id, columns=None, query=None, limit=100):
        if query:
            table = self.client.query(query, project=self.project_id).to_dataframe()
        else:
            dataset_ref = bigquery.DatasetReference(project=self.project_id, dataset_id=dataset_id)
            table_ref = bigquery.TableReference(dataset_ref=dataset_ref, table_id=table_id)

            table_schema = self.client.get_table(table_ref).schema

            table = self.client.list_rows(
                table_ref,
                selected_fields=self.filter_columns_from_schema(columns, table_schema),
                max_results=limit)\
                .to_dataframe()
        return table

    def _delete_partition_data(self, table_ref, df, partition_field='dt'):
        partition_values = df[partition_field]\
            .apply(lambda x: x.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d'))\
            .unique().tolist()
        partition_values = [f"TIMESTAMP(\"{iso_trunc_date}\")" for iso_trunc_date in partition_values]
        delete_query = f"""
            DELETE FROM `{table_ref.project}.{table_ref.dataset_id}.{table_ref.table_id}`
            WHERE {partition_field} IN ({",".join(partition_values)})
        """
        query_job = self.client.query(delete_query)
        query_job.result()  # Waits for the query to complete.

    def _create_empty_table(self, table_ref, df_sample=None, partition_field=None):
        if df_sample is None:
            df_sample = pd.DataFrame()
        table = bigquery.Table(table_ref, schema=self.generate_schema_from_dataframe(columns=df_sample.columns, dtypes=df_sample.dtypes))
        if partition_field:
            timestamp_field = partition_field
        else:
            timestamp_field = self.return_first_timestamp_field(table.schema)
        if timestamp_field:
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=timestamp_field,
                expiration_ms=2592000000  # 30 days
            )
        return self.client.create_table(table=table, exists_ok=True)

    @staticmethod
    def generate_schema_from_dataframe(columns, dtypes):
        schema = []
        for column_name, dtype in zip(columns, dtypes):
            if 'datetime' in str(dtype):
                schema.append({'name': column_name, 'type': 'TIMESTAMP', 'mode': 'NULLABLE'})
            elif dtype == 'int64':
                schema.append({'name': column_name, 'type': 'INTEGER', 'mode': 'NULLABLE'})
            elif dtype == 'float64':
                schema.append({'name': column_name, 'type': 'FLOAT', 'mode': 'NULLABLE'})
            elif dtype == 'bool':
                schema.append({'name': column_name, 'type': 'BOOLEAN', 'mode': 'NULLABLE'})
            elif dtype == 'object' or 'string' in str(dtype):
                schema.append({'name': column_name, 'type': 'STRING', 'mode': 'NULLABLE'})
        return schema

    @staticmethod
    def column_names_to_schema_fields(column_names: list[str]) -> list[bigquery.SchemaField]:
        """Takes a list of strings and returns a list of BigQuery schema fields."""
        selected_fields = []
        for column_name in column_names:
            selected_fields.append(bigquery.SchemaField(column_name, 'STRING'))
        return selected_fields

    @staticmethod
    def filter_columns_from_schema(column_names, schema):
        return [field for field in schema if field.name in column_names]

    @staticmethod
    def return_first_timestamp_field(schema_fields):
        if not schema_fields:
            for field in schema_fields:
                if field.field_type == 'TIMESTAMP':
                    return field.name
        return None

    @staticmethod
    def covert_dataframe_timestamp_columns_to_isoformat(df):
        for column_name, dtype in zip(df.columns, df.dtypes):
            if 'datetime' in str(dtype):
                df[column_name] = df[column_name].apply(lambda x: x.isoformat())
                df[column_name] = df[column_name].astype("string")
        return df


if __name__ == '__main__':
    bq = BigQueryClient(project_id="sandbox-381517")
    print(bq.get_table_schema('youtube', 'trending_US'))
