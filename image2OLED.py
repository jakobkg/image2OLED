import argparse
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("inputfile", help="Path to the image file to convert")
parser.add_argument("-o", "--output", help="Path to output file with the C array, if not given the same filename as the input is used, with filetype .c", action="store_true")
parser.add_argument("-p", "--preview", help="Print the resulting image to the terminal", action="store_true")
parser.add_argument("-d", "--dither", help="Set flag to dither image in conversion from colour to BW, if applicable", action="store_true")
parser.add_argument("-s", "--small", help="Set flag if your OLED has a resolution of 128x32 instead of 128x64", action="store_true")
parser.add_argument("-x", "--width", help="Pixel width of your OLED", type=int)
parser.add_argument("-y", "--height", help="Pixel height of your OLED. If no OLED resolution information is given, 128x64 is assumed", type=int)
parser.add_argument("-w", "--white",
                    help="If set, the padding on images with an aspect ratio different to the aspect ratio of your OLED will be white instead of black", action="store_true")

args = parser.parse_args()

## Some argument checking to be sure given input isn't goobledigook

if args.small and (args.width or args.height):
    exit("Use only -s/--small OR -x/--width <WIDTH> -y/--height <HEIGHT> to set your OLED resolution")

if (args.width is None and args.height is not None) or (args.width is not None and args.height is None):
    exit("Please provide both width and height of your OLED: -x <WIDTH> -y <HEIGHT>")

if (args.width and args.width <= 0) or (args.height and args.height <= 0):
    exit("Given OLED resolution must be positive integers")

if args.height and args.height % 8 != 0:
    exit("Vertical resolution must be a multiple of 8")

## Calculate and store OLED resolution and aspect ratio for later

outputWidth = 128 if not args.width else args.width
outputHeight = 32 if args.small else 64 if not args.height else args.height
outputAspectRatio = outputWidth / outputHeight

outputFilename = args.inputfile.rsplit(".", 1)[0] + ".c"


def image2array(filename, dithering):
    result = []
    try:
        with Image.open(filename) as img:
            print("Reading file {}".format(filename))
            if img.mode != "1":
                img = img.convert("1", dither=1 if dithering else 0)
                print("Converting image to black and white, {}dithering".format("" if dithering else "not "))
            
            inputWidth, inputHeight = img.size
            inputAspectRatio = inputWidth / inputHeight
            if inputAspectRatio >= outputAspectRatio: # If input image is too wide, resize to fit
                rescaleFactor = outputWidth / inputWidth
                img = img.resize((round(inputWidth * rescaleFactor), round(inputHeight * rescaleFactor)))
            else:
                rescaleFactor = outputHeight / inputHeight # If input image is too tall, resize to fit
                img = img.resize((round(inputWidth * rescaleFactor), round(inputHeight * rescaleFactor)))

            resizedWidth, resizedHeight = img.size

            frame = Image.new("1", (outputWidth, outputHeight), 255 if args.white else 0) # Make empty frame of same resolution as output

            if outputWidth > resizedWidth: # Place resized input image centered in the empty frame
                frame.paste(img, ((outputWidth - resizedWidth) // 2, 0))
            elif outputHeight > resizedHeight:
                frame.paste(img, (0, (outputHeight - resizedHeight) // 2))
            else:
                frame.paste(img, (0, 0))
            
            img = frame

            resizedWidth, resizedHeight = img.size
            
            for y in range(0, resizedHeight, 8):
                for x in range(0, resizedWidth):
                    col = 0
                    for p in range(0, 8):
                        pixel = int(img.getpixel((x, y + p)) / 255)
                        s = pixel << p
                        col = col | s
                    result.append(col)
    except IOError:
        exit("Error reading image file")
    
    return result

def previewImage(array, width, height):
    print("Printing preview:")
    for y in range(0, int(height / 8)):
            for p in range(0, 8, 2):
                    for x in range(0, width):
                        i = x + y * width
                        b = array[i] >> p & 1
                        b2 = array[i] >> (p + 1) & 1
                        if (b == 0 and b2 == 0):
                            print(" ", end = '')
                        elif (b == 1 and b2 == 0):
                            print("▀", end = '')
                        elif (b == 0 and b2 == 1):
                            print("▄", end = '')
                        elif (b == 1 and b2 == 1):
                            print("█", end = '')
                    print("")

def writeArray(array, width, tofile, outputfile):
    outputstring = ""
    outputstring += "static void render_image_{}(void) {{\n    ".format(outputfile[:-2])
    outputstring += "static const char PROGMEM {}[] = {{\n        ".format(outputfile[:-2])

    for index, byte in enumerate(array):
        if index % width == 0 and index > 0:
            outputstring += "\n        "
        outputstring += "{:<3}, ".format(byte) if index != len(array) - 1 else "{:<3}\n    }};\n\n".format(byte)
    
    outputstring += "    oled_write_raw_P({}, sizeof({}));\n}}".format(outputfile[:-2], outputfile[:-2])

    if tofile:
        try:
            with open(outputfile, "w+") as f:
                print("Writing to file {}".format(outputfile))
                f.write(outputstring)
        except:
            exit("Error writing to output file")
    else:
        print(outputstring)

imagearray = image2array(args.inputfile, args.dither)
if args.preview:
    previewImage(imagearray, outputWidth, outputHeight)

writeArray(imagearray, outputWidth, args.output, outputFilename)

print("Success! Copy the {} to your keymap.c to start using it!".format(("contents of " + outputFilename) if args.output else "above"))
