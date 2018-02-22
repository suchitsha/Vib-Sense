from __future__ import absolute_import, division, print_function

# only keep warnings and errors
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='0'

import requests
import time
import tensorflow as tf
import scipy.misc
import matplotlib.pyplot as plt
import cv2
import numpy as np
from monodepth_model import *


def post_process_disparity(disp):
    _, h, w = disp.shape
    l_disp = disp[0,:,:]
    r_disp = np.fliplr(disp[1,:,:])
    m_disp = 0.5 * (l_disp + r_disp)
    l, _ = np.meshgrid(np.linspace(0, 1, w), np.linspace(0, 1, h))
    l_mask = 1.0 - np.clip(20 * (l - 0.05), 0, 1)
    r_mask = np.fliplr(l_mask)
    return r_mask * l_disp + l_mask * r_disp + (1.0 - l_mask - r_mask) * m_disp

def get_image():
    # read is the easiest way to get a full image out of a VideoCapture object.
    camera_port = 0
    camera = cv2.VideoCapture(camera_port)
    time.sleep(0.5)  # otherwise the image is dark
    retval, im = camera.read()
    return im

def pooling(depth_grad):
    # RETURN AVERAGE DEPTH VALUE PER CELL, WHICH IS THE SIZE OF THE IMAGE DEVIDED BY THE NUMBER OF RAWS AND COLUMSNS
    height = 256
    width = 512
    raws = 3
    columns = 3
    cell_height = int(height/raws)
    cell_width = int(width/columns)
    min_val = np.amin(depth_grad)
    max_val = np.amax(depth_grad)
    depth_grad = depth_grad/max_val
    grid = np.ones((raws, columns))
    for i in xrange(raws):
        for k in xrange(columns):
            grid[i, k] = np.average(depth_grad[i*cell_height:(i+1)*cell_height,k*cell_width:(k+1)*cell_width])
    return grid



def test_simple(params):

    height = 256
    width = 512
    # img_path = '/home/pjk/depth/monodepth/building.jpg'
    checkpoint = '/home/pjk/depth/monodepth/models/model_cityscapes'

    left = tf.placeholder(tf.float32, [2, height, width, 3])
    model = MonodepthModel(params, "test", left, None)

    while(True):
        start_time = time.time()
        input_image = get_image()
        if input_image == None:
            continue
        original_height, original_width, num_channels = input_image.shape
        input_image = scipy.misc.imresize(input_image, [height, width], interp='lanczos')
        input_image = input_image.astype(np.float32) / 255
        input_images = np.stack((input_image, np.fliplr(input_image)), 0)

        # UNCOMMENT THE FOLLOWING TO SAVE RAW IMAGE (and img_path above)
        # file = "./test_image.png"
        # input_image = scipy.misc.imresize(input_image, [original_height, original_width], interp='lanczos')
        # cv2.imwrite(file, input_image)

        # SESSION
        config = tf.ConfigProto(allow_soft_placement=True)
        sess = tf.Session(config=config)

        # SAVER
        train_saver = tf.train.Saver()

        # INIT
        sess.run(tf.global_variables_initializer())
        sess.run(tf.local_variables_initializer())
        coordinator = tf.train.Coordinator()

        # RESTORE
        restore_path = checkpoint.split(".")[0]
        train_saver.restore(sess, restore_path)

        disp = sess.run(model.disp_left_est[0], feed_dict={left: input_images})
        disp_pp = post_process_disparity(disp.squeeze()).astype(np.float32)

        print('Depth grid: ')
        print(pooling(disp_pp))
        res = requests.post('http://192.168.5.127:5000/depth_grid', json=np.array2string(pooling(disp_pp)))
        print('Response from server:', res.text)
        # UNCOMMENT THE FOLLOWING TO SAVE DEPTH IMAGE
        # output_directory = '/home/pjk/depth/monodepth/'
        # output_name = 'test_image'
        # np.save(os.path.join(output_directory, "{}_disp.npy".format(output_name)), disp_pp)
        # disp_to_img = scipy.misc.imresize(disp_pp.squeeze(), [original_height, original_width])
        # plt.imsave(os.path.join(output_directory, "{}_disp.png".format(output_name)), disp_to_img, cmap='plasma')
        print('Execution time: ')
        print (time.time() - start_time)


def main(_):

    params = monodepth_parameters(
        encoder='vgg',
        height=256,
        width=512,
        batch_size=2,
        num_threads=1,
        num_epochs=1,
        do_stereo=False,
        wrap_mode="border",
        use_deconv=False,
        alpha_image_loss=0,
        disp_gradient_loss_weight=0,
        lr_loss_weight=0,
        full_summary=False)

    test_simple(params)


if __name__ == '__main__':
    tf.app.run()
