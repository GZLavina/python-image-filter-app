import sys
import cv2 as cv
from PyQt5 import QtWidgets, QtCore, QtGui
from filters import *

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 800

FILTER_COMPOSITION = 'Filter compostion: '
NO_FILTERS_SELECTED = FILTER_COMPOSITION + 'no filters selected.'

SLIDER_FLOAT_SCALING_FACTOR = 500


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Initializing QThread that deals with camera feed (also shows images)
        filter_list = get_image_filter_list()
        self.Worker = Worker(filter_list)
        self.Worker.start()
        self.Worker.ImageUpdate.connect(self.image_update_slot)

        # Main Horizontal Layout
        # Includes all hidden filter options
        self.main_horizontal_layout = QtWidgets.QHBoxLayout()

        # Main vertical layout
        self.main_vertical_layout = QtWidgets.QVBoxLayout()

        # Horizontal layout for filter buttons
        self.filter_buttons_layout = QtWidgets.QHBoxLayout()
        # This list keeps track of which filter parameters layout each button should show
        self.filter_button_to_param_layout_list = []
        for filter_ in filter_list:
            self.filter_button = QtWidgets.QPushButton(filter_.display_name)
            self.filter_button.clicked.connect(self.filter_button_handler)
            self.filter_buttons_layout.addWidget(self.filter_button)
            self.filter_button_to_param_layout_list.append(ButtonToParamLayout(self.filter_button, None, filter_))
        self.main_vertical_layout.addLayout(self.filter_buttons_layout)

        # Adding camera feed to main layout
        self.FeedLabel = QtWidgets.QLabel()
        self.main_vertical_layout.addWidget(self.FeedLabel)

        # Adding filter composition description
        self.filter_composition_label = QtWidgets.QLabel()
        self.filter_composition_label.setText(NO_FILTERS_SELECTED)
        self.main_vertical_layout.addWidget(self.filter_composition_label)

        # Adding "stop camera" button to main layout
        self.stop_cam_button = QtWidgets.QPushButton('Stop Camera')
        self.stop_cam_button.clicked.connect(self.cancel_feed)
        self.main_vertical_layout.addWidget(self.stop_cam_button)

        # Finished configuration of main vertical layout
        self.main_horizontal_layout.addLayout(self.main_vertical_layout)

        # TODO - Add all hidden filter parameter widgets
        self.filter_widget_layouts = []
        # This list keeps track of which filter each widget is changing
        self.filter_parameter_widgets = []
        for index, filter_ in enumerate(filter_list):
            if filter_.filter_parameter_type == FilterParameterType.INT_VALUE:
                self.filter_param_layout = self.add_filter_param_details(filter_)
                self.slider = QtWidgets.QSlider()
                self.slider.setRange(*filter_.min_max_param_value)
                self.slider.setValue(filter_.filter_parameter_value)
                self.slider.valueChanged.connect(self.filter_slider_changed)
                self.set_slider_color(self.slider, None)
                self.filter_parameter_widgets.append(FilterParameterWidget(filter_, self.slider, None))
                self.filter_param_layout.addWidget(self.slider, alignment=QtCore.Qt.AlignHCenter)
                self.finalize_filter_param_widget_setup(self.filter_param_layout, index)
            elif filter_.filter_parameter_type == FilterParameterType.BGR_VALUE:
                self.filter_param_layout = self.add_filter_param_details(filter_)
                self.slider_list = [QtWidgets.QSlider(), QtWidgets.QSlider(), QtWidgets.QSlider()]
                self.sliders_layout = QtWidgets.QHBoxLayout()
                for slider_index, slider_ in enumerate(self.slider_list):
                    slider_.setRange(*filter_.min_max_param_value)
                    slider_.setValue(filter_.filter_parameter_value[slider_index])
                    slider_.valueChanged.connect(self.filter_slider_changed)
                    self.set_slider_color(slider_, slider_index)
                    self.filter_parameter_widgets.append(FilterParameterWidget(filter_, slider_, slider_index))
                    self.sliders_layout.addWidget(slider_)
                self.filter_param_layout.addLayout(self.sliders_layout)
                self.finalize_filter_param_widget_setup(self.filter_param_layout, index)
            elif filter_.filter_parameter_type == FilterParameterType.BGR_FLOAT_VALUE:
                self.filter_param_layout = self.add_filter_param_details(filter_)
                self.slider_list = [QtWidgets.QSlider(), QtWidgets.QSlider(), QtWidgets.QSlider()]
                self.sliders_layout = QtWidgets.QHBoxLayout()
                for slider_index, slider_ in enumerate(self.slider_list):
                    slider_.setRange(*[int(value * SLIDER_FLOAT_SCALING_FACTOR) for value in filter_.min_max_param_value])
                    slider_.setValue(int(filter_.filter_parameter_value[slider_index] * SLIDER_FLOAT_SCALING_FACTOR))
                    slider_.valueChanged.connect(self.filter_slider_changed)
                    self.set_slider_color(slider_, slider_index)
                    self.filter_parameter_widgets.append(FilterParameterWidget(filter_, slider_, slider_index))
                    self.sliders_layout.addWidget(slider_)
                self.filter_param_layout.addLayout(self.sliders_layout)
                self.finalize_filter_param_widget_setup(self.filter_param_layout, index)

        # Finished configuration of main horizontal layout
        self.setLayout(self.main_horizontal_layout)

        self.filter_dictionary = get_image_filter_dict()

    # Function called by ImageUpdate to refresh camera frame
    def image_update_slot(self, image):
        self.FeedLabel.setPixmap(QtGui.QPixmap.fromImage(image))

    def add_filter_param_details(self, filter_):
        filter_param_layout = QtWidgets.QVBoxLayout()
        filter_name = QtWidgets.QLabel()
        filter_name.setText(filter_.display_name)
        filter_param_layout.addWidget(filter_name, alignment=QtCore.Qt.AlignHCenter)

        filter_param_name = QtWidgets.QLabel()
        filter_param_name.setText(filter_.filter_parameter_name)
        filter_param_layout.addWidget(filter_param_name, alignment=QtCore.Qt.AlignHCenter)
        return filter_param_layout

    def finalize_filter_param_widget_setup(self, layout, index):
        self.recursive_show_hide_widgets(layout, True)
        self.filter_button_to_param_layout_list[index].layout = self.filter_param_layout
        self.filter_widget_layouts.append(layout)
        self.main_horizontal_layout.addLayout(layout)

    def filter_slider_changed(self, i):
        for widget in self.filter_parameter_widgets:
            if widget.widget == self.sender():
                if widget.filter_.filter_parameter_type == FilterParameterType.BGR_FLOAT_VALUE:
                    i = float(i) / float(SLIDER_FLOAT_SCALING_FACTOR)
                widget.filter_.update_parameter_value(i, widget.param_index)

    def filter_button_handler(self):
        for button_and_layout in self.filter_button_to_param_layout_list:
            if button_and_layout.button == self.sender():
                filter_composition_text = self.Worker.activate_or_deactivate_filter(button_and_layout.filter_.filter_id)
                self.filter_composition_label.setText(filter_composition_text)
                if button_and_layout.filter_.filter_parameter_type != FilterParameterType.NONE:
                    button_and_layout.hidden = not button_and_layout.hidden
                    self.recursive_show_hide_widgets(button_and_layout.layout, button_and_layout.hidden)

    # PyQt does not have a setHidden function for layouts
    # This functions looks recursively for widgets within layouts that have to be hidden
    def recursive_show_hide_widgets(self, item, should_hide: bool):
        if isinstance(item, QtWidgets.QHBoxLayout) or isinstance(item, QtWidgets.QVBoxLayout):
            for i in range(item.count()):
                child_item = item.itemAt(i).layout()
                # QLayout.itemAt returns an instance of QLayoutItem
                # QLayoutItem can manage either a widget or a layout
                # If QLayoutItem.layout() returns None, it means it manages a widget
                if child_item is None:
                    child_item = item.itemAt(i).widget()
                self.recursive_show_hide_widgets(child_item, should_hide)
        else:
            item.setHidden(should_hide)

    def set_slider_color(self, slider, index):
        style_str = "::handle{{background: {}}}"
        if index is None:
            slider.setStyleSheet(style_str.format("gray"))
        elif index == 0:
            slider.setStyleSheet(style_str.format("blue"))
        elif index == 1:
            slider.setStyleSheet(style_str.format("green"))
        elif index == 2:
            slider.setStyleSheet(style_str.format("red"))

    # Function called by "Stop Camera" button
    def cancel_feed(self):
        self.Worker.stop()


