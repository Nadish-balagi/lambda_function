import json
import boto3
import pandas as pd
from sqlalchemy import create_engine
import os

# ✅ Initialize S3 client
s3 = boto3.client('s3')

def col_rename_change_data(column: str) -> str:
    """Convert column names to lowercase and replace unwanted symbols"""
    column = column.lower()
    for symbol in ['.', '/', ')']:
        column = column.replace(symbol, '')
    for symbol in ['(', ' ', '-']:
        column = column.replace(symbol, '_')
    return column

def lambda_handler(event, context):
    try:
        # ✅ Extract bucket and key from the S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        local_file = '/tmp/' + key.split('/')[-1]

        print(f"📥 Downloading: s3://{bucket}/{key} → {local_file}")
        s3.download_file(bucket, key, local_file)

        # ✅ Read CSV with encoding fallback
        try:
            df = pd.read_csv(local_file, encoding='latin1')
        except UnicodeDecodeError:
            try:
                print("⚠ Unicode error, retrying with ISO-8859-1...")
                df = pd.read_csv(local_file, encoding='ISO-8859-1')
            except UnicodeDecodeError:
                print("⚠ Still failing, ignoring bad characters...")
                df = pd.read_csv(local_file, encoding='latin1', encoding_errors='ignore')

        # ✅ Clean column names
        df.rename(columns=lambda col: col_rename_change_data(col), inplace=True)
        print(f"✅ Cleaned columns: {df.columns.tolist()}")

        # ✅ Database connection details from Lambda environment variables
        db_user = os.environ['PG_USER']
        db_password = os.environ['PG_PASSWORD']
        db_host = os.environ['PG_HOST']
        db_port = os.environ['PG_PORT']
        db_name = os.environ['PG_DATABASE']
        table_name = os.environ['PG_TABLE']

        engine_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(engine_url)

        # ✅ Insert into PostgreSQL
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"✅ Uploaded {len(df)} rows to {table_name}")

        return {
            "statusCode": 200,
            "body": json.dumps(f"Successfully processed {key} and inserted into {table_name}")
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps(str(e))
        }
