"""dickfake"""
import os
import json

import cv2
import numpy as np

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.components.containers.keypoint \
                                    import NormalizedKeypoint

from app.datalayer.schemas import Eyes, NotEyesException
from .utils import normalized_to_pixel_coordinates, \
                        overlay_image_alpha, preprocess_dick


class Dickfake:
    """core dickfake"""
    def __init__(self, dicks_path="/home/bot/dicks", 
                 mpdel_paath='/home/bot/models/detector.tflite'):
        self.dicks = [os.path.join(dicks_path, f)
                      for f in os.listdir(dicks_path)
                      if f.split(".")[-1] != 'json']

        with open(os.path.join(dicks_path, "eggs_labeling.json"), 'r',
                  encoding='utf-8') as f:
            labeling_eggs = json.load(f)
        self.result_eggs = dict()
        for eggs in labeling_eggs:
            img = os.path.join(dicks_path, eggs['img'].split('-')[-1])
            result_egg = dict()
            for side in eggs['kp-1']:
                side_name = side['keypointlabels'][0]
                result_egg[side_name] = NormalizedKeypoint(side['x']/100, side['y']/100)
            self.result_eggs[img] = result_egg

        base_options = python.BaseOptions(model_asset_path=mpdel_paath)
        options = vision.FaceDetectorOptions(base_options=base_options)
        self.detector = vision.FaceDetector.create_from_options(options)

    def __call__(self, filename) -> str:
        inbox_path = os.path.join("/home/bot/inbox_images", filename)
        image = mp.Image.create_from_file(inbox_path)
        keypoints = self.detect_keypoints(image)
        if len(keypoints) == 0:
            raise NotEyesException
        
        image = cv2.imread(inbox_path)
        for keypoint in keypoints:
            self.put_dick(keypoint, image)
        sent_path = os.path.join("/home/bot/sent_images", filename)
        cv2.imwrite(sent_path, image)

        return sent_path

    def put_dick(self, keypoint, image):

        height, width, _ = image.shape 
        dick_path = np.random.choice(self.dicks)
        dick = cv2.imread(dick_path)
        front_height, front_width, _ = dick.shape
        front_keys_n = [self.result_eggs[dick_path]['left'],
                        self.result_eggs[dick_path]['right']]

        back_eyes = Eyes(np.array(normalized_to_pixel_coordinates(keypoint[0].x, keypoint[0].y, width, height)),
                 np.array(normalized_to_pixel_coordinates(keypoint[1].x, keypoint[1].y, width, height)))

        front_eyes = Eyes(np.array(normalized_to_pixel_coordinates(front_keys_n[0].x, front_keys_n[0].y, front_width, front_height)),
                np.array(normalized_to_pixel_coordinates(front_keys_n[1].x, front_keys_n[1].y, front_width, front_height)))

        ready_dick, new_eyes = preprocess_dick(dick, back_eyes, front_eyes)
        alpha_mask = (ready_dick.sum(axis=2) / 765) < 0.98
        start_point = back_eyes.left - new_eyes.left
        overlay_image_alpha(image, ready_dick, start_point[0],
                            start_point[1], alpha_mask)
        

    def detect_keypoints(self, image):
        detection_result = self.detector.detect(image)
        keypoints = [det.keypoints[:2] for det in detection_result.detections]
        return keypoints