class Worker(QtCore.QThread):
    ImageUpdate = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, available_filters: list):
        super().__init__()
        self.ThreadActive = False
        self.available_filters = available_filters
        self.active_filters_in_order = []

    def run(self):
        self.ThreadActive = True
        capture = cv.VideoCapture(0)
        while self.ThreadActive:
            ret, frame = capture.read()
            if ret:
                for active_filter in self.active_filters_in_order:
                    frame = active_filter.apply(frame)
                frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                converted_and_scaled = (QtGui.QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QtGui.QImage.Format_RGB888)
                                        .scaled(640, 480, QtCore.Qt.KeepAspectRatio))
                self.ImageUpdate.emit(converted_and_scaled)
        capture.release()

    def activate_or_deactivate_filter(self, param_filter_id):
        filter_index = None
        for index, active_filter in enumerate(self.active_filters_in_order):
            if active_filter.filter_id == param_filter_id:
                filter_index = index

        if filter_index is not None:
            self.active_filters_in_order.pop(filter_index)
        else:
            # Add new filter at the end so that it will be processed last
            self.active_filters_in_order.append(self.available_filters[param_filter_id])

        if len(self.active_filters_in_order) > 0:
            return FILTER_COMPOSITION + ' > '.join([str(filter_) for filter_ in self.active_filters_in_order])
        else:
            return NO_FILTERS_SELECTED

    def stop(self):
        self.ThreadActive = False
        self.quit()


# Class used to keep track of which filter a parameter adjustment widget belongs to
class FilterParameterWidget:
    def __init__(self, filter_: ImageFilter, widget: QtCore.QObject, param_index: int | None):
        self.filter_ = filter_
        self.widget = widget
        # Property used when the widget used points to a specific RGB channel
        self.param_index = param_index


# Class used to keep track of which filter parameter layout a button should show when clicked
class ButtonToParamLayout:
    def __init__(self, button, layout: QtWidgets.QHBoxLayout | QtWidgets.QVBoxLayout, filter_: ImageFilter):
        self.button = button
        self.layout = layout
        self.layout_widgets = []
        self.filter_ = filter_
        self.hidden = True


if __name__ == '__main__':
    # test_numpy()
    App = QtWidgets.QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())

