import os

os.umask(0)
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
import random
import sys
import time
import shutil
from importlib import import_module
import torch
from torch.utils.data import Sampler, DataLoader



# root_path = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, root_path)

config = dict()

config['batch_size'] = 32

config['network_identifier']
config['loss_function_identifier']
config['optimizer_identifier']


def main():
    # Import all settings for experiment.
    train_dataloader = DataLoader(training_data, batch_size=batch_size)
    test_dataloader = DataLoader(test_data, batch_size=batch_size)

    config["train_split"] = os.path.join(root_path, "dataset\\HMC\\train\\data")
    config["val_split"] = os.path.join(root_path, "dataset\\HMC\\val\\data")
    config["test_split"] = os.path.join(root_path, "dataset\\HMC\\test_obs\\data")
    config['preprocess_train'] = os.path.join(root_path, "dataset\\HMC\\preprocess\\train_crs_dist6_angle90.p")
    config['preprocess_val'] = os.path.join(root_path, "dataset\\HMC\\preprocess\\val_crs_dist6_angle90.p")
    config['preprocess_test'] = os.path.join(root_path, "dataset\\HMC\\preprocess\\test_test.p")

    config['batch_size'] = 1


    # Data loader for training
    dataset = Dataset(config["train_split"], config, train=True)
    train_loader = DataLoader(
        dataset,
        batch_size=config["batch_size"],
        num_workers=config["workers"],
        collate_fn=collate_fn,
        pin_memory=True,
        drop_last=True,
    )

    epoch = config["epoch"]
    remaining_epochs = int(np.ceil(config["num_epochs"] - epoch))
    for i in range(remaining_epochs):
        train(epoch + i, config, train_loader, net, loss, post_process, opt, val_loader)


def train(epoch, config, train_loader, net, loss, post_process, opt, val_loader=None):
    net.train()

    num_batches = len(train_loader)
    epoch_per_batch = 1.0 / num_batches
    save_iters = int(np.ceil(config["save_freq"] * num_batches))
    display_iters = int(
        config["display_iters"] / (config["batch_size"])
    )
    val_iters = int(config["val_iters"] / (config["batch_size"]))

    start_time = time.time()
    metrics = dict()
    for i, data in tqdm(enumerate(train_loader)):
        epoch += epoch_per_batch
        data = dict(data)

        output = net(data)
        loss_out = loss(output, data)
        post_out = post_process(output, data)
        post_process.append(metrics, loss_out, post_out)

        opt.zero_grad()
        loss_out["loss"].backward()
        lr = opt.step(epoch)
        num_iters = int(np.round(epoch * num_batches))
        if num_iters % save_iters == 0 or epoch >= config["num_epochs"]:
            save_ckpt(net, opt, config["save_dir"], epoch)

        if num_iters % display_iters == 0:
            dt = time.time() - start_time
            metrics = sync(metrics)
            post_process.display(metrics, dt, epoch, lr)
            start_time = time.time()
            metrics = dict()

        if num_iters % val_iters == 0:
            val(config, val_loader, net, loss, post_process, epoch)

        if epoch >= config["num_epochs"]:
            val(config, val_loader, net, loss, post_process, epoch)
            return


def val(config, data_loader, net, loss, post_process, epoch):
    net.eval()

    start_time = time.time()
    metrics = dict()
    for i, data in enumerate(data_loader):
        data = dict(data)
        with torch.no_grad():
            output = net(data)
            loss_out = loss(output, data)
            post_out = post_process(output, data)
            post_process.append(metrics, loss_out, post_out)

    dt = time.time() - start_time
    metrics = sync(metrics)
    if hvd.rank() == 0:
        post_process.display(metrics, dt, epoch)
    net.train()


def save_ckpt(net, opt, save_dir, epoch):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    state_dict = net.state_dict()
    for key in state_dict.keys():
        state_dict[key] = state_dict[key].cpu()

    save_name = "%3.3f.ckpt" % epoch
    torch.save(
        {"epoch": epoch, "state_dict": state_dict, "opt_state": opt.opt.state_dict()},
        os.path.join(save_dir, save_name),
    )


def sync(data):
    data_list = comm.allgather(data)
    data = dict()
    for key in data_list[0]:
        if isinstance(data_list[0][key], list):
            data[key] = []
        else:
            data[key] = 0
        for i in range(len(data_list)):
            data[key] += data_list[i][key]
    return data


if __name__ == "__main__":
    main()