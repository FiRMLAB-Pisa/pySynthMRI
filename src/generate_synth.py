import sys
import os
sys.path.append(os.path.dirname(__file__))

import argparse
import nibabel as nib
import numpy as np
from scipy import ndimage

from model.psSynthModel import (
    SyntheticFLAIR,
    SyntheticFSE,
    SyntheticGRE,
    SyntheticMP2RAGE
)
# from model.MRIImage import Interpolation


def apply_interpolation(image, scale_factor, interpolation_type):
    """
    Apply interpolation and scaling to the image
    Based on MRIImage interpolation handling
    """
    if scale_factor == 1:
        return image
    
    if interpolation_type == "linear":
        order = 1
    elif interpolation_type == "bicubic":
        order = 3
    elif interpolation_type == "nearest":
        order = 0
    else:  # default to linear
        order = 1
    
    # Calculate new dimensions
    new_shape = tuple(int(dim * scale_factor) for dim in image.shape)
    
    # Use scipy zoom for interpolation
    scaled_image = ndimage.zoom(image, scale_factor, order=order)
    
    return scaled_image


def get_field_strength_params(field_strength, model_type):
    """
    Get field strength specific parameters
    Based on the preset system in pySynthMRI
    """
    # Default parameters for different field strengths
    # These would be configured by user in GUI
    field_params = {
        "1.5T": {
            "GRE": {"TR": 220},
            "FSE": {"TE": 75},
            "FLAIR": {"TI": 2500, "TE": 82, "TSAT":500},
            "MP2RAGE": {"TI": 1300}
        },
        "3.0T": {
            "GRE": {"TR": 31, "TE": 0},
            "FSE": {"TR":8000, "TE": 80},
            "FLAIR": {"TE": 80, "TI": 2075,  "TSAT":1405},
            "MP2RAGE": {"TI": 1816}
        },
        "7.0T": {
            "GRE": {"TR": 220},
            "FSE": {"TE": 75},
            "FLAIR": {"TI": 2500, "TE": 82, "TSAT":500},
            "MP2RAGE": {"TI": 1300}
        }
    }
    
    return field_params.get(field_strength, field_params["3.0T"]).get(model_type, {})

def apply_scaling(image):
    """
    Apply scaling similar to MRIImage.recompute_smap
    """
    SCALE = 2 ** 16 - 1  # From Smap class
    
    # Get scaling
    img = np.abs(image)
    maxval = img.max()
    minval = img.min()
    
    if maxval > minval:
        scaling = SCALE / (maxval - minval) * 0.1
        offset = minval
        scaled_image = (scaling * (img - offset)).astype(np.float32)
    else:
        scaled_image = img.astype(np.float32)
    
    return scaled_image


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic MRI images from quantitative maps")
    parser.add_argument("--t1", required=True, help="Path to T1 map NIfTI file")
    parser.add_argument("--t2", required=True, help="Path to T2 map NIfTI file") 
    parser.add_argument("--pd", required=True, help="Path to PD map NIfTI file")
    # parser.add_argument("--output", required=True, help="Output path for synthetic image")
    parser.add_argument("--model", required=True, choices=["GRE", "FSE", "FLAIR", "MP2RAGE"], help="Synthesis model")

    # Field strength option
    parser.add_argument("--field_strength", choices=["1.5T", "3.0T", "7.0T"], default="3.0T", 
                       help="MRI field strength (default: 3.0T)")
    
    # Manual parameter overrides (optional)
    parser.add_argument("--TR", type=float, help="Repetition time (ms) - overrides field strength default")
    parser.add_argument("--TE", type=float, help="Echo time (ms) - overrides field strength default")
    parser.add_argument("--TI", type=float, help="Inversion time (ms) - overrides field strength default")
    parser.add_argument("--TSAT", type=float, help="Saturation Time for FLAIR (ms) - overrides field strength default")
    
    # Image processing options
    parser.add_argument("--interpolation", choices=["linear", "bicubic", "nearest"], default="linear",
                       help="Interpolation method for scaling (default: linear)")
    parser.add_argument("--scale", type=float, default=2.0,
                       help="Scaling factor for output image (default: 2.0)")
    parser.add_argument("--apply_scaling", action="store_true",
                       help="Apply intensity scaling")

    args = parser.parse_args()

    # Load quantitative maps
    t1_img = nib.load(args.t1)
    t2_img = nib.load(args.t2)
    pd_img = nib.load(args.pd)

    t1_data = t1_img.get_fdata()
    t2_data = t2_img.get_fdata()
    pd_data = pd_img.get_fdata()

    # Get field strength specific parameters
    field_params = get_field_strength_params(args.field_strength, args.model)
    
    # Use manual parameters if provided, otherwise use field strength defaults
    TR = args.TR if args.TR is not None else field_params.get("TR")
    TE = args.TE if args.TE is not None else field_params.get("TE")
    TI = args.TI if args.TI is not None else field_params.get("TI")
    TSAT = args.TSAT if args.TSAT is not None else field_params.get("TSAT")

    # Select synthesis model and call with correct parameters
    if args.model == "GRE":
        model = SyntheticGRE()
        synthetic_image = model.signal_model(t1_data, TR)
        output_name = f"GRE - {args.field_strength}T_TR_{TR}.nii"
    elif args.model == "FSE":
        model = SyntheticFSE()
        synthetic_image = model.signal_model(t2_data, pd_data, TE)
        output_name = f"FSE - {args.field_strength}T_TE_{TE}.nii"
    elif args.model == "FLAIR":
        model = SyntheticFLAIR()
        synthetic_image = model.signal_model(t1_data, TI, TE, TSAT)
        output_name = f"FLAIR - {args.field_strength}T_TE_{TE}_TI_{TI}_TSAT_{TSAT}.nii"
    elif args.model == "MP2RAGE":
        model = SyntheticMP2RAGE()
        synthetic_image = model.signal_model(t1_data, TI)
        output_name = f"MP2RAGE - {args.field_strength}T_TI_{TI}.nii"

    # Apply the same post-processing as MRIImage.recompute_smap()
    synthetic_image = np.nan_to_num(synthetic_image)
    
    # Create a mask for non-zero regions (similar to GUI logic)
    if args.model == "GRE" or args.model == "IR":
        # GRE and IR only use T1
        mask = t1_data > 0
    elif args.model == "FSE":
        # FSE uses T2 and PD
        mask = (t2_data > 0) & (pd_data > 0)
    else:
        # Other models use all three maps
        mask = (t1_data > 0) & (t2_data > 0) & (pd_data > 0)
    
    synthetic_image[~mask] = 0

    # Apply scaling if requested
    if args.apply_scaling:
        synthetic_image = apply_scaling(synthetic_image)

    # Apply interpolation and scaling
    if args.scale != 1.0:
        synthetic_image = apply_interpolation(synthetic_image, args.scale, args.interpolation)
        
        # Update affine matrix for the scaled image
        scaled_affine = t1_img.affine.copy()
        # Adjust voxel size in affine matrix
        scaled_affine[:3, :3] = scaled_affine[:3, :3] / args.scale
    else:
        scaled_affine = t1_img.affine

    # Save the result
    synthetic_img = nib.Nifti1Image(synthetic_image, scaled_affine, t1_img.header)
    nib.save(synthetic_img, output_name)
    
    print(f"Synthetic {args.model} image saved to {output_name}")
    print(f"Field strength: {args.field_strength}")
    print(f"Parameters used: TR={TR}, TE={TE}, TI={TI}, TSAT={TSAT}")
    print(f"Interpolation: {args.interpolation}, Scale: {args.scale}")


if __name__ == "__main__":
    main()
