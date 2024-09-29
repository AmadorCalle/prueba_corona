import pickle
import os

def load_model(model_filename):
    model_path = os.path.join(os.path.dirname(__file__), model_filename)
    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)
    return model