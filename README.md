# Puncta Analyzer
Quantify puncta in images

## Requirements
- anaconda 3.7
- conda
- imageJ

## Installation
Download this repository via git or github

Using:
- terminal for Mac OS
- conda prompt for Windows

navigate to repository on your computer after you download it e.g.
and create the conda environment

```sh
cd ./puncta-analyzer
conda env create -f environment.yml
```

## Usage

The puncta analyzer is a two step process
1.  Image straightening
2.  Image analysis

### Image Straightening
1. in the `dist` folder, copy `Preprocessor_2.jar` to your imagej plugins folder
2. open the tiff file to analyze in imagej
3. use the **segmented line tool** to draw a series of line segments representing the region of the image you are interested in
4. open the plugins -> Preprocessor_2 plugin
5. save the straightened images to a directory of your choice
6. two images will be saved
  - the brightened image is for presentations
  - the processed images is for analysis
  - generally, save the processed images in one directory so they can be batch processed by the puncta analyzer


### Image Analysis
To run the program:
```
conda activate puncta-analyzer
```

Navigate to the directory that you downloaded puncta-analyzer to:
```
cd ./puncta-analyzer
```

#### Basic Usage
```
python src/puncta-analyzer.py <src> <dst>
```

Example:
```
python src/puncta-analyzer.py ./data/subtracted.tif ./data/

To view all options, type:
```
python src/puncta-analyzer --help

Usage: puncta_analyzer.py [OPTIONS] INPUT_PATH OUTPUT_PATH

  analyze puncta in tif files

Options:
  -lo, --min-sigma INTEGER RANGE  Lower values detect smaller puncta
                                  [default: 1]
  -hi, --max-sigma INTEGER RANGE  Higher values detect larger puncta
                                  [default: 10]
  -t, --threshold FLOAT RANGE     Higher values remove puncta with duller
                                  intensity  [default: 0.1]
  -ov, --overlap FLOAT RANGE      If the fraction of overlap between two
                                  puncta is greater than this value, remove
                                  the smaller puncta  [default: 0.7]
  --save-annotated                Draw circles around recognized puncta and
                                  save as an image  [default: False]
  --help                          Show this message and exit.
```
