__author__ = "Nicola Esposito"
from config import config
import pandas as pd
from utility import Constants
import logging
from utility.Utils import dict_to_string
from sampler.SampleRecord import SampleRecord


class Sampler():

    def __init__(self,request):
        settings = config.Settings()
        self.weight_support = settings.WEIGHT_SUPPORT
        self.weight_f1_score = settings.WEIGHT_F1_SCORE
        self.sample_size = request.sample_size
        self.request = request


    def compute_sampling_weight(self, data):
        """
        Compute the sampling weight based on support and F1 score.

        Parameters:
        - data (DataFrame): The data containing support and F1 score for each class.

        Returns:
        DataFrame: The data with computed sampling weight.
        """


        # Peso inversamente proporzionale alla numerosità delle classi
        total_support = data[Constants.SUPPORTO_COLUMN].sum()

        support_percentage = (total_support / data[Constants.SUPPORTO_COLUMN]) / total_support

        # Peso inversamente proporzionale al f1_score delle classi
        f1_score_percentage = (1 / data[Constants.F1_COLUMN]) / (1 / data[Constants.F1_COLUMN]).sum()


        data[Constants.SAMPLING_PERCENTAGE_COLUMN] = (self.weight_support * support_percentage +
                                       self.weight_f1_score * f1_score_percentage) / (self.weight_support + self.weight_f1_score)

        # Normalizzazione dei pesi in modo che la somma sia 1
        data[Constants.SAMPLING_PERCENTAGE_COLUMN] = data[Constants.SAMPLING_PERCENTAGE_COLUMN] / data[Constants.SAMPLING_PERCENTAGE_COLUMN].sum()

        return data
    def create_feedback_message(self, sampling_status, undersampled_classes ):
      """
        Create feedback message based on sampling status.

        Parameters:
        - sampling_status (int): The status of the sampling process.
        - undersampled_classes (dict): A dictionary containing undersampled classes.

        Returns:
        tuple: A tuple containing the sampling feedback message and the feedback table.
      """
      if sampling_status == 0:
          sampling_feedback_message = Constants.OPTIMAL_SAMPLING_FEEDBACK
          logging.info(sampling_feedback_message)
          feedback_table = None
      else:
          sampling_feedback_message = Constants.SUBOPTIMAL_SAMPLING_FEEDBACK
          feedback_table = dict_to_string(undersampled_classes)
          logging.warning(sampling_feedback_message)
          logging.warning("Sampling distribution: {}".format(feedback_table))

      return sampling_feedback_message, feedback_table


    def weighted_sampling(self, df_weight, class_column, df_records ):
      """
        Perform weighted sampling of the records, based on the weights of df_weight

        Parameters:
        - df_weight (DataFrame): The data frame containing sampling weights.
        - class_column (str): The name of the column containing class labels.
        - df_records (DataFrame): The data frame containing records to sample.

        Returns:
        tuple: A tuple containing the sampled entries and the sample record.
      """


      # DataFrame vuoto per contenere i campioni estratti
      sample_entries = pd.DataFrame()
      # dizionario per memorizzare le classi sotto rappresentate
      undersampled_classes = {}
      # Variabile per gestire il gap di campionamento
      sample_gap = 0

      # Iterazione sulle classi in base alle percentuali di campionamento
      for class_name in list(df_weight.sort_values(by=Constants.SAMPLING_PERCENTAGE_COLUMN, ascending=False)[class_column]):

          # Seleziona i record della classe corrente
          df_class = df_records[df_records[class_column] == class_name]
          # Controlla se ci sono record per la classe in oggetto. Se non ci sono, il ciclo continua con la classe successiva

          # Calcola il numero totale di record nella classe
          total_rec_class = df_class.shape[0]
          # Calcola il numero di record da campionare per questa classe
          rec_to_sample = int(round(self.sample_size * df_weight[df_weight[class_column] == class_name][Constants.SAMPLING_PERCENTAGE_COLUMN]).values[0])

          if df_class.shape[0] == 0:
            undersampled_classes[class_name] = f"({total_rec_class}/{rec_to_sample})"
            continue
          # Se c'è un gap di campionamento precedente
          if sample_gap > 0:
              # Aggiungi il gap al numero di record da campionare
              rec_to_sample += sample_gap
              sample_gap = 0

          # Se il numero totale di record è minore o uguale al numero di record da campionare
          if total_rec_class <= rec_to_sample:
              # Aggiungi tutti i record della classe al campione
              sample_entries = pd.concat([sample_entries, df_class])
              # Se il numero totale di record è strettamente minore al numero di record da campionare aggiungi il nome della classe e la sua numerosità al dizionario delle classi sotto rappresentate
              if total_rec_class < rec_to_sample:
                  undersampled_classes[class_name] = f"({total_rec_class}/{rec_to_sample})"
              # Aggiorna il gap di campionamento
              sample_gap += rec_to_sample - total_rec_class
          else:
              # Se ci sono più ABI nella classe
              if df_class[Constants.ABI_COLUMN].nunique() > 1:
                  df_buff = pd.DataFrame()
                  counter = 0
                  # Ciclo finché il numero di record nel DataFrame buffer non raggiunge il numero desiderato
                  while df_buff.shape[0] < rec_to_sample:
                      # Conta il numero di occorrenze di ogni ABI nella classe
                      abi_value_counts = df_class[Constants.ABI_COLUMN].value_counts()
                      # Itera sugli ABI in ordine crescente di occorrenze
                      for abi in abi_value_counts.sort_values(ascending=True).index.tolist():
                          df_abi = df_class[df_class[Constants.ABI_COLUMN] == abi]
                          df_abi.reset_index(inplace=True, drop=True)
                          # Se ci sono record sufficienti per l'ABI corrente
                          if df_abi.shape[0] > counter:
                              # Aggiungi un record all'ABI corrente al DataFrame buffer
                              df_buff = pd.concat([df_buff, df_abi[counter:counter+1]])
                              # Se il DataFrame buffer contiene il numero di record da campionare per quella classe, allora interrompi il ciclo
                              if df_buff.shape[0] >= rec_to_sample:
                                  break
                      counter += 1
                  # Aggiungi i record estratti dal DataFrame buffer al campione
                  sample_entries = pd.concat([sample_entries, df_buff])
              else:
                  # Se c'è un'unica ABI nella classe, seleziona i primi record necessari
                  sample_entries = pd.concat([sample_entries, df_class[:rec_to_sample]])



      if df_weight[class_column].nunique() == df_records[class_column].nunique():
          if undersampled_classes:
              sampling_status = 1
          else:
              sampling_status = 0
      else:
          sampling_status = 2

      sampling_feedback_message, feedback_table = self.create_feedback_message(sampling_status, undersampled_classes)

      sample_record = SampleRecord( self.request, sampling_feedback_message, feedback_table, sample_entries)


      return sample_entries, sample_record
