import psycopg2
import pandas as pd
# import logging
import json
from psycopg2.extras import execute_values
from src.config.credentials import db_config
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from src.config.queries import INSERT_MASTER_QUERY, INSERT_RECORD_QUERY, LIST_DATASET, LIST_SCHEME, LIST_DATASET_INFO,LIST_DATASET_RECORDS
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
                cursor.execute(INSERT_MASTER_QUERY, (dataset_name, description, lookup_key_colname, all_col_names))           
                ref_dset_master_id = cursor.fetchone()[0]
                
                records = []
                for _, row in df.iterrows():
                    for col_name, col_value in row.items():
                        if col_name != lookup_key_colname:
                            records.append((ref_dset_master_id, col_name, col_value, lookup_key_colname, row[lookup_key_colname]))
                            
                execute_values(cursor, INSERT_RECORD_QUERY, records)
                conn.commit()
                return 1 , "successfull"
            except Exception as e:
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
            
    def list_dataset_info(self):
        try:

            cursor.execute(LIST_DATASET_INFO)
            datasets = cursor.fetchall()
            print("Datasets-->", datasets)
            conn.commit()
            dataset_dicts = [{  "dataset_id": dataset[0],
                                "dataset_name": dataset[1],
                                "description": dataset[2],
                                "field": dataset[3].split(','),
                            } for dataset in datasets]

# Convert the list of dictionaries to a JSON string
            # json_output = json.dumps(dataset_dicts, indent=4)
            return {"status":"SUCCESS","Data": dataset_dicts}
        except Exception as e:
            data = f"Error: {str(e)}"
            return {"status":"FAILED","Data": data}
        
    def list_dataset_records(self, type_id):
        try:

            # cursor.execute(LIST_DATASET_RECORDS, (type_id,))
            # datasets = cursor.fetchall()
            # conn.commit()
            query =   f"""
                        SELECT  col_name, col_value, lk_colname, lk_colvalue
                        FROM ref_dset_records where type_id = {type_id}
                        """
            df = pd.read_sql_query(query, conn)

            pivot_df = df.pivot_table(index=['lk_colvalue'], columns='col_name', values='col_value', aggfunc='first').reset_index()

            pivot_df.rename(columns={'lk_colvalue': 'Scheme Name'}, inplace=True)
            # conn.close()
            conn.commit()
            result_dict = pivot_df.to_dict(orient='list')

            list_of_dicts = []

            for i in range(len(result_dict['Scheme Name'])):
                entry = {
                    "scheme_name": result_dict['Scheme Name'][i],
                    "fund_manager": result_dict['Fund Manager'][i],
                    "product_label": result_dict['Product Label'][i],
                    "risk_type": result_dict['Risk Type'][i]
                }
                list_of_dicts.append(entry)

            # final_response= json.dumps(list_of_dicts, indent=4)

            return {"status":"SUCCESS","data": list_of_dicts }
        except Exception as e:
            data = f"Error: {str(e)}"
            return {"status":"FAILED","data": data}
            
    def list_scheme(self,dataset_name):
        try:
            cursor.execute(LIST_SCHEME, (dataset_name,))
            scheme = cursor.fetchall()
            scheme_list = [item[0] for item in scheme]
            conn.commit()
            return {"status":"SUCCESS","data": scheme_list}
        except Exception as e:
            data = f"Error: {str(e)}"
            return {"status":"FAILED","data": data}