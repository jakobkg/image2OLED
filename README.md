# image2OLED
 A python script to convert image files to C arrays that display on OLEDs like the one found on Kyria mechanical keyboards

## Setup

Set up a virtualenv if you wish, navigate to this directory and do
`pip install -r requirements.txt`

## Usage
```
usage: image2OLED.py [-h] [-o] [-p] [-d] [-s] [-x WIDTH] [-y HEIGHT] [-w] inputfile

positional arguments:
  inputfile             Path to the image file to convert

optional arguments:
  -h, --help            show this help message and exit
  -o, --output          Path to output file with the C array, if not given the same filename as the input is used,
                        with filetype .c
  -p, --preview         Print the resulting image to the terminal
  -d, --dither          Set flag to dither image in conversion from colour to BW, if applicable
  -s, --small           Set flag if your OLED has a resolution of 128x32 instead of 128x64
  -x WIDTH, --width WIDTH
                        Pixel width of your OLED
  -y HEIGHT, --height HEIGHT
                        Pixel height of your OLED. If no OLED resolution information is given, 128x64 is assumed
  -w, --white           If set, the padding on images with an aspect ratio different to the aspect ratio of your OLED
                        will be white instead of black
```
