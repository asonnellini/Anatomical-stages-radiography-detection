import argparse
import os
import glob
import random
import darknet2
import time
import cv2
import numpy as np


def parser():
    parser = argparse.ArgumentParser(description="YOLO Object Detection")
    parser.add_argument("--input", type=str, default="",
                        help="image source. It can be a single image, a"
                        "txt with paths to them, or a folder. Image valid"
                        " formats are jpg, jpeg or png."
                        "If no input is given, ")
    parser.add_argument("--batch_size", default=1, type=int,
                        help="number of images to be processed at the same time")
    parser.add_argument("--weights", default="yolov4.weights",
                        help="yolo weights path")
    parser.add_argument("--dont_show", action='store_true',
                        help="windown inference display. For headless systems")
    parser.add_argument("--ext_output", action='store_true',
                        help="display bbox coordinates of detected objects")
    parser.add_argument("--save_labels", action='store_true',
                        help="save detections bbox for each image in yolo format")
    parser.add_argument("--config_file", default="./cfg/yolov4.cfg",
                        help="path to config file")
    parser.add_argument("--data_file", default="./cfg/coco.data",
                        help="path to data file")
    parser.add_argument("--thresh", type=float, default=.25,
                        help="remove detections with lower confidence")
    return parser.parse_args()


def check_arguments_errors(args):
    assert 0 < args.thresh < 1, "Threshold should be a float between zero and one (non-inclusive)"
    if not os.path.exists(args.config_file):
        raise(ValueError("Invalid config path {}".format(os.path.abspath(args.config_file))))
    if not os.path.exists(args.weights):
        raise(ValueError("Invalid weight path {}".format(os.path.abspath(args.weights))))
    if not os.path.exists(args.data_file):
        raise(ValueError("Invalid data file path {}".format(os.path.abspath(args.data_file))))
    if args.input and not os.path.exists(args.input):
        raise(ValueError("Invalid image path {}".format(os.path.abspath(args.input))))


def check_batch_shape(images, batch_size):
    """
        Image sizes should be the same width and height
    """
    shapes = [image.shape for image in images]
    if len(set(shapes)) > 1:
        raise ValueError("Images don't have same shape")
    if len(shapes) > batch_size:
        raise ValueError("Batch size higher than number of images")
    return shapes[0]


def load_images(images_path):
    """
    If image path is given, return it directly
    For txt file, read it and return each line as image path
    In other case, it's a folder, return a list with names of each
    jpg, jpeg and png file
    """
    input_path_extension = images_path.split('.')[-1]
    if input_path_extension in ['jpg', 'jpeg', 'png']:
        return [images_path]
    elif input_path_extension == "txt":
        with open(images_path, "r") as f:
            return f.read().splitlines()
    else:
        return glob.glob(
            os.path.join(images_path, "*.jpg")) + \
            glob.glob(os.path.join(images_path, "*.png")) + \
            glob.glob(os.path.join(images_path, "*.jpeg"))


def prepare_batch(images, network, channels=3):
    width = darknet.network_width(network)
    height = darknet.network_height(network)

    darknet_images = []
    for image in images:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_resized = cv2.resize(image_rgb, (width, height),
                                   interpolation=cv2.INTER_LINEAR)
        custom_image = image_resized.transpose(2, 0, 1)
        darknet_images.append(custom_image)

    batch_array = np.concatenate(darknet_images, axis=0)
    batch_array = np.ascontiguousarray(batch_array.flat, dtype=np.float32)/255.0
    darknet_images = batch_array.ctypes.data_as(darknet.POINTER(darknet.c_float))
    return darknet.IMAGE(width, height, channels, darknet_images)


def image_detection(image_path, network, class_names, class_colors, thresh):
    # Darknet doesn't accept numpy images.
    # Create one with image we reuse for each detect
    width = darknet2.network_width(network)
    height = darknet2.network_height(network)
    darknet_image = darknet2.make_image(width, height, 3)

    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (width, height),
                               interpolation=cv2.INTER_LINEAR)

    darknet2.copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = darknet2.detect_image(network, class_names, darknet_image, thresh=thresh)
    darknet2.free_image(darknet_image)
    image = darknet2.draw_boxes(detections, image_resized, class_colors)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), detections


def batch_detection(network, images, class_names, class_colors,
                    thresh=0.25, hier_thresh=.5, nms=.45, batch_size=4):
    image_height, image_width, _ = check_batch_shape(images, batch_size)
    darknet_images = prepare_batch(images, network)
    batch_detections = darknet2.network_predict_batch(network, darknet_images, batch_size, image_width,
                                                     image_height, thresh, hier_thresh, None, 0, 0)
    batch_predictions = []
    for idx in range(batch_size):
        num = batch_detections[idx].num
        detections = batch_detections[idx].dets
        if nms:
            darknet.do_nms_obj(detections, num, len(class_names), nms)
        predictions = darknet2.remove_negatives(detections, class_names, num)
        images[idx] = darknet2.draw_boxes(predictions, images[idx], class_colors)
        batch_predictions.append(predictions)
    darknet.free_batch_detections(batch_detections, batch_size)
    return images, batch_predictions


def convert2relative(image, bbox):
    """
    YOLO format use relative coordinates for annotation
    """
    x, y, w, h = bbox
    height, width, _ = image.shape
    return x/width, y/height, w/width, h/height


def save_annotations(name, image, detections, class_names):
    """
    Files saved with image_name.txt and relative coordinates
    """
    file_name = name.split(".")[:-1][0] + ".txt"
    with open(file_name, "w") as f:
        for label, confidence, bbox in detections:
            x, y, w, h = convert2relative(image, bbox)
            label = class_names.index(label)
            f.write("{} {:.4f} {:.4f} {:.4f} {:.4f} {:.4f}\n".format(label, x, y, w, h, float(confidence)))


def batch_detection_example():
    args = parser()
    check_arguments_errors(args)
    batch_size = 3
    random.seed(3)  # deterministic bbox colors
    network, class_names, class_colors = darknet.load_network(
        args.config_file,
        args.data_file,
        args.weights,
        batch_size=batch_size
    )
    image_names = ['data/horses.jpg', 'data/horses.jpg', 'data/eagle.jpg']
    images = [cv2.imread(image) for image in image_names]
    images, detections,  = batch_detection(network, images, class_names,
                                           class_colors, batch_size=batch_size)
    for name, image in zip(image_names, images):
        cv2.imwrite(name.replace("data/", ""), image)
    print(detections)

def draw_boxes_original_img(detections, image, colors):
    """
    This function returns the original input image with the detected bounding boxes
    We assume that the NN takes input images 416 x 416, which means coordinates of bounding boxes are expressed for images with that shape.
    Coordinates have indeed to be adjusted for images with a differente shape.
    Input:
    - detections: detection outputed by Yolo (e.g. from the function image_detection) 
    - image: image on which to perform the detection
    - colors: list of colors to be associated with classes
    
    Output:
    - image: image with bounding boxes
    """
    import cv2
    
    #extract height and width of the original image
    heigth, width = image.shape[:2]
    print("Original Size of the image:\n height {heigth}\n width {width}")
    for label, confidence, bbox in detections:
        left, top, right, bottom = darknet2.bbox2points(bbox)
        
        # rescale rectangle bounding box coordinates according to the size of the input image
        left = int(round((left/416) * width))  # xmin
        top = int(round((top/416) * heigth)) #ymin 
        right = int(round((right/416) * width)) #xmax
        bottom = int(round((bottom/416) * heigth)) #ymax
        
        cv2.rectangle(image, (left, top), (right, bottom), colors[label], 1)
        cv2.putText(image, "{} [{:.2f}]".format(label, float(confidence)),
                    (left, top + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    colors[label], 2)
    return image


def detectImg(ImgInput, ImgOutput):
    """
    This function takes an input image, performs detection on it and saves the output image with the bounding boxes.
    Input:
    	- ImgInput: path + filename of the image on which to perform the detection
    	- ImgOutput: path + filename of the output image with bounding boxes that is saved upon detection
    """

    random.seed(3)  # deterministic bbox colors
    network, class_names, class_colors = darknet2.load_network(
        "/code/darknet/cfg/yolo-obj-detect.cfg", 
        "/code/darknet/obj-config-files/obj.data", 
        "/code/darknet/flask-API/weights-detect/yolo-obj_last.weights",
        batch_size = 1 
    )

    images = load_images(ImgInput) 

    index = 0
    while True:
        # loop asking for new image paths if no list is given
        if True: 
            if index >= len(images):
                break
            image_name = images[index]
        else:
            image_name = input("Enter Image Path: ")
        prev_time = time.time()
        image, detections = image_detection(
            image_name, network, class_names, class_colors, 0.94 #args.thresh # replace thresh with 0.5
            )
        print(f"inside main print bbox (should be absolute respect to NN height=width = 416) {detections}")
        print(f"shape image {image.shape}")
        
        # Input image to perform the detection on
        originalImg = cv2.imread(image_name)
        # Draw boxes on the image
        detectedImg = draw_boxes_original_img(detections, originalImg, class_colors)
        # Save the output image in the path ImgOutput
        cv2.imwrite(ImgOutput, detectedImg)

        if False: # replace with true
            save_annotations(image_name, image, detections, class_names)
        darknet2.print_detections(detections, True ) # args.ext_output) # replace with True
        fps = int(1/(time.time() - prev_time))
        print("FPS: {}".format(fps))
        if not True: #args.dont_show: # replace with True
            cv2.imshow('Inference', image)
            if cv2.waitKey() & 0xFF == ord('q'):
                break
        index += 1
