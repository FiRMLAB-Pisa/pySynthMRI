import logging
import os
from datetime import datetime
from enum import Enum
from pathlib import Path

import nibabel as nib
import numpy as np
import pydicom
from pydicom.uid import generate_uid

from model.psExceptions import NotLoadedMapError, NotSelectedMapError
from model.psFileType import psFileType

log = logging.getLogger(__name__)


# log.setLevel(LOGGING_LVL)

class Orientation(Enum):
    AXIAL = 1
    CORONAL = 2
    SAGITTAL = 3


class Interpolation(Enum):
    NONE = 1
    LINEAR = 2
    BICUBIC = 3
    NN = 4


class Colormap(object):
    COLORMAP_HOT = ("HOT", 11)
    COLORMAP_BONE = ("BONE", 1)
    COLORMAP_JET = ("JET", 2)
    COLORMAP_WINTER = ("WINTER", 3)
    COLORMAP_HSV = ("HSV", 9)
    COLOR_LIST = ["HOT", "BONE", "JET", "WINTER", "HSV"]

    # def __iter__(self):
    #     for attr, value in self.__dict__.iteritems():
    #         yield attr, value

class MRIImage:
    np_matrix = None
    np_matrix_3d = None
    # image orientation, default axial
    _orientation = None

    map_type = ""
    file_type = ""  # niftii, dicom

    # window scale
    maxWindowWidth = 2 ** 18 - 1  # 4000
    maxWindowCenter = 2 ** 18 - 1  # 4000
    minWindowWidth = -7000
    minWindowCenter = -7000
    _window_width = -1
    _window_center = -1
    slices_num = {Orientation.AXIAL: -1,
                  Orientation.SAGITTAL: -1,
                  Orientation.CORONAL: -1}
    total_slices_num = {Orientation.AXIAL: -1,
                        Orientation.SAGITTAL: -1,
                        Orientation.CORONAL: -1}
    _m_max = None
    _m_min = None

    def set_init_slices_num(self, qmap_ref=None):
        if qmap_ref is not None:
            self.slices_num = qmap_ref.get_slices_num(all_orientation=True)
            self.total_slices_num = qmap_ref.get_total_slices_num(all_orientation=True)
            return
        # set init orientation and sliceposition

        self.slices_num[Orientation.AXIAL] = round(self.np_matrix.shape[2] / 2) - 1
        self.slices_num[Orientation.SAGITTAL] = round(self.np_matrix.shape[0] / 2) - 1
        self.slices_num[Orientation.CORONAL] = round(self.np_matrix.shape[1] / 2) - 1

        self.total_slices_num[Orientation.AXIAL] = self.np_matrix.shape[2]
        self.total_slices_num[Orientation.SAGITTAL] = self.np_matrix.shape[0]
        self.total_slices_num[Orientation.CORONAL] = self.np_matrix.shape[1]

    def set_map_type(self, map_type: str):
        self.map_type = map_type

    def get_map_type(self):
        return self.map_type

    def set_matrix(self, np_matrix):
        self.np_matrix = np_matrix

    def update_min_max(self):
        self._m_max = self.np_matrix.max()
        self._m_min = self.np_matrix.min()

    def get_max_value(self):
        return self._m_max

    def get_min_value(self):
        return self._m_min

    def get_matrix(self, dim):

        if self.np_matrix is None:
            # log.debug("Requesting None image")
            return None
        if self.np_matrix.ndim == 2:
            # smap case is never computed in 3d till save
            return self.np_matrix

        np_matrix_3d = self.np_matrix

        if dim == 2:
            if self._orientation == Orientation.AXIAL:
                return np.fliplr(np.rot90(np_matrix_3d[:, :, self.slices_num[Orientation.AXIAL]]))
            elif self._orientation == Orientation.SAGITTAL:
                return np.fliplr(np.rot90(np_matrix_3d[self.slices_num[Orientation.SAGITTAL], :, :]))
            elif self._orientation == Orientation.CORONAL:
                return np.fliplr(np.rot90(np_matrix_3d[:, -self.slices_num[Orientation.CORONAL], :]))
        else:
            return np_matrix_3d

    def get_mask(self, threshold=0.01, dims=2):
        return self._qmaps[list(self._qmaps.keys())[0]].get_matrix(dims) > threshold

    def get_matrix_shape(self):
        return self.np_matrix.shape

    def set_window_width(self, window_width):
        self._window_width = window_width

    def set_window_center(self, window_center):
        self._window_center = window_center

    def get_window_width(self):
        if self._window_width == -1:
            # self.init_window()
            raise ValueError
        return self._window_width

    def set_window_width(self, window_width):
        self._window_width = window_width

    def set_window_center(self, window_center):
        self._window_center = window_center

    def set_default_window_width(self, default_window_width):
        self._default_window_width = default_window_width

    def set_default_window_center(self, default_window_center):
        self._default_window_center = default_window_center

    def get_window_center(self):
        if self._window_center == -1:
            #     self.init_window()
            raise ValueError
        return self._window_center

    def reset_widow_scale(self):
        """
        reset ww, wc to config values if present, otherwise compute them using min max
        """
        if self.np_matrix is None:
            raise NotSelectedMapError("Synthetic image not selected!")

        max_val = np.abs(self.np_matrix).max()
        if self._default_window_center is not None:
            self._window_center = self._default_window_center
        else:
            self._window_center = np.floor(max_val / 2)
        if self._default_window_width is not None:
            self._window_width = self._default_window_width
        else:
            self._window_width = np.floor(max_val)

    def add_delta_window_width(self, delta):
        if self.np_matrix is None:
            raise NotSelectedMapError("Synthetic image not selected!")
        self._window_width -= delta
        if self._window_width >= self.maxWindowWidth:
            self._window_width = self.maxWindowWidth
        elif self._window_width <= self.minWindowWidth:
            self._window_width = self.minWindowWidth
        # log.debug("ww: {}".format(self._window_width))
        return self._window_width

    def add_delta_window_center(self, delta):
        if self.np_matrix is None:
            raise NotSelectedMapError("Synthetic image not selected!")
        self._window_center -= delta
        if self._window_center >= self.maxWindowCenter:
            self._window_center = self.maxWindowCenter
        elif self._window_center <= self.minWindowCenter:
            self._window_center = self.minWindowCenter
        # log.debug("wc: {}".format(self._window_center))
        return self._window_center

    def set_orientation(self, orientation):
        self._orientation = orientation

    def get_orientation(self):
        return self._orientation

    def get_parameter_slider(self, param_k):
        return self._parameters[param_k]["slider"]

    def set_slice_num(self, slices_num, coordinate=None):
        if slices_num < 0:
            slices_num = self.get_total_slices_num() - 1
        elif slices_num >= self.get_total_slices_num():
            slices_num = 0
        if coordinate is None:
            self.slices_num[self._orientation] = slices_num
        else:
            self.slices_num[coordinate] = slices_num
        return slices_num

    def set_next_slice(self):
        return self.set_slice_num(self.get_slices_num() + 1)

    def set_previous_slice(self):
        return self.set_slice_num(self.get_slices_num() - 1)

    def get_slices_num(self, all_orientation=False):
        if all_orientation:
            return self.slices_num
        else:
            return self.slices_num[self._orientation]

    def set_total_slice_num(self, total_slices_num, struct=None):
        if struct is not None:
            self.total_slices_num = total_slices_num

    def get_total_slices_num(self, all_orientation=False):
        if all_orientation:
            return self.total_slices_num
        else:
            return self.total_slices_num[self._orientation]

    def is_loaded(self):
        return self.np_matrix is not None


