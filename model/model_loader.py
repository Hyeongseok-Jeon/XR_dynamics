from model.loss import loss
from model.network import network
from model.optimizer import optimizer

def get_model(config):
    network_id = config['network_identifier']
    loss_id = config['loss_function_identifier']
    optimizer_id = config['optimizer_identifier']

