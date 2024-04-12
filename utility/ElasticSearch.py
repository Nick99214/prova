__author__ = "Nicola Esposito"
from elasticsearch import Elasticsearch, helpers
import logging
import pandas as pd
import copy
from config import config
import json
from utility import Constants
from exceptions.CustomException import CustomException

class ElasticSearch():

    def __init__(self,request):
        self.settings = config.Settings()
        self.settings_pass = config.SettingsSecrets()
        self.mapping = json.load(open(self.settings.MAPPING_FIELDS_PATH, 'r'))
        self.use_https = self.settings.ELASTICSEARCH_HTTPS_FLAG
        self.user_es = self.settings.ELASTICSEARCH_USER
        self.secret_es = self.settings_pass.ELASTICSEARCH_PSW
        self.type = request.type
        self.start_date = request.start_sampling_date
        self.end_date = request.end_sampling_date
        self.host = self.settings.ELASTICSEARCH_HOST
        self.port = self.settings.ELASTICSEARCH_PORT
        self.timeout = self.settings.TIMEOUT
        self.source = self.get_source()
        self.scroll_time = self.settings.SCROLL_TIME
        self.doc_size = self.settings.DOC_SIZE
        self.client = self.create_elasticClient()

        with open('resources/query_template.json', 'r') as file:
            self.query_template = json.load(file)

    def create_elasticClient(self):
        """
        Creates an Elasticsearch client.

        Returns:
        Elasticsearch: The Elasticsearch client.
        """
        try:
            if self.use_https:
                http_auth = (self.user_es, self.secret_es)
                elastic_url = 'https://{}:{}'.format(self.host, self.port)
                return Elasticsearch(elastic_url, verify_certs=False, basic_auth=http_auth, timeout=self.timeout)
            else:
                elastic_url = 'http://{}:{}'.format(self.host, self.port)
                return Elasticsearch(elastic_url, timeout=self.timeout)
        except Exception as e:
            logging.error(f"Error creating Elasticsearch client: {e}")
            raise CustomException(Constants.EXCEPTION_ELASTIC_ERROR_MESSAGE, Constants.EXCEPTION_ELASTIC_TYPE)

    def get_source(self):
        """
        Gets the source fields for Elasticsearch query.

        Returns:
        list: A list of source fields.
        """
        if self.type == Constants.ODG_TYPE:
            source = self.settings.ES_ODG_SOURCE.split(',')
        elif self.type == Constants.INTERVENTI_TYPE:
            source = self.settings.ES_INTERVENTI_SOURCE.split(',')
        return source

    def process_hits(self, hits, source, df_buffer):
        """
        Processes hits obtained from Elasticsearch.

        Args:
        - hits (List[dict]): Hits obtained from Elasticsearch.
        - source (list): Source fields for the query.
        - df_buffer (pd.DataFrame): DataFrame buffer containing records from previous scrollings.

        Returns:
        DataFrame: The processed DataFrame.
        """
        for item in hits:
            diz = {}
            for col in source:

                if col == '_id':
                    diz['_id'] = item['_id']

                if (col in item['_source']):
                    if col == self.mapping["zzz-odg_list_key-zzz"]:
                        for i in range(len(item['_source'][col])):
                            try:
                                if item['_source'][col][i][self.mapping["zzz-omissis_key-zzz"]] == False and item['_source'][col][i][self.mapping["zzz-title_found_key-zzz"]] and item['_source'][col][i][self.mapping["zzz-title_sorted_key-zzz"]] and item['_source'][col][i][self.mapping["zzz-preclassification_check_key-zzz"]] == False:
                                    diz_buff = diz.copy()
                                    for col_nested in item['_source'][col][i]:
                                        if col_nested in source:
                                            diz_buff[col_nested] = item['_source'][col][i][col_nested]
                                        elif isinstance(item['_source'][col][i][col_nested], dict):
                                            for col_nested_dict in item['_source'][col][i][col_nested]:
                                                if col_nested_dict in source:
                                                    diz_buff[col_nested_dict] = item['_source'][col][i][col_nested][col_nested_dict]
                                    df_buffer = pd.concat([df_buffer, pd.DataFrame([diz_buff])], ignore_index=True)

                            except:
                                pass
                        diz = {}
                    else:
                        try:
                            diz[col] = item['_source'][col].replace('\n', '')
                        except:
                            diz[col] = item['_source'][col]

            if diz:
                df_buffer = pd.concat([df_buffer, pd.DataFrame([diz])], ignore_index=True)

        return df_buffer

    def read_response(self, response, source):
        """
        Reads response obtained from Elasticsearch.

        Args:
        - response (dict): Response obtained from Elasticsearch.
        - source (list): Source fields for the query.

        Returns:
        DataFrame: The DataFrame containing the retrieved data.
        """
        scrollID = response['_scroll_id']
        docTotal = len(response['hits']['hits'])
        count = 0

        df = pd.DataFrame()
        df = self.process_hits(response['hits']['hits'], source, df)

        while docTotal > 0:
            response = self.client.scroll(scroll_id=scrollID, scroll=self.scroll_time)
            count += 1
            df = self.process_hits(response['hits']['hits'], source, df)
            scrollID = response['_scroll_id']
            docTotal = len(response['hits']['hits'])
            logging.debug('Read {} docs'.format(df.shape[0]))

        return df

    def get_from_index(self, index, source, query_terms, date_field):
        """
        Gets data from an Elasticsearch index.

        Args:
        - index (str): The Elasticsearch index.
        - source (list): Source fields for the query.
        - query_terms (dict): Query terms for filtering.
        - date_field (str): The date field for filtering.

        Returns:
        DataFrame: The DataFrame containing the retrieved data.
        """
        try:
            body_request = copy.deepcopy(self.query_template)
            body_request["_source"] = source

            body_request['query']['bool']['must'][0]['range'][date_field] = {}
            body_request['query']['bool']['must'][0]['range'][date_field]['gte'] = self.start_date
            body_request['query']['bool']['must'][0]['range'][date_field]['lte'] = self.end_date
            body_request['query']['bool']['must'][0]['range'][date_field]["format"] = "yyyy-mm-dd"
            body_request['query']['bool']['must'][0]['range'][date_field]['time_zone'] = "Europe/Rome"

            if query_terms:
                for key in query_terms.keys():
                    body_request['query']['bool']['must'].append({"term": {key: query_terms[key]}})

            response = self.client.search(
                index=index,
                scroll=self.scroll_time,
                size=self.doc_size,
                body=body_request)
            return self.read_response(response, source)
        except Exception as e:
            logging.error(f"Error querying Elasticsearch index {index}: {e}")
            raise CustomException(Constants.EXCEPTION_ELASTIC_ERROR_MESSAGE, Constants.EXCEPTION_ELASTIC_TYPE)

    def insert_bulk(self, records):
        """
        Insert records in bulk into Elasticsearch from a pandas DataFrame.

        Args:
        - records: dictionary containing the records to be inserted.

        Returns:
        int: The number of successfully inserted records.
        """
        try:
            success,_ = helpers.bulk(self.client, records, refresh=True)
            return success
        except Exception as e:
            logging.error(f"Error bulk inserting records into Elasticsearch: {e}")
            raise CustomException(Constants.EXCEPTION_ELASTIC_ERROR_MESSAGE, Constants.EXCEPTION_ELASTIC_TYPE)