class Qmap(MRIImage):
    def __init__(self, map_type: str, path=None, is_loaded=False):
        super(Qmap, self).__init__()
        self.set_map_type(map_type)
        self.path = path
        self.is_loaded = is_loaded
        self.header = None
        self.original_template = None
        self.slice_spacing = 0.
        self._colormap = Colormap.COLORMAP_HOT
        self._inverted = False

    def load_from_dicom(self):
        path = Path(self.path)
        qmap_type = self.map_type
        # load the DICOM files
        # log.debug('Loading dicom: {}'.format(wildcard_path))
        file_list = [str(pp) for pp in path.glob("**/*")]
        files = []
        for fname in file_list:
            try:
                dicom_file = pydicom.dcmread(fname)
                files.append(dicom_file)
            except Exception as e:
                print(e)
                e.dicom_map_type = path
                raise e

        log.info("Loading {} files for {} qmap...".format(len(files), qmap_type))
        # ensure they are in the correct order
        slices = sorted(files, key=lambda s: s.SliceLocation)

        # create 3D array
        img_shape = list(slices[0].pixel_array.shape)
        slice_spacing = slices[0].PixelSpacing
        dcm_header = slices[0]
        img_shape.append(len(slices))
        self.np_matrix = np.zeros(img_shape)

        # fill 3D array with the images from the files
        for i, s in enumerate(slices):
            self.np_matrix[:, :, i] = np.rot90(np.flipud(s.pixel_array)).copy()

        # set init orientation and sliceposition
        self.set_init_slices_num()
        self.file_type = psFileType.DICOM
        self.original_template = slices
        self.update_min_max()
        self.slice_spacing = slice_spacing

    def check_orientation(self, niftii, img):
        """
        Check the NIfTI orientation, and flip to  'RPS' if needed.
        :param niftii: NIfTI file
        :param img: matrix map
        :return: matrix after flipping
        """
        x, y, z = nib.aff2axcodes(niftii.affine)
        # "RPS": classic, "RAS: neurological
        if x != 'R':
            ct_arr = nib.orientations.flip_axis(img, axis=0)
        if y != 'A':
            ct_arr = nib.orientations.flip_axis(img, axis=1)
        if z != 'S':
            ct_arr = nib.orientations.flip_axis(img, axis=2)
        return img

    def load_from_niftii(self):
        path = self.path
        qmap_type = self.map_type
        log.info("Loading file for {} qmap...".format(qmap_type))
        niftii_file = nib.load(path)
        self.np_matrix = niftii_file.get_fdata()
        # self.np_matrix = self.check_orientation(niftii_file, self.np_matrix)
        self.header = niftii_file.header
        self.file_type = psFileType.NIFTII
        self.set_init_slices_num()
        self.update_min_max()
        self.slice_spacing = self.header['pixdim'][1:3]

    def get_dicom(self):
        if self.file_type == psFileType.DICOM:
            return self.original_template
        elif self.file_type == psFileType.NIFTII:
            # need conversion
            slices = []
            # if getattr(sys, 'frozen', False):
            #     # for executable
            #     template_path = os.path.join(sys._MEIPASS, 'resources', 'template', 'dicom.dcm')
            #     print(template_path)
            # else:
            template_path = os.path.join('resources', 'template', 'dicom.dcm')

            dicom_file = pydicom.dcmread(template_path)
            for i in range(self.np_matrix.shape[2]):
                arr = self.np_matrix[:, :, i].astype('uint16')
                dicom_file.Rows = arr.shape[0]
                dicom_file.Columns = arr.shape[1]
                dicom_file.PhotometricInterpretation = "MONOCHROME2"
                dicom_file.SamplesPerPixel = 1
                dicom_file.BitsStored = 16
                dicom_file.BitsAllocated = 16
                dicom_file.HighBit = 15
                dicom_file.InstanceNumber = i
                dicom_file.InStackPositionNumber = i
                dicom_file.PixelRepresentation = 1
                dicom_file.SeriesDescription = "MODIFIED DICOM"
                # dicom_file.SOPClassUID = pydicom._storage_sopclass_uids.MRImageStorage
                dicom_file.SOPInstanceUID = pydicom.uid.generate_uid()
                dicom_file.PixelData = arr.tobytes()
                slices.append(dicom_file)
            return slices

    def set_colormap(self, colormap):
        self._colormap = colormap

    def get_colormap(self):
        return self._colormap

    def set_inverted(self, inverted):
        self._inverted = inverted

    def get_inverted(self):
        return self._inverted


