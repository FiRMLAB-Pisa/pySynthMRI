  [![Contributors][contributors-shield]][contributors-url]
  [![Forks][forks-shield]][forks-url]
  [![Stargazers][stars-shield]][stars-url]
  [![Issues][issues-shield]][issues-url]
  [![License][license-shield]][license-url]


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <h3 align="center"><b>PysynthMRI</b></h3>

  <p align="center">
    Python Tool for Synthetic MRI
    <br />
    <a href="https://github.com/FiRMLAB-Pisa/pySynthMRI"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/FiRMLAB-Pisa/pySynthMRI/issues">Report Bug</a>
    ·
    <a href="https://github.com/FiRMLAB-Pisa/pySynthMRI/issues">Request Feature</a>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about">About</a>
    </li>
    <li>
       <a>Getting Started</a>
      <ul>
        <li><a href="#getting-started-with-windows">Windows</a></li>
        <li><a href="#getting-started-with-linux-or-macos">Linux</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#example-data">Example Data</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
# About
![pysynthmri-screenshot]
PysynthMRI is a python open-source tool which provides a user-friendly interface to synthesize contrast weighted images. It allows the user to load quantitative maps and adjust virtual scanner parameters to obtain, in real time, the best images.



<!-- GETTING STARTED -->
# Getting Started with Windows

## WINDOWS Installation

1. Download Release from: [https://github.com/FiRMLAB-Pisa/pySynthMRI/releases/download/v1.0.0/pySynthMRI-v1.0.0-windows-executable.zip](https://github.com/FiRMLAB-Pisa/pySynthMRI/releases/download/v1.0.0/pySynthMRI-v1.0.0-windows-executable.zip)
2. unzip pySynthMRI-v1.0.0.zip
3. run PySynthMRI.exe


# Getting Started with Linux or MacOS
These instructions will give you a copy of the project up and running on your local machine,
using Linux or MacOS<br>
Make sure you have [Python](https://python.org/) version >= 3.6.
## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/FiRMLAB-Pisa/pySynthMRI.git
   ```
2. Create a [Python Virtual Environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)

3. Install required libraries:
   ```sh
   pip install -r requirements.txt
    ```

<!-- USAGE EXAMPLES -->
# Usage


### Configuration
In order to correctly execute pySynthMRI, `config.json` file need to be created.
A default configuration file (`config-sample.json`) is provided for reference. <br/>
We suggest to copy sample file:

```sh
   cp config-sample.json config.json
```
    
Below part of the configuration file is reported for help.
```json
{
    "synthetic_images": {
        "FS15T": {                                # Name of preset (multiple presets can exists)
            "FSE": {                              # Name of signal model
                "title": "T2w - Fast Spin Echo",  # Title of signal model
                "equation": "PD*exp(-TE/T2)",     # Model equation
                "parameters": {                   # List of parameters json object
                    "TE": {                       # Name of parameter
                        "label": "TE [ms]",       # Shown label
                        "value": 80,              # Default value
                        "min": 1,                 # Min value
                        "max": 100,               # Max value
                        "step": 1                 # Slider/Mouse parameter step 
                    }
                },
                "series_number": 9001             # [optional] Add to SeriesNumber DICOM tag (0020,0011)
            },
[...]
    "quantitative_maps": {                        # Quantitative maps that can be loaded
        "T1": {                                   # Name of map
            "file_name": "qmap_t1"                # substring filename (used if autoload qmaps)
        },
        "T2": {
            "file_name": "qmap_t2"
        },
        "PD": {
            "file_name": "qmap_pd"
        }
    },
[...]
}
```
### Launch PySynthMRI
You can launch PySynthMRI running `launcher.py` in your Python IDE or via operating system command-line or terminal:

```shell
python pySynthMRI.py
```

### Default Signal Models
Custom signal models can be added at runtime or using the configuration file. <br/>
To facilitate the user, PySynthMRI contains a set of default contrast images in its configuration file: 

| Title   | Equation                                                                                     | Description                                          |
|---------|----------------------------------------------------------------------------------------------|------------------------------------------------------|
| FSE     | PD \* ((1 - exp(-TR/T1))\*exp(-TE/T2))                                                       | T2w - Fast Spin Echo                                 |
| GRE     | PD \* ((1 - exp(-TR/T1))\*exp(-TE/T2)                                                        | T1w - Gradient Echo                                  |
| FLAIR   |abs(PD) \* exp(-TSAT/T1)\*exp(-TE/T2)\*(1-2\*exp(-TI/T1))                                     | T2w - Fluid Attenuated Inversion Recover             |
| MP2RAGE | 1-2\*exp(-TI/T1)                                                                             | T1w - Magnetization-Prepared 2 RApid Gradient Echoes |
| DIR     | PD \* (1 - 2\*exp(-TI_2/T1) + 2\*exp(-(TI_1+TI_2)/T1) -  exp(-TR/T1)) \* (exp(-TE/T2))       | 3D Double Inversion Revovery                         |
| TBE | PD \* (1-2\*exp(-TI/T1)) \* (1-exp(-TR/T1)) \* exp(-TE/T2)                                       | Tissue Border Enhancement by inversion recovery      |




<!-- EXAMPLE DATA -->
## Example Data
In order to test the software with in-vivo data, we provide downloadable example files at the following link: [test_data.zip](https://github.com/FiRMLAB-Pisa/pySynthMRI/releases/download/v1.0.0/test_data.zip).
The zip file contains 3 quantitative, anonymized maps.

<h4 align="center">

| Filename        | Quantitative Map | 
|-----------------|------------------|
| qmap_t1_bet.nii | T1               |
| qmap_t2_bet.nii | T2               |
| qmap_pd_bet.nii | PD               |
    
</h4>

<!-- LICENSE -->
## License

PySynthMRI is distributed under GPL-v3.0 License. See [LICENSE.txt](https://github.com/FiRMLAB-Pisa/pySynthMRI/blob/main/LICENSE.txt) for more information.



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/FiRMLAB-Pisa/pySynthMRI
[contributors-url]: https://github.com/FiRMLAB-Pisa/pySynthMRI/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/FiRMLAB-Pisa/pySynthMRI
[forks-url]: https://github.com/FiRMLAB-Pisa/pySynthMRI/network/members
[stars-shield]: https://img.shields.io/github/stars/FiRMLAB-Pisa/pySynthMRI 
[stars-url]: https://github.com/FiRMLAB-Pisa/pySynthMRI/stargazers
[issues-shield]: https://img.shields.io/github/issues/FiRMLAB-Pisa/pySynthMRI
[issues-url]: https://github.com/FiRMLAB-Pisa/pySynthMRI/issues
[license-shield]: https://img.shields.io/github/license/FiRMLAB-Pisa/pySynthMRI
[license-url]: https://github.com/FiRMLAB-Pisa/pySynthMRI/blob/master/LICENSE.md
[pysynthmri-arch]: src/resources/images/arch.png
[pysynthmri-screenshot]: src/resources/images/screenshot.png
