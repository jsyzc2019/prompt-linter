#!/usr/bin/env python3
from __future__ import division

import sys
import GLIP_utils as GLIP
import tf2_ros
from tqdm import tqdm
import pickle

from helper import *

from ai2thor.controller import Controller
from ai2thor.platform import CloudRendering
from collections import defaultdict

from ai2thor.util.metrics import (
    get_shortest_path_to_object_type,
    path_distance,
    compute_single_spl
)


import time
import random
import cv2
import open3d as o3d
import matplotlib.pyplot as plt
from IPython import display

import torch
import openai
import os

import re
import string
from PIL import Image as PILImage
import numpy as np


import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo, PointCloud2
from nav_msgs.msg import OccupancyGrid, Odometry
from geometry_msgs.msg import Point, Pose, Quaternion, Twist, Vector3, PoseStamped
from tf.transformations import quaternion_from_euler, quaternion_multiply, euler_from_quaternion

import geometry_msgs.msg
import math

from notify_run import Notify

from subprocess import STDOUT, check_output

from std_srvs.srv import Empty

from nav_msgs.srv import GetMap, GetPlan

import json

from open3d_ros_helper import open3d_ros_helper as orh
import signal
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from lavis.models import load_model_and_preprocess 


## To kill process directly when CTRL+Z is called.
def handler(signum, frame):
    sys.exit()


TARGET_OBJECT_TYPES = [
    "AlarmClock",
    "Apple",
    "BaseballBat",
    "BasketBall",
    "Bowl",
    "GarbageCan",
    "HousePlant",
    "Laptop",
    "Mug",
    "RemoteControl",
    "SprayBottle",
    "Television",
    "Vase"
]

BACKGROUND_OBJECT_TYPES = [
    "ArmChair",
    "Bed",
    "Book",
    "Bottle",
    "Box",
    "ButterKnife",
    "Candle",
    "CD",
    "CellPhone",
    "Chair",
    "CoffeeTable",
    "Cup",
    "DeskLamp",
    "Desk",
    "DiningTable",
    "Drawer",
    "Dresser",
    "FloorLamp",
    "Fork",
    "Newspaper",
    "Painting",
    "Pencil",
    "Pen",
    "PepperShaker",
    "Pillow",
    "Plate",
    "Pot",
    "SaltShaker",
    "Shelf",
    "SideTable",
    "Sofa",
    "Statue",
    "TeddyBear",
    "TennisRacket",
    "TVStand",
    "Watch"
]

ALL_OBJECTS = TARGET_OBJECT_TYPES + BACKGROUND_OBJECT_TYPES

def map_saver(threshold_occupied, threshold_free, mapname, costmap_topic):

    """ Function to save the costmap generated by ROS
    """

    cmd = "rosrun map_server map_saver"
    if threshold_occupied:
        cmd += " --occ " + str(threshold_occupied)
    if threshold_free:
        cmd += " --free " + str(threshold_free)
    if mapname:
        cmd += " -f " + mapname
    cmd += " map:=" + costmap_topic
    subprocess.run(cmd, shell=True)

def ros_publish(event):

    """ Function to publish RoboTHOR event data to ROS
    """

    # print("\n\n\nMetadata is ", event.metadata)

    dp_img = event.depth_frame.copy()
    rgb_img = event.cv2img.copy()

    pos = event.metadata["agent"]["position"]
    orient = event.metadata["agent"]["rotation"]

    # rgb_img = np.frombuffer(rgb_img.data, dtype=np.uint8).reshape(rgb_img.height, rgb_img.width, -1)

    # rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2RGB)

    orient['x'] = np.deg2rad(orient['x'])
    orient['y'] = np.deg2rad(orient['y'])
    orient['z'] = np.deg2rad(orient['z'])

    dp_img[dp_img == np.inf] = 10
    dp_img[dp_img < 0.2] = 0

    # pcd, [fx, fy, cx, cy] = getPointCloud(event.frame.copy(), dp_img)

    # dp_img = dp_img.astype(np.uint16)

    depth_raw_message = CvBridge().cv2_to_imgmsg(dp_img, "passthrough")

    image_raw_message = CvBridge().cv2_to_imgmsg(rgb_img, "bgr8")

    cur_time = rospy.Time.now()

    # rospc = orh.o3dpc_to_rospc(pcd, frame_id="camera_link", stamp=cur_time)

    depth_raw_message.header.stamp = cur_time
    image_raw_message.header.stamp = cur_time

    depth_raw_message.header.frame_id = "camera_link"
    image_raw_message.header.frame_id = "camera_link"

    msg = CameraInfo(height=HEIGHT, width=WIDTH, distortion_model="plumb_bob", D=[0.0, 0.0, 0.0, 0.0, 0.0],
                     K=[fx, 0.0, cx, 0.0, fy, cy, 0.0, 0.0, 1.0],
                     R=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
                     P=[fx, 0.0, cx, -0.0, 0.0, fy, cy, 0.0, 0.0, 0.0, 1.0, 0.0])


    msg.header.stamp = cur_time
    msg.header.frame_id = "base_link"

    camera_info_pub.publish(msg)

    depth_raw_pub.publish(depth_raw_message)

    image_raw_pub.publish(image_raw_message)

    # pcl_pub.publish(rospc)

    # since all odometry is 6DOF we'll need a quaternion created from yaw
    ## Ros requires radians

    t = geometry_msgs.msg.TransformStamped()

    t.header.frame_id = "odom"
    t.child_frame_id = "base_link"

    # # Default from robothor is Pitch, Yaw, Roll, needs to be changed for ROS
    q = quaternion_from_euler(orient['x'], orient['z'], -orient['y'])

    t.header.stamp = cur_time
    t.transform.translation.x = pos['x']
    t.transform.translation.y = -pos['z']
    t.transform.translation.z = pos['y']
    t.transform.rotation.x = q[0]
    t.transform.rotation.y = q[1]
    t.transform.rotation.z = q[2]
    t.transform.rotation.w = q[3]

    # # print("\n\n\n\nTRANSFORM IS {}, {}, {}\n\n\n\n".format(orient['x'], -orient['z'], orient['y']))

    odom_broadcaster.sendTransform(t)

    odom = Odometry()
    odom.header.stamp = cur_time
    odom.header.frame_id = "odom"

    # set the position
    odom.pose.pose = Pose(Point(pos['x'], -pos['z'], pos['y']), Quaternion(*q))

    # set the velocity
    odom.child_frame_id = "base_link"
    odom.twist.twist = Twist(Vector3(0, 0, 0), Vector3(0, 0, 0))

    # publish the message
    odom_pub.publish(odom)

    cam_tf = geometry_msgs.msg.TransformStamped()

    cam_tf.header.frame_id = "base_link"
    cam_tf.child_frame_id = "camera_link"


    # # Default from robothor is Pitch, Yaw, Roll, needs to be changed for ROS

    q0 = quaternion_from_euler(0, 0, 0)
    q1 = quaternion_from_euler(np.deg2rad(0), np.deg2rad(90), np.deg2rad(0))
    q2 = quaternion_from_euler(np.deg2rad(0), np.deg2rad(0), np.deg2rad(-90))
    q3 = quaternion_from_euler(np.deg2rad(-90), np.deg2rad(0), np.deg2rad(0))
    q4 = quaternion_from_euler(np.deg2rad(0), np.deg2rad(90), np.deg2rad(0))

    # q1*q2 for open3d. Currently using point_cloud_xyzrgb
    q = quaternion_multiply(q0, q3)
    q = quaternion_multiply(q, q1)

    cam_tf.header.stamp = cur_time
    cam_tf.transform.translation.x = 0
    cam_tf.transform.translation.y = 0
    cam_tf.transform.translation.z = 1.5
    cam_tf.transform.rotation.x = q[0]
    cam_tf.transform.rotation.y = q[1]
    cam_tf.transform.rotation.z = q[2]
    cam_tf.transform.rotation.w = q[3]

    camera_transform_br.sendTransform(cam_tf)

    time.sleep(ROT_TIMEGAP)

    return 1
    # rate.sleep()