class Smap(MRIImage):
    DICOM_SCALE = 2 ** 16 - 1

    def __init__(self, qmaps):
        super(Smap, self).__init__()
        self._qmaps = qmaps
        self._qmaps_needed = []
        self._equation = ""
        self._parameters = dict()
        self._title = ""
        self._equation_string = ""
        self._orientation_labels_flag = True
        self._vertical_parameter = None
        self._horizontal_parameter = None
        self._series_number = None
        self._header = dict()

    def set_map_type(self, map_type):
        super(Smap, self).set_map_type(map_type)

    def set_equation(self, equation):
        self._equation = equation

    def set_equation_string(self, equation_string):
        self._equation_string = equation_string

    def get_equation_string(self):
        return self._equation_string

    def set_qmaps_needed(self, qmaps_needed):
        self._qmaps_needed = qmaps_needed

    def set_scanner_parameters(self, parameters):
        self._parameters = parameters

    def set_default_scanner_parameters(self):
        for k in self._parameters:
            self._parameters[k]["value"] = self._parameters[k]["default"]
            self._parameters[k]["slider"].sliderQ.setValue(self._parameters[k]["value"])

    def get_scanner_parameters(self):
        return self._parameters

    def set_title(self, title):
        self._title = title

    def get_title(self):
        return self._title

    def get_header_tag(self, tag):
        try:
            return self._header[tag]
        except KeyError:
            return None

    def set_header_tag(self, tag, value):
        self._header[tag] = value

    def get_orientation_labels_flag(self):
        return self._orientation_labels_flag

    def set_orientation_labels_flag(self, orientation_labels_flag):
        self._orientation_labels_flag = orientation_labels_flag

    def set_series_number(self, series_number):
        self._series_number = series_number

    def get_series_number(self):
        return self._series_number

    def get_missing_qmaps(self):
        missing_qmaps = []
        for qmap in self._qmaps_needed:
            try:
                if not self._qmaps[qmap].is_loaded:
                    missing_qmaps.append(qmap)
            except KeyError:
                missing_qmaps.append(qmap)
        return missing_qmaps

    def set_parameter(self, param, direction):
        if direction == "v":
            if self._horizontal_parameter == param:
                self._horizontal_parameter = None
            self._vertical_parameter = param
        elif direction == "h":
            if self._vertical_parameter == param:
                self._vertical_parameter = None
            self._horizontal_parameter = param

    def get_parameter(self, direction):
        if direction == "v":
            return self._vertical_parameter
        elif direction == "h":
            return self._horizontal_parameter

    def get_parameter_value(self, direction):
        if direction == "h":
            if self._horizontal_parameter is None:
                return None
            return self._parameters[self._horizontal_parameter]["value"]
        elif direction == "v":
            if self._vertical_parameter is None:
                return None
            return self._parameters[self._vertical_parameter]["value"]

    def set_parameter_value(self, param_value, direction):
        if direction == "v":
            if param_value < self._parameters[self._vertical_parameter]["min"]:
                param_value = self._parameters[self._vertical_parameter]["min"]
            elif param_value > self._parameters[self._vertical_parameter]["max"]:
                param_value = self._parameters[self._vertical_parameter]["max"]
            self._parameters[self._vertical_parameter]["value"] = param_value
            return param_value
        elif direction == "h":
            if param_value < self._parameters[self._horizontal_parameter]["min"]:
                param_value = self._parameters[self._horizontal_parameter]["min"]
            elif param_value > self._parameters[self._horizontal_parameter]["max"]:
                param_value = self._parameters[self._horizontal_parameter]["max"]
            self._parameters[self._horizontal_parameter]["value"] = param_value
            return param_value

    def recompute_smap(self, dims=2):
        # eval equation
        # log.debug(self._equation)

        # check if all needed quantitative maps are loaded
        if self.get_missing_qmaps():
            raise NotLoadedMapError("{} map not laoded!".format(', '.join(self.get_missing_qmaps())))
        if not self._equation:
            raise NotSelectedMapError("Synthetic image not selected!")

        img = eval(self._equation)

        img = np.nan_to_num(img)
        # automask TODO
        mask = self.get_mask(dims=dims)
        img[~mask] = 0

        # get scaling
        img = np.abs(img)
        maxval = img.max()
        minval = img.min()

        scaling = self.DICOM_SCALE / (maxval - minval) * 0.1
        offset = minval

        if dims == 3:
            self.np_matrix_3d = (scaling * (img - offset)).astype(np.float32)
        else:
            self.np_matrix = (scaling * (img - offset)).astype(np.float32)

    def size(self):
        return self.get_matrix_shape()

    def get_series_description(self):
        scanner_params = self.get_scanner_parameters()
        series_description = self.get_map_type()
        for sp in scanner_params:
            series_description = series_description + " " + sp + ":" + str(scanner_params[sp]["value"])
        return series_description

    def save_niftii(self, path):
        self.recompute_smap(dims=3)
        tmp = self.np_matrix_3d.astype(np.float32)
        # tmp = np.flip(np.flip(tmp.transpose(), axis=0), axis=1)

        niftii = nib.Nifti1Image(tmp, np.eye(4))
        self.import_header_from_qmap(niftii.header, psFileType.NIFTII)
        nib.save(niftii, path)
        log.debug("save_niftii: saving niftii on {}".format(path))

    def save_dicom(self, save_dir_path):
        log.debug("save_dicom")

        self.recompute_smap(dims=3)
        # tmp = self.np_matrix_3d.astype(np.short)
        tmp = np.zeros(self.np_matrix_3d.shape, dtype=np.short)
        for i in range(tmp.shape[2]):
            # reorder each 2d image
            tmp[:, :, i] = np.flipud(np.rot90(self.np_matrix_3d[:, :, i], 3)).astype(np.short)

        if not os.path.exists(save_dir_path):
            os.mkdir(save_dir_path)

        template = self.get_dicom_template_from_qmap()

        # NB: This is ok for axial images.
        slice_spacing = self._qmaps[list(self._qmaps.keys())[0]].slice_spacing[1]
        series_uid = generate_uid()
        # equal for many different synthesized images (use entropy source for generate UID)
        # based on study id, patient name
        study_uid = generate_uid(entropy_srcs=[str(self._header["PatientID"]), str(self._header["StudyID"])])

        sym_central_location = 0.
        for s in range(len(template)):
            # add SERIES NUMBER, UID, OTHER INFO
            log.info(str(self._header))
            for tag in self._header:
                template[s][tag].value = self._header[tag]

            s_relative_idx = s - len(template) / 2.
            template[s].PixelData = tmp[:, :, s].tobytes()
            save_path = os.path.join(save_dir_path, "series_" + str(s + 1) + ".dcm")
            template[s].WindowCenter = self.get_window_center()
            template[s].WindowWidth = self.get_window_width()
            # change series description
            template[s].SeriesDescription = self.get_series_description()
            # location centered on the central slice
            sym_location = (slice_spacing / 2.) + s_relative_idx * slice_spacing
            template[s].ImagePositionPatient = [0., 0., sym_location]
            template[s].SliceLocation = sym_location

            # add Parameters informations
            if "TE" in self._parameters:
                template[s].EchoTime = self._parameters["TE"]["value"]
            if "TI" in self._parameters:
                template[s].InversionTime = self._parameters["TI"]["value"]
            if "TR" in self._parameters:
                template[s].RepetitionTime = self._parameters["TR"]["value"]

            if template[s].PatientName == "":
                template[s].PatientName = "ANONYMOUS^ANONYMOUS"

            if template[s].PatientBirthDate == "":
                template[s].PatientBirthDate = "19000101"

            if template[s].StudyDescription == "":
                template[s].StudyDescription = "Synthesized Image [PySynthMRI]"

            if template[s].StudyDate == "":
                template[s].StudyDate = datetime.today().strftime('%Y%m%d')

            template[s].InstanceNumber = s
            template[s].ProtocolName = "PySynthMRI"

            # Generate UID
            template[s].SOPInstanceUID = generate_uid()
            template[s].SeriesInstanceUID = series_uid
            template[s].StudyInstanceUID = study_uid
            template[s].save_as(save_path)

    def import_header_from_qmap(self, header, file_type):
        qmap = self._qmaps[list(self._qmaps.keys())[0]]
        if file_type == psFileType.NIFTII:
            if qmap.file_type == file_type:
                header["pixdim"] = qmap.header["pixdim"]

    def get_dicom_template_from_qmap(self):
        qmap = self._qmaps[list(self._qmaps.keys())[0]]
        return qmap.get_dicom()
