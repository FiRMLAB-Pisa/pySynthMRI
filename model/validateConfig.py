import copy
import json

from model.MRIImage import Interpolation
from model.psExceptions import ConfigurationFilePermissionError

CONFIG_FILE_NAME = "config.json"
class ValidateConfig:
    def __init__(self):
        fd = open(CONFIG_FILE_NAME)
        config = json.load(fd)

        self.presets = config["synthetic_images"]
        self.default_preset = list(self.presets.keys())[0]

        self.synth_types = self._parse_synthetic_maps(config)
        self.qmap_types = config["quantitative_maps"]
        self.image_interpolation = config["image_interpolation"]
        self.screenshot_directory = config["screenshot_directory"]
        for synth_type in self.synth_types:
            self.validate_equation(self.synth_types[synth_type], synth_type)
            self.validate_scanner_parameters(self.synth_types[synth_type])
            self.validate_window_scale(self.synth_types[synth_type])
        # interpolation
        self.validate_interpolation(self.image_interpolation)

    def _parse_synthetic_maps(self, config):
        # check all available presets
        synth_maps = dict()
        for preset_key in self.presets:
            for smap_key in config["synthetic_images"][preset_key]:
                new_name = smap_key + " - " + preset_key
                synth_maps[new_name] = copy.deepcopy(config["synthetic_images"][preset_key][smap_key])
                synth_maps[new_name]["preset"] = preset_key
                # synth_maps[new_name]["label"] = smap_key + " - " + preset_key
        return synth_maps

    def validate_interpolation(self, image_interpolation):
        if image_interpolation["interpolation_type"] == "linear":
            image_interpolation["interpolation_type"] = Interpolation.LINEAR
        elif image_interpolation["interpolation_type"] == "nn":
            image_interpolation["interpolation_type"] = Interpolation.NN
        elif image_interpolation["interpolation_type"] == "bicubic":
            image_interpolation["interpolation_type"] = Interpolation.BICUBIC
        else:
            image_interpolation["interpolation_type"] = Interpolation.NONE

    def validate_scanner_parameters(self, synth_type):
        synth_type["mouse_v"] = None
        synth_type["mouse_h"] = None
        scanner_parameters = synth_type["parameters"]
        for idx, k in enumerate(scanner_parameters):
            scanner_parameters[k]["default"] = scanner_parameters[k]["value"]
            if idx == 0:
                scanner_parameters[k]["mouse"] = "V"
                synth_type["mouse_v"] = k
            elif idx == 1:
                scanner_parameters[k]["mouse"] = "H"
                synth_type["mouse_h"] = k
            else:
                scanner_parameters[k]["mouse"] = "N"


    def validate_equation(self, synth_type, synth_type_label):
        symbols = ["exp", "abs", "sqrt", "cos", "sin", "tan"]
        synth_type["equation_string"] = synth_type["equation"]

        # check parenthesis
        if synth_type["equation"].count("(") != synth_type["equation"].count(")"):
            raise TypeError("Check parenthesis in {} equation.".format(synth_type_label))

        for s in symbols:
            symbol = s + "("
            synth_type["equation"] = synth_type["equation"].replace(symbol, "np." + symbol)

        synth_type["equation"] = synth_type["equation"].replace("Pi", "np.pi")
        # synth_type["equation"] = synth_type["equation"].replace("exp(", "np.exp(")
        # synth_type["equation"] = synth_type["equation"].replace("abs(", "np.abs(")
        for scanner_param in synth_type["parameters"]:
            synth_type['title']  # (?<=\b|[a-zA-Z0-9])TI(?=\b|_)
            # '(?<![a-zA-Z])'+ scanner_param + '(?![a-z-Z])'
            synth_type["equation"] = synth_type["equation"].replace(scanner_param,
                                                                    'self._parameters["' + scanner_param + '"]["value"]')
        synth_type["qmaps_needed"] = []
        for qmap in self.qmap_types:
            if qmap in synth_type["equation"]:
                synth_type["qmaps_needed"].append(qmap)

        for qmap in self.qmap_types:
            synth_type["equation"] = synth_type["equation"].replace(qmap,
                                                                    'self._qmaps["' + qmap + '"].get_matrix(dim=dims)')

    def validate_window_scale(self, synth_struct):
        if "window_center" not in synth_struct:
            synth_struct["window_center"] = None
            synth_struct["default_window_center"] = None
        else:
            synth_struct["default_window_center"] = synth_struct["window_center"]

        if "window_width" not in synth_struct:
            synth_struct["window_width"] = None
            synth_struct["default_window_width"] = None
        else:
            synth_struct["default_window_width"] = synth_struct["window_width"]

    def update_file(self, preset, map_type, parameters, ww=None, wc=None):
        try:
            with open(CONFIG_FILE_NAME, "r+") as fd:
                config = json.load(fd)
                # remove preset from name
                map_type = map_type[:-len(" - " + preset)]
                # update config struct
                for p_name in parameters:
                    p_value = parameters[p_name]["value"]
                    config['synthetic_images'][preset][map_type]['parameters'][p_name]['value'] = p_value

                # update ww wc
                if ww is not None and wc is not None:
                    config['synthetic_images'][preset][map_type]['window_width'] = ww
                    config['synthetic_images'][preset][map_type]['window_center'] = wc
                # rewrite file
                fd.seek(0)
                json.dump(config, fd, indent=4)
                fd.truncate()
                return True
        except:
            raise ConfigurationFilePermissionError("Error saving configuration file. Check if file exists or if it is locked.")

    def get_preset_idx(self, preset):
        return self.presets.index(preset)
