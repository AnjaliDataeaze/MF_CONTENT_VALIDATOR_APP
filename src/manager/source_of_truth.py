import psycopg2
import pandas as pd
import logging
from psycopg2.extras import execute_values
from src.config.credentials import db_config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
except Exception as error:
    print(f"Error connecting to PostgreSQL: {error}")
    exit()

class Source_of_Truth:

    def upload_csv_to_db(self, csv_file_path, dataset_name, description, lookup_key_colname):
        df = pd.read_csv(csv_file_path)

        if lookup_key_colname not in df.columns:
            raise ValueError(f"The specified lookup key column '{lookup_key_colname}' does not exist in the CSV file.")
        
        # Get all column names as a comma-separated string
        all_col_names = ','.join(df.columns)
        
        try:
           
            # Insert metadata into Ref_dset_master
            insert_master_query = """
            INSERT INTO Ref_dset_master (dset_name, description, lookup_key_colname, all_col_names)
            VALUES (%s, %s, %s, %s) RETURNING Id;
            """
            cursor.execute(insert_master_query, (dataset_name, description, lookup_key_colname, all_col_names))
            
            # Get the generated Id for the inserted record
            ref_dset_master_id = cursor.fetchone()[0]
            print("reference_id", ref_dset_master_id)
            
            # Prepare data for bulk insertion into Ref_dset_records, excluding lookup_key_colname as col_name
            records = []
            for _, row in df.iterrows():
                for col_name, col_value in row.items():
                    if col_name != lookup_key_colname:
                        records.append((ref_dset_master_id, col_name, col_value, lookup_key_colname, row[lookup_key_colname]))
                        
            # Insert records into Ref_dset_records using execute_values for bulk insertion
            insert_record_query = """
            INSERT INTO Ref_dset_records (type_id, col_name, col_value, lk_colname, lk_colvalue)
            VALUES %s;
            """
            execute_values(cursor, insert_record_query, records)
            
            # Commit the transaction
            conn.commit()
            
        except Exception as e:
            logging.error(f"Error: {e}")
            if conn:
                conn.rollback()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
        logging.info(f"CSV file '{csv_file_path}' has been successfully uploaded to the database.")

# Database configuration