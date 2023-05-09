import numpy as np

class SyntheticMP2RAGE:

    @staticmethod
    def signal_model(t1_map, inversion_time=1300):
        img = 1 - 2 * np.exp(-inversion_time / t1_map)

        return img


class SyntheticGRE:

    @staticmethod
    def signal_model(t1_map, repetition_time=220):
        img = np.abs(1 - (np.exp(np.divide(-repetition_time, t1_map))))
        return np.around(img, decimals=2)


class SyntheticFSE:

    @staticmethod
    def signal_model(t2_map, proton_density, echo_time=75):
        return np.abs(proton_density * (np.exp(-echo_time / t2_map)))


class SyntheticFLAIR:

    @staticmethod
    def signal_model(t1_map, t2_map, proton_density, inversion_time=2500, echo_time=82, t1_sat_flair=500):
        k = np.divide(echo_time, t2_map)
        k1 = np.divide(inversion_time, t1_map)
        k2 = np.divide(t1_sat_flair, t1_map)
        return np.abs(proton_density) * np.exp(-k2) * np.exp(-k) * (1 - 2 * np.exp(-k1))


class GenericModel:
    """
    Synthetic contrast-weighted image
    """
    @staticmethod
    def signal_model(maps, params):
        """
        Synthesize weighted-contrast image using quantitative maps and provide virtual scanner parameters
        input:
            maps: dictionary containing quantitative maps as specified in Config files
            params: list of virtual scanner parameters represented by tuples (value, parameter equation)
        return:
            Synthesized image
        """

        img = None
        mask = None
        used_map = None
        for value, equation in params:
            offset = equation[0]
            scale = equation[1]  # can be scalar or a map
            if isinstance(scale, str):
                scale = maps[scale]
            used_map = maps[equation[2]]


            if img is not None:
                # first scanner parameter
                img = img * (offset + (scale * np.exp(-value / used_map)))
            else:
                img = offset + (scale * np.exp(-value / used_map))

        # get mask
        if mask is None and used_map is not None:
            mask = used_map == 0
            img[mask] = 0

        if img is None:
            # synth map can be T1w, T2w, PDw
            return np.ones((200, 200))
        return np.abs(img)
