__author__ = "Nicola Esposito"
import pandas as pd
from config import config
import cx_Oracle
import logging
cx_Oracle.init_oracle_client(lib_dir=r"C:\Oracle\instantclient_21_13")
from exceptions.CustomException import CustomException
from utility import Constants
class OracleDBConnector():

    def __init__(self):
        self.settings = config.Settings()
        self.settings_pass = config.SettingsSecrets()
        self.host = self.settings.ORACLEDB_HOST
        self.port = self.settings.ORACLEDB_PORT
        self.service_name = self.settings.ORACLEDB_SERVICE
        self.username = self.settings.ORACLEDB_USER
        self.password = self.settings_pass.ORACLEDB_PSW

        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        """
        Establishes a connection to the Oracle database.
        """
        try:
            connection_string = f'{self.username}/{self.password}@{self.host}:{self.port}/{self.service_name}'
            self.connection = cx_Oracle.connect(connection_string, mode=cx_Oracle.SYSDBA)
            self.cursor = self.connection.cursor()
        except cx_Oracle.Error as error:
            logging.error("Error while connecting with Oracle DB {}:".format(self.host), error)
            raise CustomException(Constants.EXCEPTION_ORACLE_ERROR_MESSAGE,Constants.EXCEPTION_ORACLE_TYPE)

    def disconnect(self):
        """
        Disconnects from the Oracle database.
        """

        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()



    def read_table(self, query):
        """
        Executes a query to read data from a table in the Oracle database.

        Args:
        - query (str): The SQL query to execute.

        Returns:
        pd.DataFrame: A DataFrame containing the fetched records from the table.
        """
        
        try:
            self.cursor.execute(query)
            records = self.cursor.fetchall()
            df = pd.DataFrame(records, columns=[col[0] for col in self.cursor.description])
            return df

        except cx_Oracle.Error as error:
            logging.error("Error while reading records from Oracle DB:", error)
            raise CustomException(Constants.EXCEPTION_ORACLE_ERROR_MESSAGE,Constants.EXCEPTION_ORACLE_TYPE)


    def insert_record(self, new_record, table_name):
        """
        Inserts a new record into a specified table in the Oracle database.

        Args:
        - new_record (SampleRecord): The record to be inserted.
        - table_name (str): The name of the table where the record will be inserted.
        """
        try:
            rec_fields = list(new_record.get_attribute_names())
            insert_query = f"INSERT INTO {table_name} ({', '.join(rec_fields)}) VALUES (:{', :'.join(rec_fields)})"
            self.cursor.execute(insert_query, new_record.to_dict())
            self.connection.commit()
        except cx_Oracle.Error as error:
            logging.error("Error while inserting records into {}:".format(table_name), error)
            raise CustomException(Constants.EXCEPTION_ORACLE_ERROR_MESSAGE,Constants.EXCEPTION_ORACLE_TYPE)

