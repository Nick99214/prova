# REQUEST
ODG_TYPE = 'odg'
INTERVENTI_TYPE = 'interventi'

# RESPONSE
OK = "OK"
OK_RESPONSE_MESSAGE = 'Sample created'
KO = "KO"
KO_RESPONSE_MESSAGE_NOT_ENOUGH_DATA = "The 'sample_size' specified is greater than the total number of records available. Please choose a smaller sample size."

#METADATA DATABASE
CLASS_COLUMN = 'CLASS'
SUPPORTO_COLUMN = 'SUPPORTO'
RECORD_ID_COLUMN = 'RECORD_ID'
BODY_COLUMN = 'BODY'
ABI_COLUMN = 'abi_code'
F1_COLUMN = 'F1'



#SAMPLING
SAMPLING_PERCENTAGE_COLUMN = 'sampling_percentage'
OPTIMAL_SAMPLING_FEEDBACK = 'Sampling is optimal'
SUBOPTIMAL_SAMPLING_FEEDBACK = 'Sampling is suboptimal. '
SAMPLE_STATUS_CREATED = 'CREATED'



#EXCEPTIONS
EXCEPTION_SAMPLING_TYPE = "SamplingException"
EXCEPTION_SAMPLING_ERROR_MESSAGE = "An error occurred during sampling process."
EXCEPTION_ORACLE_TYPE = "OracleException"
EXCEPTION_ORACLE_ERROR_MESSAGE = "An error occurred while interacting with Oracle DB."
EXCEPTION_ELASTIC_TYPE = "ElasticException"
EXCEPTION_ELASTIC_ERROR_MESSAGE = "An error occurred while interacting with Elasticsearch."
GENERAL_ERROR_MESSAGE = "General Error occurred."
