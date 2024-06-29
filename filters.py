import numpy as np
from enum import Enum
from typing import Callable
import cv2 as cv


def simple_greyscale(image: np.ndarray):
    original_shape = image.shape
    image = (image.reshape(-1, 3)
             .mean(-1)
             .astype(np.uint8)
             .reshape(original_shape[0], original_shape[1]))
    return cv.cvtColor(image, cv.COLOR_GRAY2BGR)


# Allows for user selected vector of weights
# Binds pixel value to maximum of 255
def weighted_greyscale(image: np.ndarray, weights: np.ndarray):
    original_shape = image.shape
    image = (image.reshape(-1, 3)
             .dot(weights)
             .astype(np.uint8)
             .reshape(original_shape[0], original_shape[1]))
    image = np.where(image < 255, image, 255)
    return cv.cvtColor(image, cv.COLOR_GRAY2BGR)


def greyscale_from_channel(image: np.ndarray, channel: int):
    original_shape = image.shape
    image = image.reshape(-1, 3)[:, channel].reshape(original_shape[0], original_shape[1])
    return cv.cvtColor(image, cv.COLOR_GRAY2BGR)


def filter_or(image: np.ndarray, color: np.ndarray):
    return (image | color).astype(np.uint8)


def negate(image):
    return image ^ 255


def binarize(image: np.ndarray, threshold: int):
    image = simple_greyscale(image)
    return np.where(image > threshold, 255, 0).astype(np.uint8)


def blur(image: np.ndarray, size: np.ndarray):
    return cv.blur(image, tuple(size))


def gaussian_blur(image: np.ndarray, size: np.ndarray):
    size = size - (size % 2 == 0)
    return cv.GaussianBlur(image, tuple(size), 0)


def canny(image: np.ndarray, thresholds: list):
    image = cv.Canny(cv.cvtColor(image, cv.COLOR_BGR2GRAY), *thresholds)
    return cv.cvtColor(image, cv.COLOR_GRAY2BGR)


def embossed_edges(image):
    kernel = np.array([[0, -3, -3],
                       [3, 0, -3],
                       [3, 3, 0]])
    img_emboss = cv.filter2D(image, -1, kernel=kernel)
    return img_emboss


def pencil_sketch(image):
    return cv.cvtColor(cv.pencilSketch(image)[0], cv.COLOR_GRAY2BGR)


def test_numpy():
    print('comecou')
    # image = cv.imread("image.jpg")
    # resized = cv.resize(image, (0, 0), fx=0.1, fy=0.1)
    # sticker = cv.imread('sticker.png', cv.IMREAD_UNCHANGED)
    # resized_sticker = cv.resize(sticker, (0, 0), fx=0.1, fy=0.1)
    # cv.imshow('teste', overlay(resized, resized_sticker))
    # cv.waitKey(0)


class FilterParameterType(Enum):
    NONE = 0
    INT_VALUE = 1
    BGR_VALUE = 2
    BGR_FLOAT_VALUE = 3
    INT_TUPLE_2 = 4


class ImageFilter:
    def __init__(self,
                 display_name: str,
                 filter_id: int,
                 filter_function: Callable,
                 filter_parameter_type: FilterParameterType,
                 filter_parameter_name: str = "",
                 filter_parameter_value=None,
                 min_max_param_value: tuple = None):
        self.display_name = display_name
        self.filter_id = filter_id
        self.filter_function = filter_function
        self.filter_parameter_type = filter_parameter_type
        self.filter_parameter_name = filter_parameter_name
        self.filter_parameter_value = filter_parameter_value
        self.min_max_param_value = min_max_param_value

    def apply(self, image):
        if self.filter_parameter_value is not None:
            return self.filter_function(image, self.filter_parameter_value)
        else:
            return self.filter_function(image)

    def update_parameter_value(self, value, index: int | None):
        if self.filter_parameter_type == FilterParameterType.INT_VALUE:
            self.filter_parameter_value = value
        else:
            self.filter_parameter_value[index] = value

    def __repr__(self):
        return self.display_name

    def __str__(self):
        return self.display_name


def get_image_filter_list():
    # Filter_id must increase linearly in the same order as the filters
    return [
        ImageFilter("Simple Greyscale", 0, simple_greyscale, FilterParameterType.NONE),
        ImageFilter("Weighted Greyscale", 1, weighted_greyscale, FilterParameterType.BGR_FLOAT_VALUE, "Weights", np.array([0.07, 0.71, 0.21]), (0.0, 1.0)),
        ImageFilter("Greyscale from channel", 2, greyscale_from_channel, FilterParameterType.INT_VALUE, "Channel", 0, (0, 2)),
        ImageFilter("OR Filter", 3, filter_or, FilterParameterType.BGR_VALUE, "Filter Color", np.array([255, 0, 255]), (0, 255)),
        ImageFilter("Negate", 4, negate, FilterParameterType.NONE),
        ImageFilter("Binarize", 5, binarize, FilterParameterType.INT_VALUE, "Threshold", 127, (0, 255)),
        ImageFilter("Blur", 6, blur, FilterParameterType.INT_TUPLE_2, "Width / Height", np.array([15, 15]), (1, 200)),
        ImageFilter("Canny", 7, canny, FilterParameterType.INT_TUPLE_2, "Lower Threshold / Upper Threshold", [50, 150], (1, 300)),
        ImageFilter("Embossed Edges", 8, embossed_edges, FilterParameterType.NONE),
        ImageFilter("Gaussian Blur", 9, gaussian_blur, FilterParameterType.INT_TUPLE_2, "Width / Height", np.array([15, 15]), (1, 200)),
        ImageFilter("Pencil Sketch", 10, pencil_sketch, FilterParameterType.NONE)
    ]


def get_image_filter_dict():
    return {filter_.display_name: filter_ for filter_ in get_image_filter_list()}