def rotate_in_place(target, thresh=0.8):

    """ Perform Rotate in Place (RIP), and return semantic information.
    """

    global RIP_RESOLUTION
    semantic_dict = defaultdict(list)

    caption_all =""
    for object in ALL_OBJECTS:
        caption_all += (f"{object} . ")

    # Setup GLIP target search variables
    target = string_correct(target)

    target_caption = f"{target} . "
    target_conf = thresh
    target_rotation = None
    target_im = None
    target_dp = None

    # Hardcoding 90 degree turns for when the robot uses LAVIS.
    if LAVIS_PASS is True:
        RIP_RESOLUTION = 90

    for i in range(0, 361, RIP_RESOLUTION):

        event = controller.step(action="RotateRight", degrees=RIP_RESOLUTION)
        ros_publish(event)

        if LAVIS_PASS:
            im_pil = PILImage.fromarray(event.cv2img)
            im_pil = vis_processors["eval"](im_pil).unsqueeze(0).to(device)
            lavis_caption = lavis_model.generate({"image": im_pil})

            semantic_dict[i].append(lavis_caption)

        else:

            yolo_results = yolo_model(event.frame.copy())
            df = yolo_results.pandas().xyxy[0]
            for ind in df.index:
                name = df['name'][ind]
                coords = [df['xmin'][ind], df['ymin'][ind], df['xmax'][ind], df['ymax'][ind]] 
                semantic_dict[name].append((int(i), coords))

        # Get GLIP Results on Target class and save if found. Can set thresh to make locking more accurate
        glip_target_result, _ = GLIP_model.run(event.frame.copy(), target, thresh=thresh, save=False)
        score = glip_target_result.get_field("scores").numpy()

        if score.size > 0:
            score = score[0]
        else:
            score = 0

        if len(glip_target_result) > 0 and score >= target_conf:
            target_rotation = i
            target_dp = event.depth_frame.copy()
            target_im = event.frame.copy()
            target_conf = score
            target_result = glip_target_result


        ## Hallway check
        if HALLWAY_CHECK:
            glip_hallway_result, _ = GLIP_model.run(event.frame.copy(), "hallway", thresh=0.8, save=False)
            if len(glip_hallway_result) > 0:
                semantic_dict['hallway'].append((int(i), glip_hallway_result.bbox[0]))
                # plt.imsave('hallway_image_{}.jpg',event.frame.copy())

    # Get target image and depth image to make point cloud, confidence for tracking, and heading for point cloud localization
    if target_rotation is not None:
        # Choosing GLIP output for target locking
        return [target_rotation, target_im, target_dp, target_result, target_conf]

    else:
        # For GPT Processing
        return semantic_dict

def move_forward_ros(event, reachable_pos, fd=None, allow_unknown = True):

    # Setting path planning param in unknown areas
    rospy.set_param('/rosparam set /move_base/NavfnROS/allow_unknown', allow_unknown)
    time.sleep(0.1)

    # Forward distance for sampling path.
    fd = fd or FORWARD_DIST

    tarposlist = []

    pos = event.metadata["agent"]["position"]
    orient = event.metadata["agent"]["rotation"]

    init_yaw = orient['y']

    q = quaternion_from_euler(orient['x'], orient['z'], -orient['y'])

    cur_time = rospy.Time.now()

    event = controller.step(action="MoveAhead", moveMagnitude=1)
    ros_publish(event)

    pos1 = event.metadata["agent"]["position"]

    orient = 1
    if (pos1['x'] - pos['x']) < 0:
        orient = -1

    # Picking a point along the linear direction
    newx = pos1['x'] + orient*fd
    newy = -(pos1['z'] + orient*fd)
    newz = pos1['y'] #-4.1374993324279785 # Weird fixed Z value on Thor

    print("Moving to {}, {} from {}, {}".format(newx, newy, pos['x'], -pos['z']))

    path = GetPlan()

    Start = PoseStamped()
    Start.header.seq = 0
    Start.header.frame_id = "odom"
    Start.header.stamp = cur_time
    Start.pose = Pose(Point(pos['x'], -pos['z'], pos['y']), Quaternion(*q))

    Goal = PoseStamped()
    Goal.header.seq = 0
    Goal.header.frame_id = "odom"
    Goal.header.stamp = cur_time
    Goal.pose = Pose(Point(newx, newy, newz), Quaternion(*q))

    path.start = Start
    path.goal = Goal
    path.tolerance = 2

    try:
        rospy.wait_for_service('/move_base/NavfnROS/make_plan', timeout=5)
        service = rospy.ServiceProxy('/move_base/NavfnROS/make_plan', GetPlan)
        retval = service(path.start, path.goal, path.tolerance)

    except:
        print("Plan Making Fail!")
        return []

    poselist = retval.plan.poses

    if len(poselist) == 0:
        return []

    # Counter for out of space points
    oosp = 0

    for pose in poselist:

        xpos = round(pose.pose.position.x, 3)
        ypos = round(pose.pose.position.y, 3)
        zpos = round(pose.pose.position.z, 3)

        orientation_q = pose.pose.orientation

        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (roll, pitch, yaw) = euler_from_quaternion(orientation_list)

        yaw = round(np.rad2deg(yaw),2)

        # tarpos = dict(x=xpos, y=ypos, z=zpos)

        minfunc = lambda x:np.sqrt((int(x["x"])-xpos)**2 + (int(-x["z"])-ypos)**2)

        tarpos = min(reachable_pos, key=minfunc)

        if np.sqrt((int(tarpos["x"])-xpos)**2 + (int(-tarpos["z"])-ypos)**2) >= PATH_FITTING_THRESHOLD:
            oosp += 1
            continue

        if tarpos not in reachable_pos:
            print("Path point {} not reachable! Yaw is {}.".format(tarpos, yaw))
            continue

        event = controller.step(
            action="Teleport",
            position=tarpos,
            rotation=dict(x=0, y=init_yaw, z=0),
        )

        ros_publish(event)

        if tarpos not in tarposlist:
            tarposlist.append(tarpos) 

        # print("Moving to {}, {}. Yaw is {}".format(xpos, ypos, yaw))

        # event = controller.step(action="MoveAhead", moveMagnitude=2.5)
        # ros_publish(event)

        # event = controller.step(action="MoveAhead", moveMagnitude=2.5)
        # ros_publish(event)

    print("Fitting efficiency is - {}%".format((100*(1-oosp/len(poselist)))))

    return tarposlist

def check_goal(event, target):

    for obj in event.metadata["objects"]:
        if obj['objectType'] == target:
            print(obj['objectType'], obj['visible'])
            if obj['visible']:
                print("GPT target was visibile! OSR successfull.")
                with open(respath + "/{}_osrsuc.txt".format(run_num), "w+") as f:
                    f.write("OSR Success! GPT found target. Object was {}.".format(target))

            dist = obj['distance']
            print("Distance to object is ", dist)
            if dist<=TARGET_DIST:
                return True
            else:
                return False

def finish_episode(target, event, initial_position, pathlist, psrsuc, psrtot):

    # event = controller.last_event

    if check_goal(event, target):

        controller.step(action="Done")

        print("\n\n\n\n EPISODE SUCCESS! \n\n\n\n")

        target_suc_dict[target] += 1

        try:
            short_path = get_shortest_path_to_object_type(
                controller=controller,
                object_type=target,
                initial_position=initial_position
            )

            spl = compute_single_spl(
                pathlist,
                short_path,
                1
            )

        except Exception as e:
            print("Exception at SPL computation - ", e)
            spl = 0

        return 1, spl, psrsuc, psrtot

    print("\n\n\n\n EPISODE FAILIURE! \n\n\n\n")

    try:
        short_path = get_shortest_path_to_object_type(
            controller=controller,
            object_type=target,
            initial_position=initial_position
        )

        spl = compute_single_spl(
            pathlist,
            short_path,
            0
        )

        target_suc_dict[target] -= 1

    except Exception as e:
        print("Exception at SPL computation - ", e)
        spl = 0

    return 0, spl, psrsuc, psrtot




def parse_scene(data, OSR=True):

    """ Parses the RoboTHOR scene to perform ObjNav. OSR = Oracle Success Rate, i.e., the rate of success of the agent successfully
        finding the target in its view, despite not being able to perform low level navigation towards it.
    """

    scene, target = data['scene'], data['object_type']

    initial_position, initial_orientation = data['initial_position'], data['initial_orientation']

    controller.reset(scene=scene)

    event = controller.step(
        action="Teleport",
        position=initial_position,
        rotation=initial_orientation,
        horizon=0
    )

    origmoves = ['MoveAhead', 'MoveBack', 'RotateRight', 'RotateLeft']
    moves = ['MoveAhead', 'MoveBack', 'RotateRight45', 'RotateLeft45', 'RotateRight90', 'RotateLeft90', 'STOP']
    directions = ['FRONT', 'RIGHT', 'BEHIND', 'LEFT']

    reachable_pos = controller.step(
        action="GetReachablePositions"
    ).metadata["actionReturn"]

    print("STARTING NEW EPISODE \n\nTarget object is {}. \n\n".format(target))

    movelist = []
    pathlist = []

    psrsuc = 0
    psrtot = 0

    for step in range(STEP_SIZE):

        # Images
        cv2_img = event.cv2img  # or file, Path, PIL, OpenCV, numpy, list

        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        im_pil = PILImage.fromarray(cv2_img)
        dp_img = event.depth_frame.copy()
        avg_dist = float(round(np.mean(dp_img), 2))

        pos = event.metadata["agent"]["position"]
        orient = event.metadata["agent"]["rotation"]

        pathlist.append(pos)

        #########################  Rotate in place and publish map  ######################################

        print("Looking for {} in the environment".format(target))
        results = rotate_in_place(target, thresh=GLIP_THRESHOLD)


############################### If GLIP finds Target! ##################################

        if type(results) is list: 

            target_rotation, target_im, target_dp, target_result, target_conf = results

            print(f"\n\n\n GLIP has found target with {target_conf} confidence! \n\n")

            print("Rotating {} degrees towards target.".format(target_rotation))

            event = controller.step(action="RotateRight", degrees=target_rotation)
            ros_publish(event)

            if OSR:

                for obj in event.metadata["objects"]:
                    if obj['objectType'] == target:
                        print(obj['objectType'], obj['visible'])
                        if obj['visible']:

                            print("GLIP target was accurate, and visible! OSR successfull.")
                            with open(respath + "/{}_osrsuc.txt".format(run_num), "w+") as f:
                                f.write("Success! GLIP was true with confidence {}. Object was {}.".format(target_conf, target))

                            return finish_episode(target, event, initial_position, pathlist, psrsuc, psrtot)

        
################################### YOLO + LLM Nav if target not found by GLIP ############################################

        else:
            print("\n\n\n Using LLM-Nav! \n\n")

            # For Prompt Success Rate
            psrtot += 1

            objpos_dict = results.copy()
            objlist = list(objpos_dict.keys())

            # If target is detected by YOLO, do depth check right away.
            target_corrected = string_correct(target)

            if LAVIS_PASS:
                indexlist = []

            else:
                indexlist = [idx for idx, s in enumerate(objlist) if target_corrected.lower() in s]


            if len(indexlist)>0:

                print("YOLO found target!")

                objlabel = objlist[indexlist[0]]

                angles = [elem[0] for elem in objpos_dict[str(objlabel)]]
                avg_ang = sum(angles)/len(angles)

                print("Rotating towards {} by {} degrees.".format(target_corrected, avg_ang))

                event = controller.step(action="RotateRight", degrees=avg_ang)
                ros_publish(event)

                if OSR:

                    for obj in event.metadata["objects"]:
                        if obj['objectType'] == target:
                            print(obj['objectType'], obj['visible'])
                            if obj['visible']:

                                print("YOLO object was accurate, and visibile! OSR successfull.")

                                with open(respath + "/{}_osrsuc.txt".format(run_num), "w+") as f:
                                    f.write("Success! YOLO was true. Object was {}.".format(target))

                                return finish_episode(target, event, initial_position, pathlist, psrsuc, psrtot)


            else:

                if LAVIS_PASS:
                    front_cmd = str(objpos_dict[90*0][0][0])
                    right_cmd = str(objpos_dict[90*1][0][0])
                    back_cmd = str(objpos_dict[90*2][0][0])
                    left_cmd = str(objpos_dict[90*3][0][0])
                    
                    prompt = (f"I want to find a {target} in my house."
                    f" In FRONT of you there is {front_cmd}." 
                    f" To your RIGHT, there is {right_cmd}."
                    f" BEHIND you there is {back_cmd}."
                    f" To your LEFT there is {left_cmd}." 
                    f" Which direction from {directions} should I go towards? Reply in ONE word.")

                else:
                    prompt = "I want to find a {} in my house. Which object from {} should I go towards? Reply in ONE word.".format(target_corrected, objlist)

                print(prompt)

                try:
                    output = gpt_pass(prompt)

                except Exception as e:
                    print("GPT-3 failed with error ", e)
                    print("Trying ChatGPT instead")

                    try:
                        output = opt_pass(prompt)

                    except Exception as e:
                        print("OPT also failed with error ", e)
                        print("Setting output to target.")
                        output = str(target)
                
                print("LLM output is {}".format(output))


                # Splitting the GPT output into words.
                splits = [''.join(c for c in s if c not in string.punctuation) for s in output.split()]

                objlabel = ""

                if LAVIS_PASS:
                    indexlist = [idx for idx, s in enumerate(directions) if splits[0].upper() in s]                    
                else:
                    # Getting the object label from GPT output
                    indexlist = [idx for idx, s in enumerate(objlist) if splits[0].lower() in s]

                # Checking if the label is valid, and rotating the agent towards it.
                if len(indexlist)>0:
                    objlabel = objlist[indexlist[0]]
                    print("objlabel is ", objlabel)
                    # objlabel = objlabel[0]
                    if LAVIS_PASS:

                        angles = [objlabel]
                        psrsuc += 1

                        with open(respath + "/{}_{}_psrsuc.txt".format(run_num, step), "w+") as f:
                            f.write("PSR Successfull. GPT output is - ".format(splits[0]))
                    
                    else:
                        if objlabel in objlist:
                            angles = [elem[0] for elem in objpos_dict[str(objlabel)]]
                            # angles = objpos_dict[str(objlabel)][0]
                            psrsuc += 1

                            with open(respath + "/{}_{}_psrsuc.txt".format(run_num, step), "w+") as f:
                                f.write("PSR Successfull. GPT output is - ".format(splits[0]))

                        else:
                            print("GPT output not in objlist")

                            with open(respath + "/{}_{}_psrfail.txt".format(run_num, step), "w+") as f:
                                f.write("PSR Failure. GPT output is - ".format(splits[0]))

                            angles = [np.random.randint(0, 360)]

                else:
                    print("GPT did not ouput an object from object list given! Randomly choosing a direction.")

                    with open(respath + "/{}_{}_psrfail.txt".format(run_num, step), "w+") as f:
                        f.write("PSR Failure. GPT output is - ".format(splits[0]))

                    angles = [np.random.randint(0, 360)]


                avg_ang = angles[0] #sum(angles)/len(angles)

                print("Rotating right by {} degrees. Moving towards {}!".format(avg_ang, objlabel))

                event = controller.step(action="RotateRight", degrees=avg_ang)
                ros_publish(event)

                ## Using ROS to plan a path in front of the robot and move ahead.
                poses = move_forward_ros(event, reachable_pos, allow_unknown=False)
                pathlist.extend(poses)

                if len(poses)==0:
                    print("Failed to move along path. Moving forward instead!")

                    for i in range(FORWARD_STEPS):

                        event = controller.step(action="MoveAhead", moveMagnitude=1)

                        ros_publish(event)
                        pathlist.append(event.metadata["agent"]["position"])

############################### Goal checking after run #############################################################################
    
    return finish_episode(target, event, initial_position, pathlist, psrsuc, psrtot)



""" The code below contains various hyperparameters for running the experiment.
    The results are stored as text files in a 'results' folder, with each episode and its concurrent runs.
    Note, you need to run 'compute_results.py' in order to get realtime statistics on the results.
"""



if __name__ == '__main__':

    HEIGHT = 512 # Image frame height
    WIDTH = 512 # Image frame width
    STEP_SIZE = 5 # How many times must the agent RIP with the LLM in a single episode.
    FOV = 60 # Field of View.
    RIP_RESOLUTION = 30 # Rotate in Place resolution.
    ROT_TIMEGAP = 0.001 # Sleep time between rotations.
    FORWARD_DIST = 6 # For the path planner, how many meters ahead should the agent go to explore?
    LOCKED_FORWARD_DIST = 2 # How many meters should the planner plan a path for after finding the target. Irrelavant for OSR.
    LOCKED_STEPS = 3 # Number of steps to move forward after target locking takes place.
    FORWARD_STEPS = 5 # Brute force alternate to move forward in Thor, if move_base fails to find a feasible path.
    TARGET_DIST = 2 # Target distance threshold for determining success.
    PATH_FITTING_THRESHOLD = 5 # In meters. For fitting ROS plan poses to Thor's positions. Higher value translates to more inflation/cushion space.
    GLIP_THRESHOLD = 0.7 # Threshold for accepting GLIP's predictions.
    EPISODE_SKIP = -1 # Number of Thor episodes to skip.
    VISIBILITY_DIST = 20 # Thor's visiblity distance.


    HALLWAY_CHECK = True # True, if the word "hallway" should be added to the detected object list.
    START_CURRENT = True # True, if episode runs need to be started where it left off.
    LAVIS_PASS = False # Set either this or YOLO_PASS to be True.
    YOLO_PASS = True # Set either this or LAVIS_PASS to be True.

    

    ## Computing intrinsics

    # Convert fov to focal length
    focal_length = 0.5 * WIDTH / math.tan(np.deg2rad(FOV / 2))
    
    # Camera intrinsics
    fx, fy, cx, cy = (focal_length, focal_length, WIDTH / 2, HEIGHT / 2)
    intrinsics = [fx, fy, cx, cy]


    ## Initialize CUDA
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.cuda.synchronize() 
    signal.signal(signal.SIGTSTP, handler)

    

    ## GLIP Setup
    GLIP_model = GLIP.GLIP()


    ## Semantic Extractor Setup
    if LAVIS_PASS:
        lavis_model, vis_processors, _ = load_model_and_preprocess(name="blip_caption", model_type="base_coco", is_eval=True, device=device)

    if YOLO_PASS:
        yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # or yolov5n - yolov5x6, custom
        yolo_model = torch.nn.DataParallel(yolo_model)

    
    ## ROS Setup
    
    rospy.init_node('robothor', anonymous=True)

    # Setting up Publishers
    depth_raw_pub = rospy.Publisher('depth_image', Image, queue_size=1)
    image_raw_pub = rospy.Publisher('rgb_image', Image, queue_size=1)
    camera_info_pub = rospy.Publisher("camera_info", CameraInfo, queue_size=1)
    odom_pub = rospy.Publisher("thor_odom", Odometry, queue_size=1)
    # pcl_pub = rospy.Publisher("pcl", PointCloud2, queue_size=1)

    odom_broadcaster = tf2_ros.TransformBroadcaster()
    camera_transform_br = tf2_ros.TransformBroadcaster()

    map_saver_pub = rospy.Publisher("map_saver", OccupancyGrid, queue_size=1)
    rate = rospy.Rate(10)




    ## RoboTHOR Setup

    kitchens = [f"FloorPlan{i}" for i in range(1, 31)]
    living_rooms = [f"FloorPlan{200 + i}" for i in range(1, 31)]
    bedrooms = [f"FloorPlan{300 + i}" for i in range(1, 31)]
    bathrooms = [f"FloorPlan{400 + i}" for i in range(1, 31)]

    all_scenes = kitchens + living_rooms + bedrooms + bathrooms

    controller = Controller(
        agentMode="locobot",
        visibilityDistance=VISIBILITY_DIST,
        scene=random.choice(all_scenes),
        gridSize=0.25,
        snapToGrid=True,
        movementGaussianSigma=0.005,
        rotateStepDegrees=90,
        rotateGaussianSigma=0.0,
        renderDepthImage=True,
        renderInstanceSegmentation=False,
        width=WIDTH,
        height=HEIGHT,
        fieldOfView=FOV,
        platform=CloudRendering
    )





    ## Variable Initialization

    filelist = []
    for root, dirs, files in os.walk('val/episodes/'):
        filelist.append(files)

    filelist = filelist[0]

    PSR_TOT = 0
    PSR_SUC = 0


    ## Starting from episode where the experiment was interrupted.

    if START_CURRENT:

        rex = re.compile('([0-9]+)')
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower()
                    for text in re.split(rex, s)]   

        covered = []
        for root, dirs, files in os.walk('results/'):
            covered.append(dirs)

        covered = covered[0]

        if len(covered) == 0:
            cur_epno = 0
            curr_run_num = 0

        else:
            covered.sort(key=natural_sort_key)
            cur_epno = covered[-1]
            cur_epno = int(re.search(r'\d+', cur_epno).group())

            covered = []
            
            for file in os.listdir('results/ep{}/'.format(cur_epno)):

                try:
                    curr_run_num = int(re.search(r'\d+', file).group())
                    covered.append(curr_run_num)

                except:
                    continue

            try:
                curr_run_num = int(sorted(covered)[-1])
            except:
                curr_run_num = 1

    # notify = Notify()


    # Temp. variables for storing runtime success rates.

    suc = 0
    splsuc = 0

    psrsuc = 0
    psrtot = 0
    psrscore = 0

    midsuc = 0
    midspl = 0
    midpsr = 0
    midpsrtot = 0

    totsuc = 0
    totspl = 0
    totpsr = 0

    datlen = 0


    # For per target success measurement
    target_suc_dict = dict()
    for i in ALL_OBJECTS:
        target_suc_dict[str(i)] = 0

    # target_suc_dict = np.load('target_success.pkl', allow_pickle=True)


    ################################ STARTING EXPERIMENT ##############################################

    for i, file in tqdm(enumerate(filelist)):

        # For skipping episodes
        if i < EPISODE_SKIP:
            continue

        if START_CURRENT:
            if i < cur_epno:
                continue

        # if i not in [6, 7]:
            # continue

        data = list(json.load(open(os.getcwd() + '/val/episodes/' + file)))

        datlen += len(data)

        respath = "results/ep{}".format(i)
        if not os.path.isdir(respath):
            os.mkdir(os.getcwd() + "/" + respath)

        for run_num, episode in tqdm(enumerate(data)):

            # print("Parsing episode {}. Run num is  {}. Expected run number is {}".format(i, run_num, curr_run_num))

            if START_CURRENT:
                if (run_num < curr_run_num) and (i==cur_epno):
                    continue
            try:
                suc, splsuc, psrsuc, psrtot = parse_scene(episode, OSR=True)
                torch.cuda.empty_cache()

            except Exception as e:
               print("Scene Parsing Failure! Exception: ", e)
               
               # notify.send('Exception occured! Parsing Failure - {}'.format(e))
               
               with open('target_success.pkl', 'wb+') as f:
                   pickle.dump(target_suc_dict, f)

            if psrtot>0:
                print(suc, splsuc, psrsuc/psrtot)
                psrscore = 100*(psrsuc/psrtot)
            else:
                print(suc, splsuc)
                psrscore = 0

            if suc == 1:
                with open(respath + "/{}_success.txt".format(run_num), "w+") as f:
                    f.write("Success! SPL was {}. Object was {}. Current PSR was {}%".format(splsuc, episode['object_type'], psrscore))

            else:
                with open(respath + "/{}_failure.txt".format(run_num), "w+") as f:
                    f.write("Failure! SPL was {}. Object was {}. Current PSR was {}%".format(splsuc, episode['object_type'], psrscore))


            # Dumping current target success rate
            with open('target_success_current.pkl', 'wb+') as f:
                pickle.dump(target_suc_dict, f)

            ## Saving and clearing the costmap!
            try:
                rospy.wait_for_service('/rtabmap/reset', timeout=5)
                service = rospy.ServiceProxy('/rtabmap/reset', Empty)
                retval = service()
                print(retval)

                rospy.wait_for_service('/rtabmap/trigger_new_map', timeout=5)
                service = rospy.ServiceProxy('/rtabmap/trigger_new_map', Empty)
                retval = service()
                print(retval)

                rospy.wait_for_service('/move_base/clear_costmaps', timeout=5)
                service = rospy.ServiceProxy('/move_base/clear_costmaps', Empty)
                retval = service()
                print(retval)

            except Exception as e:
                print("Service call failed: %s" % e)

            midsuc += suc
            midspl += splsuc

            midpsr += psrsuc
            midpsrtot += psrtot

            # Saving map
            # map_saver(90, 10, "{}/{}".format(respath,episode['id']), "/map")


        if midpsrtot == 0:
            print("Failed to use GPT in the entire episode!")
            psrscore = 0

        else:
            psrscore = 100*(midpsr/midpsrtot)

        print("\n\n\nEpisode {} Success Rate is {}, and Avg. SPL is {}. PSR is {}. \n\n\n".format(i, midsuc / len(data), midspl / len(data), psrscore))

        with open(respath + "/results.txt", "w+") as f:
            f.write("SR - {}".format(midsuc / len(data)))
            f.write("\nSPL - {}".format(midspl / len(data)))
            f.write("\nPSR - {}".format(psrscore))

        with open('target_success.pkl', 'wb+') as f:
            pickle.dump(target_suc_dict, f)

        totsuc += midsuc
        totspl += midspl

        PSR_SUC += midpsr
        PSR_TOT += midpsrtot
        
        midsuc = 0
        midspl = 0
        midpsr = 0
        midpsrtot = 0


    print("\n\n\n\nOverall SR is {}, and SPL is {}. PSR is {}/".format(totsuc/datlen, totspl/datlen, 100*(PSR_SUC/PSR_TOT)))

    with open("results/results.txt", "w+") as f:
        f.write("Overall SR - {}".format(totsuc / datlen))
        f.write("\nOverall SPL - {}".format(totspl / datlen))
        f.write("\nOverall PSR - {}".format(100*(PSR_SUC/PSR_TOT)))