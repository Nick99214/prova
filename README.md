# Sampler API

RestAPI azionabile dall'interfaccia di monitoring delle annotazioni. Crea dei samples di N interventi o M OdG bilanciati secondo criteri vari. Il sample viene assegnato a due annotatori selezionati secondo criteri da definire. 

## Request & Response
**REQUEST**

La rest api risponde all'indirizzo http://127.0.0.1:5000/bki/api/v1/get_sample

Un esempio di body request è il seguente
```json
{
     "sample_size":100,
     "type":"odg",
     "start_sampling_date": "2022-12-05",
     "end_sampling_date": "2024-10-05",
     "annotator_1": "Mario",
     "annotator_2": "Luigi"

}
```
- *sample_size*: numerosità del campione da estrarre
- *type*: tipologia di campione da estrarre. Può essere odg o interventi
- *start_sampling_date*: data di inizio campionamento
- *end_sampling_date*: data di fine campionamento
- *annotator_1*: primo annotatore assegnato alla taggatura del campione
- *annotator_2*: secondo annotatore assegnato alla taggatura del campione

**RESPONSE**

Un esempio di response è la seguente
```json
{
    "result": "OK",
    "sample_id": "aacc2ddb-cd48-4b25-954d-c34d9da053e8",
    "response_message": "Sample created"
}
```
- *result*: indica l'esito dell'esecuzione del processo di classificazione ("OK" o "KO")
- *sample_id*: id del sample creato (vuoto in caso di KO)
- *response_message*: messaggio che spiega esito della risposta


## Guida all'installazione
Per l'installazione delle librerie necessarie alla corretta esecuzione del codice, lanciare il comando
```bash
    pip install -r requirements.txt
```

## Guida alla configurazione
Nella cartella *resources* è presente il file di configurazione *.env* nel quale sono riportati

- UVICORN_HOST: Indirizzo IP del server uvicorn.
- UVICORN_PORT: Porta del server uvicorn.
- mapping_fields_path: Percorso del file JSON di mapping dei campi.
- oracle_host: Indirizzo IP del server Oracle.
- oracle_port: Porta del server Oracle.
- oracle_service_name: Nome del servizio Oracle.
- oracle_username: Nome utente per l'accesso a Oracle.
- oracle_password: Password per l'accesso a Oracle.
- oracle_samples_table: Tabella Oracle contenente i record dei sample.
- oracle_interventi_classification_table: Tabella Oracle contente il report di classificazione degli interventi.
- oracle_odg_classification_table: Tabella Oracle contente il report di classificazione degli odg.
- elasticsearch_host: Indirizzo e porta del server Elasticsearch.
- use_https: Indica se utilizzare HTTPS per la connessione a Elasticsearch.
- user_es: Nome utente per l'accesso a Elasticsearch (se necessario).
- secret_es: Password per l'accesso a Elasticsearch (se necessario).
- timeout: Timeout per la connessione a Elasticsearch.
- index_interventi: Indice degli interventi in Elasticsearch.
- index_odg: Indice degli odg in Elasticsearch.
- scroll_time: Tempo di scorrimento per le richieste di ricerca in Elasticsearch.
- doc_size : numero massimo di documenti restituito ad ogni singola interrogazione di Elasticsearch  
- es_interventi_source: Campi sorgente per gli interventi in Elasticsearch.
- es_odg_source: Campi sorgente per gli odg in Elasticsearch.
- weight_support: Peso assegnato al supporto della classe nell'elaborazione della percentuale di campionamento per classi.
- weight_f1_score: Peso assegnato al f1_score della classe nell'elaborazione della percentuale di campionamento per classi.    
