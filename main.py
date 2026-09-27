import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus #to encode the special character in password
import logging
from dotenv import load_dotenv
import os
load_dotenv()
import argparse

db_password = os.getenv("DB_PASSWORD")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def extract(filepath):
    try:
        df = pd.read_csv(filepath)
        logging.info(f"Extracted {len(df)} rows from {filepath}")
        return df
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        raise
        

def transform(df):
    try:
    # drop the missing values
        df.dropna(how = 'all',inplace = True) 

    # find and remove duplicates
        # df1 = df[df.duplicated()]
        df.drop_duplicates(inplace = True)
        
    # handle missing values of customer column
        df.fillna({ 'customer' : 'Unknown'}, inplace = True)

    # handle missinge prices and quantities
        df.dropna(subset = ['quantity','price'], inplace = True)


    # Filter out rows where quantity <= 0
        df = df[df['quantity']>0]
        df.reset_index(drop=True, inplace=True) #ressting index bca after deleting column indexes also deltes


    # handling date columns
        date_formats = ['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']

        def parse_date(date_str):
            for i in date_formats:
                try:
                    return pd.to_datetime(date_str,format=i)
                except ValueError:
                    continue
            return pd.NaT

    
        df['order_clean_date'] =df['order_date'].apply(parse_date)
        df = df.drop(columns = ['order_date'])
        df = df.rename(columns = {'order_clean_date' : 'order_date'})
        df['order_id'] = df['order_id'].astype(int)
        df['quantity'] = df['quantity'].astype(int)

    #  add total_price column

        df['total_price'] = df['price'] * df['quantity']
        
        # adding column oder month
        df['order_month'] = df['order_date'].dt.to_period('M')
        df['order_month'] = df['order_month'].astype(str)
        logging.info(f"Data tansfomed succussfully: %d rows",len(df))
        return df
    except Exception as e:
        logging.error(f"Data not tansfomed succussfully: {e}")
        raise


def load(df,enginee,table_name):
    try:
        # Step 1: try to read existing order_ids from the table
        try:
            existingIds = pd.read_sql(sql= f'select order_id from {table_name}',con=enginee)['order_id'].tolist()
            # print(existingIds)
        except :
            existingIds = []
            
        # Step 2: filter df to only rows NOT already in the table
        
        new_rows = df[~df['order_id'].isin(existingIds)]
        
         # Step 3: insert only the new rows, using append instead of replace
        new_rows.to_sql(table_name, enginee, if_exists='append', index=False)
        logging.info(f"Inserted {len(new_rows)} new rows into {table_name} (skipped {len(df) - len(new_rows)} duplicates)")
        return
    except Exception as e:
        logging.error(f"Data not loaded into table {table_name}: {e}")
        raise
    
if __name__ == "__main__":
    try:
        
        parser = argparse.ArgumentParser(description="ETL pipeline for sales data")
        parser.add_argument("--file", type=str, default="sales_data.csv", help="Path to the input CSV file")
        parser.add_argument("--table", type=str, default="sales", help="Target table name in the database")

        args = parser.parse_args()
        
        password = db_password
        encoded_pass = quote_plus(password)
        enginee = create_engine(f'postgresql+psycopg://{db_user}:{encoded_pass}@{db_host}:{db_port}/{db_name}')
        
        raw_df = extract(args.file) #extract
        clean_df = transform(raw_df) #transform
        load(clean_df, enginee, args.table) #load
    
        logging.info("Pipeline completed successfully!")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise