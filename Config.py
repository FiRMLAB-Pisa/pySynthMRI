# Quantitative Maps:
T1 = "T1"
T2 = "T2"
PD = "PD"
quantitative_maps = [T1, T2, PD]

# Synthetic Maps:
MP2RAGE = ("MP2RAGE", "T1-weighted - Magnetization-Prepared 2 RApid Gradient Echoes")
GRE = ("GRE", "T1-weighted - Gradient Echo ")
FSE = ("FSE", "T2-weighted - Fast Spin Echo")
FLAIR = ("FLAIR", "T2-weighted - Fluid Attenuated Inversion Recover")
synth_images = [MP2RAGE, GRE, FSE, FLAIR]

# Virtual Scanner Parameters
synth_parameters = {
    "TE": {
        "label": "TE",
        "default": 82, #75
        "min": 1,
        "max": 100,
        "step": 1,
        "weight": 1,
        "default_maps": [FLAIR[0], FSE[0]],
        "equation": [0, PD, T2]      # = 0 + PD*exp(-TE/T2)
    },
    "TR": {
        "label": "TR",
        "default": 220,
        "min": 100,
        "max": 500,
        "step": 5,
        "weight": 2,
        "default_maps": [GRE[0]],
        "equation": [1, -1, T1]      # = 1 -1*exp(-TR/T1)
    },
    "TI": {
        "label": "TI",
        "default": 2500, # 1300
        "min": 1000,
        "max": 3500,
        "step": 10,
        "weight": 3,
        "default_maps": [FLAIR[0], MP2RAGE[0]],
        "equation": [1, -2, T1]     # = 1 -2*exp(-IT/T1)
    },
    "T1SAT": {
        "label": "T1SAT",
        "default": 500,
        "min": 400,
        "max": 1000,
        "step": 10,
        "weight": 4,
        "default_maps": [FLAIR[0]],
        "equation": [0, 1, T1]     # = 1 -1*exp(-T1SAT/T1)
    }
}


image_interpolation = {
    "interpolation_type": "linear",
    "scale": 4
}