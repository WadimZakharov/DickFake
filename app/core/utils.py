import math
from typing import Tuple, Union

import cv2
import numpy as np
from numpy.linalg import norm
from app.datalayer.schemas import Eyes


def normalized_to_pixel_coordinates(
    normalized_x: float, normalized_y: float, image_width: int,
    image_height: int) -> Union[None, Tuple[int, int]]:
    """Converts normalized value pair to pixel coordinates."""

    if not (_is_valid_normalized_value(normalized_x) and
        _is_valid_normalized_value(normalized_y)):
    # TODO: Draw coordinates even if it's outside of the image bounds.
        return None
    x_px = min(math.floor(normalized_x * image_width), image_width - 1)
    y_px = min(math.floor(normalized_y * image_height), image_height - 1)
    return x_px, y_px

def _is_valid_normalized_value(value: float) -> bool:
    return (value > 0 or math.isclose(0, value)) and (value < 1 or
                                    math.isclose(1, value))

def get_theta(v, w):
    sign = np.sign(v[0]*w[1] - w[0]*v[1])
    return sign*np.arccos(v.dot(w)/(norm(v)*norm(w))) * 57.29577951308

def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    image_center = int(image_center[0]), int(image_center[1])
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1],
                            flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255))
    return result, np.array(image_center)


def rotate_point(point, center, angle):
    ox, oy = center
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) + math.sin(angle) * (py - oy)
    qy = oy - math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return np.array([qx, qy])


def overlay_image_alpha(img, img_overlay, x, y, alpha_mask):
    """Overlay `img_overlay` onto `img` at (x, y) and blend using `alpha_mask`.

    `alpha_mask` must have same HxW as `img_overlay` and values in range [0, 1].
    """
    # Image ranges
    y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
    x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])

    # Overlay ranges
    y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
    x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)

    # Exit if nothing to do
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
        return

    # Blend overlay within the determined ranges
    img_crop = img[y1:y2, x1:x2]
    img_overlay_crop = img_overlay[y1o:y2o, x1o:x2o]
    alpha = alpha_mask[y1o:y2o, x1o:x2o, np.newaxis]
    alpha_inv = 1.0 - alpha

    img_crop[:] = alpha * img_overlay_crop + alpha_inv * img_crop


def preprocess_dick(dick: np.array, back_eyes: Eyes, front_eyes: Eyes):

    front_height, front_width, _ = dick.shape
    back_eye_vector = back_eyes.right - back_eyes.left
    front_eye_vector = front_eyes.right - front_eyes.left

    angle_of_rotation = get_theta(back_eye_vector, front_eye_vector)
    rotated_dick, image_center = rotate_image(dick, angle_of_rotation)

    dist_back = math.dist(back_eyes.left, back_eyes.right)
    dist_front = math.dist(front_eyes.left, front_eyes.right)
    resize_coef = dist_back / dist_front

    new_width = round(front_width * resize_coef)
    new_height = round(front_height * resize_coef)
    resize_rotated_dick = cv2.resize(rotated_dick, (new_width, new_height))

    rotate_left = rotate_point(front_eyes.left*resize_coef,
                               image_center*resize_coef,
                               angle_of_rotation/57.29577951308)

    rotate_right = rotate_point(front_eyes.right*resize_coef, 
                                image_center*resize_coef, 
                                angle_of_rotation/57.29577951308)

    rotate_eyes = Eyes(np.around(rotate_left).astype(int),
                       np.around(rotate_right).astype(int))

    return resize_rotated_dick, rotate_eyes
