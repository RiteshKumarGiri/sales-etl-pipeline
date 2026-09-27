import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus #to encode the special character in password
import logging
from dotenv import load_dotenv
import os
load_dotenv()

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


def load(df,enginee):
    try:
        engine = enginee 
        df.to_sql('sales', engine, if_exists='replace', index=False)
        logging.info(f'Data has been loaded to sales table sucessfully')
        return
    except Exception as e:
        logging.error(f"Data not loaded into table: {e}")
        raise
    
if __name__ == "__main__":
    try:
        password = db_password
        encoded_pass = quote_plus(password)
        enginee = create_engine(f'postgresql+psycopg://{db_user}:{encoded_pass}@{db_host}:{db_port}/{db_name}')
        
        raw_df = extract("sales_data.csv") #extract
        clean_df = transform(raw_df) #transform
        load(clean_df, enginee) #load
    
        logging.info("Pipeline completed successfully!")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise