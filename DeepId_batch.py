#!/usr/bin/env python
# encoding: utf-8

"""
@author: liubo-it
@software: PyCharm Community Edition
@file: DeepId_batch.py
@time: 2016/5/25 14:49
"""


import os
from DeepID.DeepId1_batch.DeepId1_batch import train
from DeepID.util.DeepId import writer
from time import time
from Queue import Queue
import threading
import msgpack
from DeepID.util.MyThread import MyThread
from optparse import OptionParser
import pdb


class DeepIdBatch(object):
    def __init__(self, options, maxsize=3, epoch_num=10):
        # 每个batch数据很大,读入后可以多训练几轮
        self.train_queue = Queue(maxsize)
        self.valid_queue = Queue(maxsize)
        self.sample_list_file = '/data/liubo/face/vgg_face_dataset/all_data/all_sample_list.p'
        self.model_folder = '/data/liubo/face/vgg_face_dataset/model'
        self.train_batch_size = 12800
        self.valid_batch_size = 128
        self.epoch_num = epoch_num
        model_type = options.model_type
        if model_type == 'new_shape':
            self.input_shape = (3, 156, 124)# 每个图片的shape
            self.pic_shape = (156, 124, 3)
            self.model_file = os.path.join(self.model_folder, 'vgg_face.small_data.new_shape.rgb.deepid.model')
            self.weight_file = os.path.join(self.model_folder,'vgg_face.small_data.new_shape.rgb.deepid.weight')
        elif model_type == 'small_rgb':
            self.input_shape = (3, 50, 50)# 每个图片的shape
            self.pic_shape = (50, 50, 3)
            self.model_file = os.path.join(self.model_folder, 'vgg_face.all_data.small.rgb.deepid.model')
            self.weight_file = os.path.join(self.model_folder, 'vgg_face.all_data.small.rgb.deepid.weight')


    def read_train(self):
        train_sample_list, valid_sample_list = msgpack.load(open(self.sample_list_file, 'rb'))
        person_num = len(set([tmp[1] for tmp in train_sample_list]))
        train_batch_num = len(train_sample_list) / self.train_batch_size
        valid_batch_num = len(valid_sample_list) / self.valid_batch_size
        train_valid_model_args = (self.input_shape, person_num, self.model_file, self.weight_file, self.train_queue,
                    self.valid_queue, self.epoch_num, train_batch_num, valid_batch_num,)
        train_write_args = (self.train_queue, self.epoch_num, self.train_batch_size, train_sample_list,
                            train_batch_num, person_num, self.pic_shape)
        valid_write_args = (self.valid_queue, self.epoch_num, self.valid_batch_size, valid_sample_list,
                            valid_batch_num, person_num, self.pic_shape)
        train_valid_model_thread = MyThread(func=train, args=train_valid_model_args, name='train_valid_model')
        train_write_thread = MyThread(func=writer, args=train_write_args, name='train_write')
        valid_write_thread = MyThread(func=writer, args=valid_write_args, name='valid_write')
        train_valid_model_thread.start()
        train_write_thread.start()
        valid_write_thread.start()
        train_valid_model_thread.join()
        train_write_thread.join()
        valid_write_thread.join()


if __name__ == '__main__':


    parser = OptionParser()
    parser.add_option("-m", "--model_type", default='small_rgb',  help="model type")
    (options, args) = parser.parse_args()
    deepid = DeepIdBatch(options)
    deepid.read_train()

