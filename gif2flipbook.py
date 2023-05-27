from alive_progress import alive_bar
import glob
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
import re
import shutil
import sys


cwd = os.getcwd()
path_gifs = os.path.join(cwd, "GIFS", "*.*")
#The list returned by "glob" is sorted, such that the prefix letters may be
#assembled in sequence in the resulting list. For example: "['a-name-1.gif', 'A-name-2.gif',
#'b-name-3.gif', 'B-name-4.gif', 'c-name-5.gif', 'C-name-6.gif', 'd-name-7.gif', 'D-name-8.gif']",
#where GIFS sharing a letter would feature on flip sides of the same quadrant of the sheet of paper.
gif_files = sorted(glob.glob(path_gifs), key=str.lower)

print("\nCurrently doing preliminary processing of " + str(len(gif_files)) + " GIF files:\n")

if len(gif_files) > 0 and len(gif_files) <= 8:
    #The default non-printable border at the top and bottom
    #of the page is set to a quarter inch (or rather the
    #corresponding number of pixels, 75 px)
    border = math.floor(0.25*300)

    #By default, central horizontal and vertical lines will
    #divide every sheet of paper in four even parts to facilitate
    #cutting the pages after printing. The user can pass in the
    #argument "no_lines" when running the code if they will be
    #printing on perforated paper and guide lines would therefore
    #not be needed.
    lines = True

    #If the user does not wish the size of the images to be increased
    #so as to fit within the available space, the "no_size_increase"
    #argument may be passed in when running the code.
    no_size_increase = False

    #The "minimum_frame_number" variable allows the user to specify
    #the minimum number of frames that the flipbook will contain.
    #Should the selected GIFS have less frames than "minimum_frame_number",
    #they will loop over until the required amount of frames has been reached.
    minimum_frame_number = None

    if len(sys.argv) > 1:
        #The "try/except" statement will
        #intercept any "ValueErrors" and
        #ask the users to correctly enter
        #the desired values for the variables
        #directly after the colon separating
        #the variable name from the value.
        try:
            for i in range(1, len(sys.argv)):
                if sys.argv[i][:7].strip().lower() == "border:":
                    border = math.floor(float(sys.argv[i][7:])*300)
                elif sys.argv[i].strip().lower() in ["no_lines", "no_lines:"]:
                    lines = False
                elif sys.argv[i].strip().lower() in ["no_size_increase", "no_size_increase"]:
                    no_size_increase = True
                elif sys.argv[i][:21].strip().lower() == "minimum_frame_number:":
                    minimum_frame_number = int(sys.argv[i][21:])

        except Exception as e:
            print(e)
            sys.exit('\nPlease specify the non-printable border (in inches and decimal form, but without units) ' +
            'precedec by the "border:" argument. Also, you may pass in the "no_lines" argument should you not ' +
            'wish to have guides to cut along the line when assembling your flipbook (if you are printing on ' +
            'perforated paper, for instance). For example, for a 1/4 inch border and no guiding lines, you would ' +
            'enter the following: "python3 gif2flipbook.py border:0.25 no_lines".\n')

    #The GIF file names are extracted from the paths when splitting along the backslash or forward
    #slash path dividers and selecting for the last element, and then spitting it along the periods
    #and selecting the first resulting element to remove the extension. It is important that the
    #GIF file names do not contain any special characters (only letters and no spaces).
    gif_names = [re.split(r"/|\\", gif_files[i])[-1].split(".")[0] for i in range(len(gif_files))]

    with alive_bar(len(gif_files)) as bar:
        #The number of frames in each GIF will be collected in the list "number_of_frames",
        #and the GIF with the most frames will be used as a guideline for how many times
        #the other GIFS need to loop over until the end of the flipbooks, as they are
        #all printed on the same sheet of paper.
        number_of_frames = []
        #The paths of the PNG images for every frame of each GIF are stored in the list
        #"gif_png_paths".
        gif_png_paths = []
        for i in range(len(gif_files)):
            #A "PNG" folder containing subfolders for every GIF is created.
            if not os.path.exists(os.path.join(cwd, "PNGS", gif_names[i])):
                os.makedirs(os.path.join(cwd, "PNGS", gif_names[i]))
            #The individual frames of every GIF are exported as PNG images
            #using the "Image.seek()" method to bring the GIF object to the
            #frame number "j".
            with Image.open(gif_files[i]) as gif_object:
                for j in range(gif_object.n_frames):
                    gif_object.seek(j)
                    gif_object.save(os.path.join(cwd, 'PNGS', gif_names[i], gif_names[i] + "-" + str(j) + '.png'))

            path_pngs = os.path.join(cwd, "PNGS", gif_names[i], "*.png")
            #The paths of the PNG files extracted from the GIFS are stored within the list "gif_png_paths".
            #As the paths are strings, they need to be sorted numerically using a lambda function that
            #splits the path strings along the hyphens, and indexing the last element, corresponding to
            #the suffix (ex: 0.gif), and then excluding the extension and converting the resulting
            #strings into integers.
            gif_png_paths.append(sorted(glob.glob(path_pngs), key=lambda x:int(x.split("-")[-1].split(".")[0])))
            number_of_frames.append(gif_object.n_frames)
            bar()

    #The maximum number of frames for the longest
    #GIF is stored in "maximum_frame_number" and if
    #it is inferior to "minimum_frame_number", the
    #its value would be set to that of "minimum_frame_number".
    maximum_frame_number = max(number_of_frames)

    if minimum_frame_number and maximum_frame_number < minimum_frame_number:
        maximum_frame_number = minimum_frame_number

    #The number of frames in every GIF is printed on screen to allow
    #the users to select GIFS of similar lengths for making flipbooks,
    #although this isn't striclty necessary, as the shorter GIFS will
    #simply be looped over until the "maximum_frame_number" is reached.
    print("\n\nHere is the number of frames in your GIFS:\n")
    for i in range(len(gif_names)):
        print("- " + gif_names[i] + ": " + str(number_of_frames[i]))

    #The following nested "for" loops will populate the list
    #"png_index_list", which will determine when a shorter GIF
    #will need to loop over.
    png_index_list = []
    gif_indices_repeat = [0, 0, 0, 0, 0, 0, 0, 0]
    #For every new GIF, an empty list is appended to "png_index_list"
    #in order to add the PNG frame indices, up to the last index within
    #a given GIF, upon which it starts again at frame zero.
    #The list "gif_indices_repeat" (initialized at index zero
    #for each GIF) stores the current PNG frame indices.
    for i in range(len(gif_png_paths)):
        png_index_list.append([])
        for j in range(maximum_frame_number):
            if gif_indices_repeat[i] < len(gif_png_paths[i])-1:
                png_index_list[-1].append(gif_indices_repeat[i])
                gif_indices_repeat[i] += 1
            else:
                png_index_list[-1].append(gif_indices_repeat[i])
                if gif_indices_repeat[i] < len(gif_png_paths[i])-1:
                    gif_indices_repeat[i] += 1
                else:
                    gif_indices_repeat[i] = 0

    #If the user has included more than four GIFS within the "GIFS" subfolder
    #of the working folder, then the PNG frame indices within "png_index_list"
    #for even-numbered GIFS will be reversed, as they GIFS will be printed on
    #both sides of the sheet of paper. That is to say that the GIFS on the two
    #sides of the page are progressing in opposite directions, as the flip book
    #needs to be "flipped" in order to watch the animation on the other side.
    if len(gif_files) > 4:
        for i in range(len(png_index_list)):
            if i%2 == 0:
                png_index_list[i] = png_index_list[i][::-1]

    print("\n\nCurrently generating a PDF document with a total of " + str(maximum_frame_number) + " frames.\n")
    with alive_bar(maximum_frame_number) as bar:
        #The width and height of the resized PNG images will be stored in the
        #list "gif_dimensions".
        gif_dimensions = []
        #The dictionary "image_layout" contains keys mapping to the GIF indices and
        #values containing the string equivalent of the expressions required to determine
        #the x,y coordinates of the upper-left corner of the resized PNG images that will
        #be pasted onto "blank_canvas" or "blank_canvas_reverse". These cannot be determined
        #at this point, as the "resizing_factor" has not yet been calculated for each GIF.
        #An "eval()" method will be called later in the code upon obtaining this information,
        #effectively updating the values of "image_layout" for the corresponding x,y tuples.
        if len(gif_files) < 5:
            image_layout = {0:"(math.floor(8.5/4*300-width/2), border)",
            1:"(math.floor(8.5*0.75*300-width/2), border)",
            2:"(math.floor(8.5*0.75*300-width/2), math.floor(11*300-border-height))",
            3:"(math.floor(8.5/4*300-width/2), math.floor(11*300-border-height))"}
        elif len(gif_files) > 4:
            image_layout = {0:"(math.floor(8.5/4*300-width/2), border)",
            1:"(math.floor(8.5*0.75*300-width/2), border)",
            2:"(math.floor(8.5*0.75*300-width/2), border)",
            3:"(math.floor(8.5/4*300-width/2), border)",
            4:"(math.floor(8.5*0.75*300-width/2), math.floor(11*300-border-height))",
            5:"(math.floor(8.5/4*300-width/2), math.floor(11*300-border-height))",
            6:"(math.floor(8.5/4*300-width/2), math.floor(11*300-border-height))",
            7:"(math.floor(8.5*0.75*300-width/2), math.floor(11*300-border-height))"}

        for i in range(maximum_frame_number):
            #A blank canvas (white US letter JPEG image, with a resolution of 300 ppi (2550x3300 px))
            #is generated for the first GIF and will contain frames from 4 different GIFS.
            blank_canvas = Image.open(os.path.join(cwd, "blank_canvas.jpg"))
            blank_canvas_editable = ImageDraw.Draw(blank_canvas)
            #If there are more than four GIFS in "gif_files" it means that some of these will
            #be included on the reverse side of the pages. A reverse canvas therefore
            #needs to be created in order to pair up the GIF file names starting with
            #the same letters (ex: "a-name-1.gif" and "A-name-2.gif").
            if len(gif_files) > 4:
                blank_canvas_reverse = Image.open(os.path.join(cwd, "blank_canvas.jpg"))
                blank_canvas_reverse_editable = ImageDraw.Draw(blank_canvas_reverse)
            for j in range(len(gif_files)):
                if i == 0:
                    frame = Image.open(gif_png_paths[j][0])
                    frame_editable = ImageDraw.Draw(frame)
                    #The width and height of the frame will be checked against the available
                    #space on the quarter of page on which it would be printed. If the image is
                    #too small or too big, The default value of one for "resize_factor" would then
                    #be the minimum between "width_check" and "height_check" to ensure that the resized
                    #image will fit into the available space.
                    resize_factor = 1
                    width, height = frame.size

                    width_check = 1-(width - (8.5/2*300-2*border))/width
                    height_check = 1-(height - (4.5*300-border))/height
                    if width_check < 1 or height_check < 1:
                        resize_factor = min([width_check, height_check])
                    elif no_size_increase == False and width_check > 1 and height_check > 1:
                        resize_factor = min([width_check, height_check])

                    #Should the "resize_factor" not be equal to one, it means that the
                    #PNG images need to be resized. The updated "width" and "height" x,y tuple
                    #for the resized images will allow to position the images correctly on the flipbooks.
                    frame = frame.resize((math.floor(resize_factor*width), math.floor(resize_factor*height)))
                    width, height = frame.size
                    gif_dimensions.append((width, height))

                #Once all of the GIFS have had their resizing_factor determined, further
                #iterations of the "for i in range(len(maximum_frame_number)):" loop will
                #simply use the updated width and height dimensions stored in the "gif_dimensions" list.
                else:
                    width, height = gif_dimensions[j]

                #Now that the resized image dimensions are known for every GIF, the values
                #within the "image_layout" mapping to every GIF index (the keys of the dictionary)
                #will be updated using an "eval()" method. This only needs to be done for the first
                #run through the "for i in range(len(maximum_frame_number)):" loop, as the same
                #x, y tuples of the upper-left corners of the PNG images for every GIF will be
                #used throughout when pasting the images.
                if i == 0:
                    image_layout[j] = eval(image_layout[j])

                #An Image object is instantiated for each of the PNG frames of the GIFS,
                #following the sequence determined above within "png_index_list" that
                #accounts for the shorter GIFS looping over (restarting at index zero),
                #until reaching "maximum_frame_number".
                frame_k = Image.open(os.path.join(gif_png_paths[j][png_index_list[j][i]]))
                frame_k_editable = ImageDraw.Draw(frame_k)

                #If "resize_factor" wasn't equal to one, it means that the PNG images for
                #the given GIF needs to be resized according to the updated width and height
                #values.
                if resize_factor != 1:
                    frame_k = frame_k.resize((width, height), resample=Image.Resampling.LANCZOS)

                #If there are four or less GIFS within the "GIFS" subfolder of the
                #working folder, these will all be printed on the same side of the page,
                #and therefore there will be no instances of "blank_canvas_reverse".
                #The images up top need (indices 0 being the upper left corner and later
                #indices progressing in clockwise order) to be flipped in order for their
                #bottom to line up with the short edge of the pages. This will facilitate
                #assembling the flipbooks with all pages well lined up along the precut
                #sides of the pages.
                if len(gif_files) < 5:
                    if j in [0, 1]:
                        blank_canvas.paste(frame_k.rotate(180), image_layout[j])
                    else:
                        blank_canvas.paste(frame_k, image_layout[j])
                #A similar approach is taken for five or more GIFS, but in this case
                #successive GIFS will be printed on opposite sides of the page, with
                #those printed on the upper corners needing once again to be flipped.
                else:
                    if j in [0,2]:
                        blank_canvas.paste(frame_k.rotate(180), image_layout[j])

                    elif j in [4,6]:
                        blank_canvas.paste(frame_k, image_layout[j])
                    elif j in [1,3]:
                        blank_canvas_reverse.paste(frame_k.rotate(180), image_layout[j])
                    elif j in [5,7]:
                        blank_canvas_reverse.paste(frame_k, image_layout[j])

            #If the user hasn't passed in the "no_lines" argument, a horizontal and vertical
            #line will be drawn in order to divide the pages into quarters, which will facilitate
            #cutting the pages and assembling the flipbooks. These lines are only drawn on one side
            #of each sheet of paper.
            if lines:
                blank_canvas_editable.line([(2550/2, 0), (2550/2, 3300)], fill="Gainsboro", width=5)
                blank_canvas_editable.line([(0, 3300/2), (2550, 3300/2)], fill="Gainsboro", width=5)

            #The PDF files are saved in the "if" and "else" statements
            #below, with the "append=True" option being selected for
            #the pages after the first one.
            if i == 0:
                blank_canvas.save(os.path.join(cwd, "flipbook.pdf"),
                quality=100, resolution=300)
                if len(gif_files) > 4:
                    blank_canvas_reverse.save(os.path.join(cwd, "flipbook.pdf"),
                    quality=100, resolution=300)

            else:
                blank_canvas.save(os.path.join(cwd, "flipbook.pdf"),
                append=True, quality=100, resolution=300)
                if len(gif_files) > 4:
                    blank_canvas_reverse.save(os.path.join(cwd, "flipbook.pdf"),
                    append=True, quality=100, resolution=300)
            bar()

    #Lastly, the "PNGS" folder containing the PNGs and its contents is deleted.
    shutil.rmtree(os.path.join(cwd, "PNGS"))

else:
    print("Please include between one and eight GIF files inclusively within the GIFS folder.")
