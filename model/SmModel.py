import glob
import os
from enum import Enum

import nibabel as nib
import numpy as np
from nibabel.pydicom_compat import pydicom

import Config
from utils.synthMap import GenericModel


class Orientation(Enum):
    AXIAL = 1
    CORONAL = 2
    SAGITTAL = 3


class MRIImage:
    """
    Wrapper class for MRI images.
    """
    def __init__(self, type_image=None, name="", path="", image3d=None, button_box=None, is_found=False, is_loaded=False):
        self.type_image = type_image
        self.name = name
        self.path = path
        self.button_box = button_box
        self.image3d = image3d
        self.is_found = is_found
        self.is_loaded = is_loaded


class SmModel:
    """
    The model of the Application. It contains all the loaded data, generated images and choosen parameter values
    """
    def __init__(self, appSM):
        self.appSM = appSM
        self.dcm_folder = None
        self.original_synth_dicom = None
        self.original_synth_matrix = None
        self.original_synth_hdr = None
        self.modified_synth_matrix_2d = None
        self.modified_synth_matrix_3d = None
        self.map_type = None
        self.current_orientation_slice = {Orientation.AXIAL: -1,
                                          Orientation.SAGITTAL: -1,
                                          Orientation.CORONAL: -1}
        self.orientation = Orientation.AXIAL
        self.mri_images = []
        self.synth_maps = [t[0] for t in Config.synth_images]
        self.synth_names = [t[1] for t in Config.synth_images]
        self.quantitative_maps = Config.quantitative_maps
        self.set_mri_images_from_config()
        self.synt_par = Config.synth_parameters
        self.wl = None
        self.wc = None
        self.maxWindowWidth = 4000
        self.maxWindowCenter = 4000
        self.minWindowWidth = 100
        self.minWindowCenter = 100
        self.mousePos = (0, 0)
        self.scale = Config.image_interpolation["scale"]
        self.interpolation = Config.image_interpolation["interpolation_type"]
        # self.modified_matrix_flag = False
        self.reload_ui = True
        self.root_dcm_folder = None
        self.missing_dicoms = True
        self.input_images_type = "Dicom"

    # GETTER AND SETTER
    def set_map_type(self, map_type):
        self.map_type = map_type

    def get_map_type(self, long_name=False):
        if long_name:
            return self.get_long_name_by_short_name(self.map_type)
        return self.map_type

    def get_long_name_by_short_name(self, short_name):
        return self.synth_names[self.synth_maps.index(short_name)]

    def set_input_images_type(self, input_images_type):
        self.input_images_type = input_images_type

    def get_input_images_type(self):
        return self.input_images_type

    def is_input_niftii(self):
        return self.input_images_type == "Niftii"

    def set_mri_images_from_config(self):
        for qm_name in self.quantitative_maps:
            self.mri_images.append(MRIImage(type_image="Q", name=qm_name))
        for qm_name in self.synth_maps:
            self.mri_images.append(MRIImage(type_image="S", name=qm_name))

    def reset_synth_params(self):
        for sp in self.synt_par.keys():
            self.synt_par[sp]["value"] = Config.synth_parameters[sp]["default"]
        self.setAxial()

    def set_root_dcm_folder(self, root_dcm_folder):
        # consider windows and linux paths
        self.root_dcm_folder = os.path.normpath(root_dcm_folder)

    def get_mri_image_list(self):
        return self.mri_images

    def get_quantitative_mri_image_names(self):
        return [pi.name for pi in self.mri_images if pi.type_image == "Q"]

    def get_quantitative_mri_image_paths(self):
        return [pi.path for pi in self.mri_images if pi.type_image == "Q"]

    def get_quantitative_mri_image_list(self):
        return [pi for pi in self.mri_images if pi.type_image == "Q"]

    def are_quantitative_maps_set(self):
        for q_img in self.get_quantitative_mri_image_list():
            if not q_img.is_found:
                return False
        return True

    def get_synthetic_mri_image_names(self):
        return [pi.name for pi in self.mri_images if pi.type_image == "S"]

    def get_synthetic_mri_image_paths(self):
        return [pi.path for pi in self.mri_images if pi.type_image == "S"]

    def get_synthetic_mri_image_list(self):
        return [pi for pi in self.mri_images if pi.type_image == "S"]

    def set_mri_image_path(self, name, path):
        pi = self.get_mri_image_by_name(name)
        pi.is_found = True
        pi.path = path

    def get_mri_image_by_name(self, name):
        for pi in self.mri_images:
            if pi.name == name:
                return pi
        return None

    def get_quantitative_mri_images(self):
        return [q_mri for q_mri in self.mri_images if q_mri.type_image == "Q"]

    def load_dicom_folder_infos(self):
        # search maps for modifying synthetic maps
        sub_dirs_names = [o for o in os.listdir(self.root_dcm_folder) if
                          os.path.isdir(os.path.join(self.root_dcm_folder, o))]
        sub_dirs_paths = [os.path.join(self.root_dcm_folder, o) for o in sub_dirs_names]
        for name in sub_dirs_names:
            pi = self.get_mri_image_by_name(name)
            if pi is not None:
                subfolder_path = os.path.join(self.root_dcm_folder, name)
                self.set_mri_image_path(name, subfolder_path)

    def load_niftii_folder_infos(self):
        # search maps for modifying synthetic maps
        sub_filenames = [f for f in os.listdir(self.root_dcm_folder) if os.path.isfile(os.path.join(self.root_dcm_folder, f))]
        for name in sub_filenames:
            basename = name.split("_")[0]
            pi = self.get_mri_image_by_name(basename)
            if pi is not None:
                subfolder_path = os.path.join(self.root_dcm_folder, name)
                self.set_mri_image_path(basename, subfolder_path)

    def load_missing_dicoms(self):
        for quantitative_image in self.get_quantitative_mri_images():
            # self.load_file_by_name(quantitative_image)
            self.load_input_file_by_name(quantitative_image)

    def load_input_file_by_name(self, parametric_image):
        name = parametric_image.name
        path = parametric_image.path
        if path.endswith(".nii"):
            self.load_niftii_by_name(parametric_image)
        else:
            self.load_file_by_name(parametric_image)

    def load_dicom_by_name(self, parametric_image):
        name = parametric_image.name
        path = parametric_image.path

        wildcard_path = os.path.join(path, "*")
        files = []
        print('Loading image: {}'.format(wildcard_path))
        for fname in glob.glob(wildcard_path, recursive=False):
            try:
                files.append(pydicom.dcmread(fname))
            except Exception as e:
                e.dicom_map_type = name
                raise e
        # ensure they are in the correct order
        slices = sorted(files, key=lambda s: s.SliceLocation)

        # create 3D array
        img_shape = list(slices[0].pixel_array.shape)
        img_shape.append(len(slices))
        img3d = np.zeros(img_shape)

        for i, s in enumerate(slices):
            img2d = s.pixel_array
            img3d[:, :, i] = img2d

        pi = self.get_mri_image_by_name(name)
        pi.image3d = img3d

    def load_niftii_by_name(self, parametric_image):
        name = parametric_image.name
        path = parametric_image.path
        niftii_file = nib.load(path)
        img3d = niftii_file.get_fdata()

        img3d = np.transpose(img3d, (1, 0, 2))
        img3d = np.flip(img3d, axis=0)
        img3d = np.flip(img3d, axis=1)

        pi = self.get_mri_image_by_name(name)
        pi.image3d = img3d

    def load_file_by_name(self, parametric_image):
        if self.input_images_type == "Dicom":
            self.load_dicom_by_name(parametric_image)
        elif self.input_images_type == "Niftii":
            self.load_niftii_by_name(parametric_image)


    def load_file(self, path):
        """ Load file. Format can be dicom or Niftii. Path contains dicom dir path or .nii file path """
        if self.input_images_type == "Dicom":
            wildcard_path = os.path.join(path, "*")
            # load the DICOM files
            files = []
            print('Loading dicom: {}'.format(wildcard_path))
            # dirPath get 1 unique set of dicoms
            for fname in glob.glob(wildcard_path, recursive=False):
                # print("loading: {}".format(fname))
                try:
                    files.append(pydicom.dcmread(fname))
                except Exception as e:
                    e.dicom_map_type = path
                    raise e

            print("file count: {}".format(len(files)))

            # ensure they are in the correct order
            slices = sorted(files, key=lambda s: s.SliceLocation)

            # create 3D array
            img_shape = list(slices[0].pixel_array.shape)
            dcm_header = slices[0]
            img_shape.append(len(slices))
            self.original_synth_matrix = np.zeros(img_shape)

            # fill 3D array with the images from the files
            for i, s in enumerate(slices):
                img2d = s.pixel_array

                self.original_synth_matrix[:, :, i] = img2d
            self.modified_synth_matrix_3d = self.original_synth_matrix.copy()
            # init modified image 3d to the original one
            # TODO use tag (0020,0037) http://dicomiseasy.blogspot.com/2013/06/getting-oriented-using-image-plane.html
            # self.dcm_img = np.flipud(self.dcm_img)

            self.original_synth_hdr = dcm_header
            # self.set_init_slicenum()
            self.original_synth_dicom = slices

        elif self.input_images_type == "Niftii":
            niftii_file = nib.load(path)
            self.original_synth_matrix = niftii_file.get_fdata()
            self.original_synth_matrix = np.flip(np.flip(self.original_synth_matrix, axis=1), axis=0).T
            self.modified_synth_matrix_3d = self.original_synth_matrix.copy()
            self.original_synth_hdr = niftii_file.header
            self.original_synth_dicom = niftii_file
            self.original_synth_hdr.WindowWidth = 3600
            self.original_synth_hdr.WindowCenter = 3600

    def save_synthetic_image(self, dir_path, filename, output_format):
        modified_img_3d = self.modified_synth_matrix_3d

        if output_format == "dicom":
            dir_path = os.path.join(dir_path, filename)
            slices = modified_img_3d.shape[2]
            modified_dicom = self.original_synth_dicom
            try:
                os.mkdir(dir_path)
            except FileExistsError:
                raise FileExistsError
            for slice in range(slices):
                modified_img_2d = modified_img_3d[slice]
                # modified_img_2d = self.original_synth_matrix[slice]
                modified_img_2d = modified_img_2d.astype(np.short)
                modified_dicom[slice].PixelData = modified_img_2d.tobytes()
                if slice == 0:
                    p = modified_dicom[slice].PixelData

                path = os.path.join(dir_path, filename + "_" + str(slice + 1) + ".dcm")
                # os.mkdir(dir_path)
                modified_dicom[slice].WindowCenter = self.original_synth_hdr.WindowCenter
                modified_dicom[slice].WindowWidth = self.original_synth_hdr.WindowWidth
                modified_dicom[slice].SeriesDescription = filename
                modified_dicom[slice].save_as(path)

        elif output_format == "niftii":
            file_path = os.path.join(dir_path, filename + ".nii")

            tmp = modified_img_3d.astype(np.float32)
            tmp = np.flip(np.flip(tmp.transpose(), axis=0), axis=1)

            nifti = nib.Nifti1Image(tmp, np.eye(4))
            nib.save(nifti, file_path)

    def set_slice_num(self, sliceNum):
        """Gets called by the SliceView when slice slider is moved"""
        self.current_orientation_slice[self.orientation] = sliceNum

    def get_slice_num(self, orientation):
        return self.current_orientation_slice[orientation]

    def set_init_slicenum(self):
        self.current_orientation_slice[Orientation.AXIAL] = round(self.original_synth_matrix.shape[2] / 2) - 1
        self.current_orientation_slice[Orientation.SAGITTAL] = round(self.original_synth_matrix.shape[0] / 2) - 1
        self.current_orientation_slice[Orientation.CORONAL] = round(self.original_synth_matrix.shape[1] / 2) - 1

    def getAxialSlice(self):
        return self.original_synth_matrix.shape[2]

    def getVoxelRange(self, sliceType):
        """Return min and max of maps"""
        if sliceType == 'Axial':
            slice_data = self.original_synth_matrix[:, :, self.get_slice_num(sliceType)]
        elif sliceType == 'Sagittal':
            slice_data = self.original_synth_matrix[self.get_slice_num(sliceType), :, :]
        elif sliceType == 'Coronal':
            slice_data = self.original_synth_matrix[:, self.get_slice_num(sliceType), :]

        return slice_data.min(), slice_data.max()

    def get_2d_image(self):
        if self.modified_synth_matrix_2d is None:
            self.orient_img_2d()
        return self.modified_synth_matrix_2d

    def orient_img_2d(self):
        if self.orientation == Orientation.AXIAL:
            self.modified_synth_matrix_2d = np.flipud(
                self.modified_synth_matrix_3d[:, :, self.current_orientation_slice[Orientation.AXIAL]])

        elif self.orientation == Orientation.SAGITTAL:
            self.modified_synth_matrix_2d = self.modified_synth_matrix_3d[
                                            :, self.current_orientation_slice[Orientation.SAGITTAL], :].T
        elif self.orientation == Orientation.CORONAL:
            self.modified_synth_matrix_2d = self.modified_synth_matrix_3d[
                                            self.current_orientation_slice[Orientation.CORONAL], :, :].T

    def setAxial(self):
        self.orientation = Orientation.AXIAL

    def setSagittal(self):
        self.orientation = Orientation.SAGITTAL

    def setCoronal(self):
        self.orientation = Orientation.CORONAL

    def get_mri_image_matrix_by_name(self, name, dim=2):
        pi = self.get_mri_image_by_name(name)
        t_img3d = pi.image3d
        if dim == 2:
            if self.orientation == Orientation.AXIAL:
                return np.flipud(t_img3d[:, :, self.current_orientation_slice[Orientation.AXIAL]])
            elif self.orientation == Orientation.SAGITTAL:
                return t_img3d[:, self.current_orientation_slice[Orientation.SAGITTAL], :].T
            elif self.orientation == Orientation.CORONAL:
                return t_img3d[self.current_orientation_slice[Orientation.CORONAL], :, :].T
        else:
            return pi.image3d

    # timeit
    def modify_syntetic_map(self, dims=2):

        DICOM_SCALE = 2 ** 15 - 2

        t1_img = self.get_mri_image_matrix_by_name(Config.T1, dims)
        t2_img = self.get_mri_image_matrix_by_name(Config.T2, dims)
        pd_img = self.get_mri_image_matrix_by_name(Config.PD, dims)

        maps = {
            Config.T1: t1_img,
            Config.T2: t2_img,
            Config.PD: pd_img
        }
        pars = [(self.synt_par[par]["value"], self.synt_par[par]["equation"]) for par in self.synt_par if
                self.synt_par[par]["enabled"]]

        img = GenericModel.signal_model(maps, pars)

        # get scaling
        img = np.abs(img)
        maxval = img.max()
        minval = img.min()

        scaling = DICOM_SCALE / (maxval - minval) * 0.1
        offset = minval

        self.original_synth_hdr.WindowCenter = np.floor(0.1 * DICOM_SCALE / 2)
        self.original_synth_hdr.WindowWidth = np.floor(0.1 * DICOM_SCALE)
        if dims == 3:
            self.modified_synth_matrix_3d = (scaling * (img - offset)).astype(np.float32)  # 102, 120, 021, 210, 0,1,2
            self.modified_synth_matrix_3d = np.transpose(self.modified_synth_matrix_3d, (2, 0, 1))
        else:
            self.modified_synth_matrix_2d = (scaling * (img - offset)).astype(np.float32)
