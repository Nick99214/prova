from config import config
from sampler.Sampler import Sampler
from sampler.SampleEntry import SampleEntry
from utility import Constants
from utility.ElasticSearch import ElasticSearch
from utility.OracleDBConnector import OracleDBConnector
from exceptions.CustomException import CustomException
import json
import logging
class Service:
    def __init__(self, request):
        self.settings = config.Settings()
        self.mapping  = json.load(open(self.settings.MAPPING_FIELDS_PATH, 'r'))
        self.request = request
        self.sampler = Sampler(request)
        self.oracle_client = OracleDBConnector()
        self.es_client = ElasticSearch(request)



    def get_class_report(self):
        """
        Gets the classification report of last training.

        Returns:
        DataFrame: The classification report.
        """
        query = "SELECT * FROM {}"
        table_name, id_field = self._get_classification_table()
        query = query.format(table_name)
        df_class_report = self.oracle_client.read_table(query)
        df_class_report.rename(columns={id_field: Constants.CLASS_COLUMN}, inplace=True)
        return df_class_report

    def _get_classification_table(self):
        """
        Gets the name of table containing the classification report.

        Returns:
        tuple: A tuple containing the table name and the ID field.
        """
        if self.request.type == Constants.INTERVENTI_TYPE:
            return self.settings.ORACLE_INTERVENTI_CLASSIFICATION_TABLE, self.mapping["zzz-codice_interventi_class_table_key-zzz"]
        elif self.request.type == Constants.ODG_TYPE:
            return self.settings.ORACLE_ODG_CLASSIFICATION_TABLE, self.mapping["zzz-codice_odg_class_table_key-zzz"]


    def get_documents(self):
        """
        Gets the documents from Elasticsearch that will be used for sampling.

        Returns:
        DataFrame: The obtained documents.
        """
        if self.request.type == Constants.INTERVENTI_TYPE:
            query_terms = {self.mapping["zzz-is_sentence_key-zzz"]: True,self.mapping["zzz-is_ner_subj_key-zzz"]: True}
            df_documents = self.es_client.get_from_index(self.settings.ELASTICSEARCH_BI_INDEX, self.es_client.source, query_terms=query_terms, date_field='dataConsiglio')
            class_field = self.mapping["zzz-tipologia_intervento_key-zzz"]
            id_field = self.mapping["zzz-interventi_id_field_key-zzz"]
            body_field = self.mapping["zzz-interventi_body_field_key-zzz"]
        elif self.request.type == Constants.ODG_TYPE:
            df_documents= self.es_client.get_from_index(self.settings.ELASTICSEARCH_ML_INDEX, self.es_client.source, query_terms=None, date_field='created_at')
            class_field = self.mapping["zzz-codice_odg_key-zzz"]
            id_field = self.mapping["zzz-odg_id_field_key-zzz"]
            body_field = self.mapping["zzz-odg_body_field_key-zzz"]



        df_documents.rename(columns={class_field: Constants.CLASS_COLUMN, id_field: Constants.RECORD_ID_COLUMN, body_field: Constants.BODY_COLUMN},inplace=True)
        return df_documents


    def do_sampling(self, df_class_report, df_records):
        """
        Performs sampling process.

        Args:
        df_class_report (pd.DataFrame): The classification report.
        df_records (pd.DataFrame): records to sample.

        Returns:
        tuple: A tuple containing the sampled items and the sampling record.
        """
        try:
            df_weight = self.sampler.compute_sampling_weight(df_class_report)
            return self.sampler.weighted_sampling(df_weight, Constants.CLASS_COLUMN, df_records)
        except Exception as e:
            raise CustomException( Constants.EXCEPTION_SAMPLING_ERROR_MESSAGE, Constants.EXCEPTION_SAMPLING_TYPE)
    def do_sample_entries_insertion(self,sample_entries, sample_id):
        """
        Performs insertion of sampled entries into Elasticsearch.

        Args:
        sample_entries(pd.DataFrame): The sampled entries.
        sample_id (str): The ID of the sample.

        Returns:
        int: The number of entries successfully inserted.
        """


        bulk_rows = []
        for _, row in sample_entries.iterrows():
            sample_entry = SampleEntry(
                record_id=row[Constants.RECORD_ID_COLUMN],
                record_type=self.request.type,
                body=row[Constants.BODY_COLUMN],
                model_category=row[Constants.CLASS_COLUMN],
                protocollo=row[self.mapping["zzz-protocollo_key-zzz"]],
                sample_id=sample_id
            )

            row_entry = {
                '_index': self.settings.ELASTICSEARCH_SAMPLES_ENTRIES_INDEX,
                '_source': sample_entry.to_dict()
            }
            bulk_rows.append(row_entry)
        return self.es_client.insert_bulk(bulk_rows)

    def do_sampling_pipeline(self):
        """
        Performs the sampling pipeline.

        Returns:
        str: The ID of the created sample.
        """

        logging.info("Reading data from elasticsearch")
        df_documents = self.get_documents()
        if df_documents.shape[0] < self.request.sample_size:
            return ''
        logging.info("Reading data from oracle")
        df_class_report = self.get_class_report()
        logging.info("Starting sampling process")
        sample_entries, sample_record = self.do_sampling(df_class_report, df_documents)
        logging.info("The sample has been created")
        self.oracle_client.insert_record(sample_record, self.settings.ORACLE_SAMPLES_TABLE)
        logging.info("Successfully inserted sample record into oracle table {}".format(self.settings.ORACLE_SAMPLES_TABLE))
        success = self.do_sample_entries_insertion(sample_entries, sample_record.sample_id)
        logging.info(f"Successfully inserted {success} sample's entries into Elasticsearch index '{self.settings.ELASTICSEARCH_SAMPLES_ENTRIES_INDEX}'.")
        self.oracle_client.disconnect()
        return sample_record.sample_id