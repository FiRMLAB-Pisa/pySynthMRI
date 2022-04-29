import re

from model.MRIImage import Interpolation
import json


class ValidateConfig:
    def __init__(self):
        fd = open('config.json')
        config = json.load(fd)

        self.synth_types = config["synthetic_images"]
        self.qmap_types = config["quantitative_maps"]
        self.image_interpolation = config["image_interpolation"]

        for syth_type in self.synth_types:
            self.validate_equation(self.synth_types[syth_type])
            self.validate_scanner_parameters(self.synth_types[syth_type])
        # interpolation
        self.validate_interpolation(self.image_interpolation)

        # self.synth_types = Config.synth_types
        # for syth_type in self.synth_types:
        #     validate_equation(self.synth_types[syth_type])
        #     validate_scanner_parameters(self.synth_types[syth_type])
        # # interpolation
        # self.image_interpolation = Config.image_interpolation
        # validate_interpolation(self.image_interpolation)
        # self.qmap_types = Config.qmap_types

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
        scanner_parameters = synth_type["parameters"]
        for k in scanner_parameters:
            scanner_parameters[k]["default"] = scanner_parameters[k]["value"]

    def validate_equation(self, synth_type):
        symbols = ["exp", "abs", "sqrt", "cos", "sin", "tan"]
        synth_type["equation_string"] = synth_type["equation"]
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
