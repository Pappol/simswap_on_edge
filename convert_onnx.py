from http.client import SWITCHING_PROTOCOLS
from re import T
import tensorflow as tf
import os
import cv2
import torch
import fractions
import numpy as np
from PIL import Image
import torch.nn.functional as F
from torchvision import transforms
from models.models import create_model
from options.test_options import TestOptions
import torch.onnx
import argparse
from os import listdir
from os.path import isfile, join


def convert_model():
    opt = TestOptions().parse()
    transformer = transforms.Compose([
            transforms.ToTensor(),
            #transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    transformer_Arcface = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])


    start_epoch, epoch_iter = 1, 0

    torch.nn.Module.dump_patches = True
    model = create_model(opt)
    model.eval()

    with torch.no_grad():    
        pic_a = opt.pic_a_path
        img_a = Image.open(pic_a).convert('RGB')
        img_a = transformer_Arcface(img_a)
        img_id = img_a.view(-1, img_a.shape[0], img_a.shape[1], img_a.shape[2])

        pic_b = opt.pic_b_path

        img_b = Image.open(pic_b).convert('RGB')
        img_b = transformer(img_b)
        img_att = img_b.view(-1, img_b.shape[0], img_b.shape[1], img_b.shape[2])

        # convert numpy to tensor
        img_id = img_id.cuda()
        img_att = img_att.cuda()

        #create latent id
        img_id_downsample = F.interpolate(img_id, size=(112,112))
        latend_id = model.netArc(img_id_downsample)
        latend_id = latend_id.detach().to('cpu')
        latend_id = latend_id/np.linalg.norm(latend_id,axis=1,keepdims=True)
        latend_id = latend_id.to('cuda')

        output_path = "./output/"
        torch.onnx.export(model,(img_id, img_att, latend_id, latend_id, True), output_path + "model.onnx",
                    export_params=True,opset_version=10, verbose=True)



convert_model()