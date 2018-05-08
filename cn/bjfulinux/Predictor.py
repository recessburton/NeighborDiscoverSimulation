import pickle
import pandas as pd


class Predictor:
    def __init__(self, model):
        self.classifier = self.restore_model(model)

    def restore_model(self, model):
        model_file_name = {
            'xgb': './cn/bjfulinux/xgboost.model',
            'svm': './cn/bjfulinux/svm.model',
            'bayes': './cn/bjfulinux/bayes.model'
        }[model]
        with open(model_file_name, 'rb') as fr:
            return pickle.load(fr)

    def predict(self, data):
        df = pd.DataFrame([data])
        df.columns = ['distance_r_p', 'distance_r_t', 'distance_p_t', 'rssi_r_p', 'rssi_r_t', 'com_r_p',
                      'com_r_t', 'com_p_t', 'com_r_p_t', 'max_rssi', 'avg_rssi', 'noise_thre']
        return self.classifier.predict(df)
