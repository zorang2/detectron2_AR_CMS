#!/usr/bin/env python3
# -- coding: utf-8 --

import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()
# import some common libraries
import torch
import numpy as np
import tqdm
import cv2
import glob
import re
# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.video_visualizer import VideoVisualizer
from detectron2.utils.visualizer import ColorMode, Visualizer
from detectron2.data import MetadataCatalog
from detectron2.structures import Boxes
import time

path = "/home/sldev1/Project/hyeongeun_test/data/AR_CMS_DATASET/221124/LH/"

def videoPath(path):
    video_path = glob.glob(path+'*.MP4')

    return video_path

video_list = videoPath(path)


def runOnVideo(video, maxFrames):
    """ Runs the predictor on every frame in the video (unless maxFrames is given),
    and returns the frame with the predictions drawn.
    """

    def onlykeep_wanted_class(outputs):
        cls = outputs['instances'].pred_classes
        scores = outputs["instances"].scores
        boxes = outputs['instances'].pred_boxes

        # index to keep whose class == 0
        # index chart
        # 0 = person -------------------------<br/>
        # 1 = bicycle ------------------------<br/>
        # 2 = car ----------------------------<br/>
        # 3 = motorcycle ---------------------<br/>
        # 4 = airplane
        # 5 = bus -----------------------------<br/>
        # 6 = train
        # 7 = truck ---------------------------<br/>

        a = (cls == 0).nonzero().flatten().tolist()
        b = (cls == 1).nonzero().flatten().tolist()
        c = (cls == 2).nonzero().flatten().tolist()
        d = (cls == 3).nonzero().flatten().tolist()
        e = (cls == 5).nonzero().flatten().tolist()
        f = (cls == 7).nonzero().flatten().tolist()

        a.extend(b)
        a.extend(c)
        a.extend(d)
        a.extend(e)
        a.extend(f)

        a.sort()

        indx_to_keep = a

        # only keeping index  corresponding arrays
        cls1 = torch.tensor(np.take(cls.cpu().numpy(), indx_to_keep))
        scores1 = torch.tensor(np.take(scores.cpu().numpy(), indx_to_keep))
        boxes1 = Boxes(torch.tensor(np.take(boxes.tensor.cpu().numpy(), indx_to_keep, axis=0)))

        # create new instance obj and set its fields
        obj = detectron2.structures.Instances(image_size=(frame.shape[0], frame.shape[1]))
        obj.set('pred_classes', cls1)
        obj.set('scores', scores1)
        obj.set('pred_boxes', boxes1)

        return obj

    readFrames = 0

    while True:
        hasFrame, frame = video.read()
        if not hasFrame:
            break

        # Get prediction results for this frame
        outputs = predictor(frame)  # original_output

        global person_count
        global bicycle_count
        global car_count
        global motorcycle_count
        global bus_count
        global truck_count
        person_count += (outputs['instances'].pred_classes).tolist().count(0)
        bicycle_count += (outputs['instances'].pred_classes).tolist().count(1)
        car_count += (outputs['instances'].pred_classes).tolist().count(2)
        motorcycle_count += (outputs['instances'].pred_classes).tolist().count(3)
        bus_count += (outputs['instances'].pred_classes).tolist().count(5)
        truck_count += (outputs['instances'].pred_classes).tolist().count(7)

        # print(f" person : {person_count} \n bicycle : {bicycle_count} \n car : {car_count} \n motorcycle_count : {motorcycle_count} \n bus : {bus_count} \n truck : {truck_count}")

        wanted_outputs = onlykeep_wanted_class(outputs)

        # Make sure the frame is colored
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Draw a visualization of the predictions using the video visualizer
        visualization = v.draw_instance_predictions(frame, wanted_outputs.to("cpu"))

        # Convert Matplotlib RGB format to OpenCV BGR format
        visualization = cv2.cvtColor(visualization.get_image(), cv2.COLOR_RGB2BGR)

        yield visualization

        readFrames += 1
        if readFrames > maxFrames:
            break


for i in tqdm.tqdm(video_list):

    # Extract video properties
    print("***************************\n", i, "\n*****************************")
    video = cv2.VideoCapture(i)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames_per_second = video.get(cv2.CAP_PROP_FPS)
    num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"width : {width}, height : {height}, frames_per_second : {frames_per_second}, num_frames : {num_frames}")

    # Initialize video writer
    video_writer = cv2.VideoWriter(i[:-4] + "_output_test.mp4", fourcc=cv2.VideoWriter_fourcc(*"mp4v"),
                                   fps=float(frames_per_second), frameSize=(width, height), isColor=True)

    # Initialize predictor
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.75  # set threshold for this model
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml")
    predictor = DefaultPredictor(cfg)

    # Initialize visualizer
    v = VideoVisualizer(MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), ColorMode.IMAGE)

    person_count = 0
    bicycle_count = 0
    car_count = 0
    motorcycle_count = 0
    bus_count = 0
    truck_count = 0

    # Create a cut-off for debugging
    num_frames = 60

    # Enumerate the frames of the video
    for visualization in tqdm.tqdm(runOnVideo(video, num_frames)):
        # Write test image
        cv2.imwrite(i[:-4] + '_output.png', visualization)

        # Write to video file
        video_writer.write(visualization)

    # print total count of classes
    print(
        f" {i}의 제원***********\n person : {person_count} \n bicycle : {bicycle_count} \n car : {car_count} \n motorcycle : {motorcycle_count} \n bus : {bus_count} \n truck : {truck_count}")

    details1 = [(
                    f" {i}의 제원***********\n person : {person_count} \n bicycle : {bicycle_count} \n car : {car_count} \n motorcycle : {motorcycle_count} \n bus : {bus_count} \n truck : {truck_count}")]
    details2 = [
        (f"width : {width}, height : {height}, frames_per_second : {frames_per_second}, num_frames : {num_frames}")]

    with open('readme.txt', 'w') as f:
        f.write('\n'.join(details1))
        f.write('\n'.join(details2))

    # Release resources
    video.release()
    video_writer.release()
    cv2.destroyAllWindows()

    # LH 걸린 시간 : 75:32:56