import psycopg2
import pandas as pd
# import logging
from psycopg2.extras import execute_values
from src.config.credentials import db_config
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from src.config.queries import INSERT_MASTER_QUERY, INSERT_RECORD_QUERY, LIST_DATASET, LIST_SCHEME
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
            return 2 , f"The specified lookup key column '{lookup_key_colname}' does not exist in the CSV file."
            # raise ValueError(f"The specified lookup key column '{lookup_key_colname}' does not exist in the CSV file.")
        else:
            all_col_names = ','.join(df.columns)
            
            try:
            
                # insert_master_query = """
                # INSERT INTO Ref_dset_master (dset_name, description, lookup_key_colname, all_col_names)
                # VALUES (%s, %s, %s, %s) RETURNING Id;
                # """
                cursor.execute(INSERT_MASTER_QUERY, (dataset_name, description, lookup_key_colname, all_col_names))           
                ref_dset_master_id = cursor.fetchone()[0]
                
                # Prepare data for bulk insertion into Ref_dset_records, excluding lookup_key_colname as col_name
                records = []
                for _, row in df.iterrows():
                    for col_name, col_value in row.items():
                        if col_name != lookup_key_colname:
                            records.append((ref_dset_master_id, col_name, col_value, lookup_key_colname, row[lookup_key_colname]))
                            
                # Insert records into Ref_dset_records using execute_values for bulk insertion
                # insert_record_query = """
                # INSERT INTO Ref_dset_records (type_id, col_name, col_value, lk_colname, lk_colvalue)
                # VALUES %s;
                # """
                execute_values(cursor, INSERT_RECORD_QUERY, records)
                conn.commit()
                return 1 , "successfull"
            except Exception as e:
                print("Error-->", str(e))
                if conn:
                    conn.rollback()
                return 2, str(e)
            
                  
    def list_dataset(self):
        try:
            cursor.execute(LIST_DATASET)
            dataset = cursor.fetchall()
            dataset_list = [item[0] for item in dataset]
            conn.commit()
            
            return {"status":"SUCCESS","Data": dataset_list}
        except Exception as e:
            data = f"Error: {str(e)}"
            return {"status":"FAILED","Data": data}
            

    def list_scheme(self,dataset_name):
        try:
            cursor.execute(LIST_SCHEME, (dataset_name,))
            scheme = cursor.fetchall()
            scheme_list = [item[0] for item in scheme]
            conn.commit()
            return {"status":"SUCCESS","Data": scheme_list}
        except Exception as e:
            data = f"Error: {str(e)}"
            return {"status":"FAILED","Data": data}