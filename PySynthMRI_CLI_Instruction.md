# 🧪 PySynthMRI CLI Tool — Quick Start Guide

This guide helps you generate synthetic MRI images (FLAIR, GRE, FSE, MP2RAGE) using a command-line Python script without launching the GUI.

---

## ✅ 1. Folder Structure

Organize your project like this:

```
pySynthMRI-main/
├── src/
│   ├── generate_synth.py        ← ✅ put the script here
│   └── model/
│       └── psSynthModel.py      ← already in repo
test_data/
    └── data/
        └── test_subject/
            ├── qmap_t1_bet.nii  ← ✅ T1 map
            ├── qmap_t2_bet.nii  ← ✅ T2 map
            └── qmap_pd_bet.nii  ← ✅ PD map
```

---

## ✅ 2. Install Dependencies

Ensure Python 3.6+ is installed.

Then run:

```bash
pip install nibabel numpy
```

Or you can install all dependencies listed in the repo's requirements.txt:
```bash
pip install -r requirements.txt
```

---

## ✅ 3. Run the Script

Navigate into the `src/` folder:

```bash
cd path\to\pySynthMRI-main\src
```

Then run one of the following:

---

## 🧪 4. Model Usage Examples

### ▶️ GRE (Gradient Echo)

```bash
python generate_synth.py --t1 "/mnt/c/Temp/QBB/pySynthMRI-v1.0.0/test_data/qmap_t1_bet.nii" 
                        --t2 "/mnt/c/Temp/QBB/pySynthMRI-v1.0.0/test_data/qmap_t2_bet.nii" 
                        --pd "/mnt/c/Temp/QBB/pySynthMRI-v1.0.0/test_data/qmap_pd_bet.nii" 
                        --field_strength 3.0T --scale 2 --interpolation linear --apply_scaling
                        --model GRE
```

### ▶️ FSE (Fast Spin Echo)

```bash
python generate_synth.py --t1 "/mnt/c/Temp/QBB/pySynthMRI-v1.0.0/test_data/qmap_t1_bet.nii" 
                        --t2 "/mnt/c/Temp/QBB/pySynthMRI-v1.0.0/test_data/qmap_t2_bet.nii" 
                        --pd "/mnt/c/Temp/QBB/pySynthMRI-v1.0.0/test_data/qmap_pd_bet.nii" 
                        --field_strength 3.0T --scale 2 --interpolation linear --apply_scaling
                        --model FSE
```

### ▶️ FLAIR

```bash
python generate_synth.py --t1 "/mnt/c/Temp/QBB/pySynthMRI-v1.0.0/test_data/qmap_t1_bet.nii" 
                        --t2 "/mnt/c/Temp/QBB/pySynthMRI-v1.0.0/test_data/qmap_t2_bet.nii" 
                        --pd "/mnt/c/Temp/QBB/pySynthMRI-v1.0.0/test_data/qmap_pd_bet.nii" 
                        --field_strength 3.0T --scale 2 --interpolation linear --apply_scaling
                        --model FLAIR
```

### ▶️ MP2RAGE

```bash
python generate_synth.py --t1 "/mnt/c/Temp/QBB/pySynthMRI-v1.0.0/test_data/qmap_t1_bet.nii" 
                        --t2 "/mnt/c/Temp/QBB/pySynthMRI-v1.0.0/test_data/qmap_t2_bet.nii" 
                        --pd "/mnt/c/Temp/QBB/pySynthMRI-v1.0.0/test_data/qmap_pd_bet.nii" 
                        --field_strength 3.0T --scale 2 --interpolation linear --apply_scaling
                        --model MP2RAGE

```

---

## ✅ 5. View Results

Use a medical viewer like:
- **MRIcroGL**
- **ITK-SNAP**
- OR imageJ with NIFTI add on
- Or use Python:

```python
import nibabel as nib
import matplotlib.pyplot as plt

img = nib.load("gre_synthetic.nii.gz")
data = img.get_fdata()
plt.imshow(data[:, :, data.shape[2] // 2], cmap="gray")
plt.axis("off")
plt.title("Middle Slice")
plt.show()
```

---

## 🔒 Notes

- This script does **not** use `config.json`
- Output NIfTI files will be saved in your working directory
