from alive_progress import alive_bar
import cv2
from datetime import date
import glob
import math
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pypdf import PdfMerger
import re
import shutil
import sys


cwd = os.getcwd()
#The default non-printable border at the top and bottom
#of the page is set to a quarter inch (or rather the
#corresponding number of pixels, 75 px)
border = math.floor(0.25*300)

#The frame number i+1 from the "for i in range(maximum_frame_number):" loop
#is printed in the top of each quadrant in order to facilitate flipbook assembly.
numbers_font = ImageFont.truetype(os.path.join(cwd, "baskvl.ttf"), 60)

#By default, central horizontal and vertical lines will
#divide every sheet of paper in four even parts to facilitate
#cutting the pages after printing. The user can pass in the
#argument "no_lines" when running the code if they will be
#printing on perforated paper and guide lines would therefore
#not be needed.
lines = True

#The default resolution of the PDF resolution is set to
#200 dpi and can be altered by passing in the desired
#value, after the "resolution:" argument.
pdf_resolution = 200

#If the user does not wish the size of the images to be increased
#so as to fit within the available space, the "no_size_increase"
#argument may be passed in when running the code.
no_size_increase = False

#The "number_of_frames" variable allows the user to specify
#the minimum number of frames that the flipbook will contain.
#Should the selected GIFS have less frames than "number_of_frames",
#they will loop over until the required amount of frames has been reached.
number_of_frames = None

#If the user includes video files in the "GIF" folder,
#they will typically want to select a subclip of that
#video to convert into a flipbook. The default "start_time"
#(time stamp at which the clip begins) is set to zero seconds
#and the "end_time" (time stamp at which the video clip stops)
#is set to five seconds. These will be replaced by the time
#stamps included in the name of the video file (if any). Should
#the user not specify these, the first five seconds of the video
#will be converted into a flipbook.
start_time = 0
end_time = 5

#Should all flipbooks need to be generated in 3d anaglyph format, you can pass in the "3d" argument
#when running the code and "three_dee_flipbooks" will be set to "True". The default number of
#pixels in-between the red and cyan channels is set to 15 pixels, with the cyan layer on the
#right. Should you like to change the number of horizontal pixels in-between the red and cyan
#channels for all of the anaglyph flipbooks, you would need to pass in the number of pixels
#after the "3d" argument, preceded by a colon. For example, "3d:30" would generate anaglyph
#flipbooks with 30 pixels in-between the red and cyan channels, with the cyan layer on
#the right. To have the red layer be on the right side of the anaglyph frames for all 3D
#flipbooks, simply add "r" after the number (ex: "3d:30r"). You may also decide to only
#have selected animations rendered in 3d anaglyph format (or only certain animations with
#the red layer on the right) by including the parenthesized number of pixels in-between
#the red and cyan layers, in addition to "r" (red) or "b" (blue) designating which layer
#will be found on the right end of the anaglyph frames for this animation
#(ex: "my_video (5)(10)(3d30r).mp4" would generate a subclip spanning the timestamps of 5 to 10 seconds of
#that animation in anaglyph format, with 30 pixels in-between the red and cyan layers, with the red
#channel being on the right of the frames.
three_dee_flipbooks = False
red_right = False
pixels_between_red_cyan = 15

#Flipbooks that are to be rendered in anaglyph 3D format may need to have their
#frames brightened, as anaglyph images appear darker than regular frames. You may
#specify a brightening ratio (inputted in percent form) specifically for a given
#animation in its file name (parenthesized and followed by a percent symbol).
#In addition to this, a brightening ratio may be specified for all animations other than
#those that have a brightening ratio in their file name, by passing in the percent value after
#the "brighten:" argument (example "brighten:50%" would brighten the frames by 50%, while -50%
#would darken the frames by 50%).

#By default, the extracted frames of the animations are not brightened in
#creating the flipbooks. You may specify a brightening value applied to all
#frames of all animations by passing in the percentage value after the "brighten:"
#argument (ex: "brighten:70%" to brighten all frames of all animations by 70%),
#or indicate the brightening value for a specific animation in its file name
#(ex: "my_animation (-40%).gif", in which case this specific animation would be
#darkened by 40%, the darkening being a result of the negative sign).
brighten_percent = None

#The default number of frames per second ("fps") is set to 25
#and the user may select another number. The minimum between
#the actual fps of the video and the value of "fps" will be selected,
#as the video cannot have more frames than its fps would allow.
fps = 25

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
            elif sys.argv[i][:17].strip().lower() == "number_of_frames:":
                number_of_frames = int(sys.argv[i][17:])
            elif sys.argv[i][:4].strip().lower() == "fps:":
                fps = int(sys.argv[i][4:].strip())
            elif sys.argv[i][:9].strip().lower() == "brighten:":
                brighten_percent = int(sys.argv[i][9:].replace("%", "").strip())/100
            #Should all flipbooks need to be generated in 3d anaglyph format, you may pass in the "3d" argument
            #when running the code and "three_dee_flipbooks" will be set to "True". The default number of
            #pixels in-between the red and cyan channels is set to 15 pixels, with the cyan layer on the
            #right. Should you like to change the number of horizontal pixels in-between the red and cyan
            #channels for all of the anaglyph flipbooks, you would need to pass in the number of pixels
            #after the "3d" argument, preceded by a colon. For example, "3d:30" would generate anaglyph
            #flipbooks with 30 pixels in-between the red and cyan channels, with the cyan layer on
            #the right. To have the red layer be on the right side of the anaglyph frames for all 3D
            #flipbooks, simply add "r" after the number (ex: "3d:30r"). You may also decide to only
            #have selected animations rendered in 3d anaglyph format (or only certain animations with
            #the red layer on the right) by including the parenthesized number of pixels in-between
            #the red and cyan layers, preceded by "3d" and followed by either "r" (red) or "b" (blue)
            #designating which layer will be found on the right end of the anaglyph frames for this animation
            #(ex: "my_video (5)(10)(3d30r).mp4" would generate a subclip spanning the timestamps of 5 to 10 seconds of
            #that animation in anaglyph format, with 30 pixels in-between the red and cyan layers, with the red
            #channel being on the right of the frames.
            elif sys.argv[i][:2].strip().lower() == "3d":
                three_dee_flipbooks = True
                three_dee_split = [element for element in sys.argv[i].strip().lower().split(":") if element != ""]
                if len(three_dee_split) > 1:
                    pixels_between_red_cyan = int(re.findall(r"[\d]+", three_dee_split[1])[0])
                    if "r" in three_dee_split[1]:
                        #The variable "red_right" will have the red channel be on the right end of the anaglyph
                        #frames for all of the 3d flipbook animations. Otherwise, the default value of "red_right"
                        #is initialized to "False", meaning that the cyan layer is on the right.
                        red_right = True
            elif sys.argv[i][:11].strip().lower() == "resolution:":
                pdf_resolution = int(sys.argv[i][11:].strip())

    except Exception as e:
        print(e)
        sys.exit('\nPlease specify the non-printable border (in inches and decimal form, but without units) ' +
        'precedec by the "border:" argument. Also, you may pass in the "no_lines" argument should you not ' +
        'wish to have guides to cut along the line when assembling your flipbook (if you are printing on ' +
        'perforated paper, for instance). For example, for a 1/4 inch border and no guiding lines, you would ' +
        'enter the following: "python3 gif2flipbook.py border:0.25 no_lines".\n')

path_gifs = os.path.join(cwd, "GIFS", "*.*")
#The list returned by "glob" is sorted, such that the prefix letters may be
#assembled in sequence in the resulting list. For example: "['a-name-1.gif', 'A-name-2.gif',
#'b-name-3.gif', 'B-name-4.gif', 'c-name-5.gif', 'C-name-6.gif', 'd-name-7.gif', 'D-name-8.gif']",
#where GIFS sharing a letter would feature on flip sides of the same quadrant of the sheet of paper.
gif_files = sorted(glob.glob(path_gifs), key=str.lower)
gif_files_extensions = []

if len(gif_files) > 0 and len(gif_files) <= 8:
    #The GIF file names are extracted from the paths when splitting along the backslash or forward
    #slash path dividers and selecting for the last element, and then spitting it along the periods
    #and selecting the first resulting element to remove the extension. It is important that the
    #GIF file names do not contain any special characters (only letters and no spaces).

    gif_names = [re.split(r"/|\\", gif_files[i])[-1] for i in range(len(gif_files))]
    gif_names = [re.split(r"([.])", gif_names[i])[:-2][0] for i in range(len(gif_names))]

    print("\nCurrently analyzing " + str(len(gif_files)) + " animation " +
    ("files")*(len(gif_files) > 1) + ("file")*(len(gif_files) == 1) + ":\n")

    with alive_bar(len(gif_files)) as bar:
        #The number of frames in each GIF will be collected in the list "gif_number_of_frames",
        #and the GIF with the most frames will be used as a guideline for how many times
        #the other GIFS need to loop over until the end of the flipbooks, as they are
        #all printed on the same sheet of paper.
        gif_number_of_frames = []

        #The paths of the PNG images for every frame of each GIF are stored in the list
        #"gif_png_paths".
        gif_png_paths = []

        #The list "list_three_dee" will keep track of which animations are to be rendered in anaglyph
        #flipbook format.
        list_three_dee = []

        #The list "list_brighten_percent" will be populated with the brightening ratio
        #for each animation, whether it be derived from its file name (which overrides
        #any other default or user-defined value) or from the "brighten:" argument
        #when running the code, or the default value of "None".
        list_brighten_percent = []

        #The list "frame_durations" will either contain an integer value of the millisecond duration of each frame
        #for video animations (1/fps*1000) or the list of individual millisecond durations for each frames of
        #an animated image such as GIFS. This will allow to extract the frames from the videos and to generate
        #GIF previews of the 3D flipbooks.
        frame_durations = []

        #The list "list_red_right" will keep track of which anaglyph animations have the red channel
        #on the right side. The list "list_pixels_between_red_cyan" will keep tabs on the number of pixels
        #in-between the red and cyan channels in the anaglyph frames for each animation.
        list_red_right = []
        list_pixels_between_red_cyan = []

        #The "fps_setting" variable stores the default fps setting of 25, unless it was overriden
        #by the user by passing in another fps value after the "fps" argument when running the code.
        #This is required, as the fps variable will be overriden with the minimal value in-between
        #the video fps and the fps supplied by the user (or the default of 25).
        fps_setting = fps

        for i in range(len(gif_files)):
            #Similarly, the presence of the number of horizontal pixels in-between the red and cyan channels
            #of the anaglyph frames found within the file names will be determined here.
            #The regex expression 'r"[(](3d[ ]?[r|b]?[ ]?[\d]+[ ]?[r|b]?)[)]"' matches "3d" plus an optional space,
            #followed by the optional presence of "r" (red) or "b" (blue or cyan) designating which color will be present
            #on the right of the anaglyph frame, with the number of horizontal pixels ([\d]+) in-between the red and cyan channels.
            #These values are appended in the list "list_brighten_percent".
            current_file_name_pixels_between_red_cyan = re.findall(r"[(](3d[ ]?[r|b]?[ ]?[\d]+[ ]?[r|b]?)[)]", gif_names[i].lower())
            #If you only want to designate that the animation is to be rendered in 3D, you would write "(3d)" in the file name, so
            #a search has to be done for this specifically.
            if current_file_name_pixels_between_red_cyan == []:
                current_file_name_pixels_between_red_cyan = re.findall(r"[(](3d)[)]", gif_names[i].lower())
            if current_file_name_pixels_between_red_cyan != []:
                list_three_dee.append(True)
                #Here only the digits are retained in the "re.findall", as only "[\d]" is parenthesized, as opposed to the above regex
                #expression, which includes "r" or "b"), in order to append the integer value of the number of pixels in-between the red and cyan channels.
                #Also, the "^d" is included in the regex expression to prevent "3" in "3d" from overriding the value of "pixels_between_red_cyan" for
                #this animation, as you can choose to only include "(3d)" in the animation file name to indicate that this animation is to be
                #rendered in anaglyph format with the default number of pixels between the red and cyan channels of 15, with the cyan layer
                #being on the right side.

                #The "if" statement excludes any file names having "(3d)", and the '.replace("3d", "")' method would allow for only "100" to be retained
                #in a file name containing "(3dR100)".
                if current_file_name_pixels_between_red_cyan[0] != "3d":
                    pixels_between_red_cyan_hits = re.findall(r"[r|b]?[ ]?([\d]+)[ ]?[r|b]?", current_file_name_pixels_between_red_cyan[0].replace("3d", ""))
                    if pixels_between_red_cyan_hits != []:
                        list_pixels_between_red_cyan.append(int(pixels_between_red_cyan_hits[0]))
                    else:
                        list_pixels_between_red_cyan.append(pixels_between_red_cyan)
                else:
                    list_pixels_between_red_cyan.append(pixels_between_red_cyan)

                #If "r" is present in "current_file_name_pixels_between_red_cyan[0]", it means that the red channel will
                #be located on the right of the anaglyph frames, and "True" will be appended to the list "list_red_right" for this animation.
                #Otherwise, the default color for the right layer is cyan, and "False" will be appended to "list_red_right".
                if "r" in current_file_name_pixels_between_red_cyan[0]:
                    list_red_right.append(True)
                else:
                    list_red_right.append(False)
            elif three_dee_flipbooks:
                list_pixels_between_red_cyan.append(pixels_between_red_cyan)
                list_red_right.append(red_right)
                list_three_dee.append(True)
            else:
                list_three_dee.append(False)
                #"None" needs to be appended to the lists
                #"list_pixels_between_red_cyan" and "list_red_right"
                #even if the animation is not to be generated in anaglyph
                #format, so that the indexing of this list works well for
                #the ones that are to be made into 3D flipbooks.
                list_pixels_between_red_cyan.append(None)
                list_red_right.append(None)

            #The presence of brightening percent values within the file names will be determined here,
            #and these values are appended in the list "list_brighten_percent". 'r"[(]([-]?[\d]+)[ ]?%[)]"'
            #means that only the digits will be retained (parenthesized in the regex expression, preceded
            #or not by a negative sign). If no brightening value was supplied in the file name
            #(which would override any default values for that file), then either the default
            #brightening value of "brighten_percent" of "None", or any other value specified
            #by the user after the "brighten:" argument when running the code will be
            #appended to the "list_brighten_percent" for that animation.
            current_file_brighten_percent = re.findall(r"[(]([-]?[\d]+)[ ]?%[)]", gif_names[i].lower())
            if current_file_brighten_percent != []:
                list_brighten_percent.append(int(current_file_brighten_percent[0])/100)
            else:
                list_brighten_percent.append(brighten_percent)

            #The files within the "GIF" folder are checked to see
            #whether they are of the same type as some of the most
            #common animated image formats ("gif", "webp", "apng",
            #"avif", "flif" and "mng"). If not, the "try, except"
            #statement below attempts extract the frames of the
            #video within the "start_time" and "end_time"
            #timestamps and save them as PNG images.
            file_path_split = gif_files[i].split(".")
            file_extension = file_path_split[-1].lower()
            gif_files_extensions.append(file_extension)
            #A "PNG" folder containing subfolders for every GIF is created.
            if not os.path.exists(os.path.join(cwd, "PNGS", gif_names[i])):
                os.makedirs(os.path.join(cwd, "PNGS", gif_names[i]))
            #The "path_pngs" path will be used to populate the "list gif_png_paths"
            #with the paths of all "PNG" files that will be extracted from the animations.
            path_pngs = os.path.join(cwd, "PNGS", gif_names[i], "*.png")

            if file_extension not in ["gif", "webp", "apng", "avif", "flif", "mng"]:
                try:
                    #Should the user wish to only convert a clip of the video
                    #into a flipbook, they must specify the starting and ending
                    #point of the clip by including them within parentheses.
                    #The numer of hours, minutes and seconds need to be separated
                    #by hyphens within these parentheses. For example, a clip of a MP4
                    #video starting at 1 hour 35 minutes and 5 seconds and ending at 1
                    #hour 35 minutes and 10 seconds would have the following
                    #parentheses: "A-videoname-(1-35-5)(1-35-10).mp4"
                    #The regex expression below (r"[(]([\d|-]+)[)]") only retains
                    #the contents of every parentheses in the file name. The users
                    #should then refrain from using parentheses other than when
                    #indicating the starting and ending points of the subclips and
                    #the number of pixels in-between the cyan and red channels of
                    #anaglyph frames.
                    start_end = re.findall(r"[(]([\d|-]+)[)]", gif_names[i])

                    #If there is more than one set of parenthesized expression containing
                    #only digits, it means that the user has supplied a staring and ending
                    #point to the subclip. They are then sorted (just in case the user
                    #has accidentally provided the stopping point before the starting point)
                    #and then each of them are split along hyphens to determine the number of
                    #hours, minutes and seconds that each time point corresponds to. These are
                    #then converted into seconds.
                    if len(start_end) > 1:
                        start_end.sort()
                        if "-" in start_end[0]:
                            start_time = [element.strip() for element in start_end[0].split("-")]
                            if len(start_time) > 2:
                                start_time = int(start_time[0])*3600 + int(start_time[1])*60 + int(start_time[2])
                            else:
                                start_time = int(start_time[0])*60 + int(start_time[1])
                        else:
                            start_time = int(start_end[0])

                        if "-" in start_end[1]:
                            end_time = [element.strip() for element in start_end[1].split("-")]
                            if len(end_time) > 2:
                                #1 second is subtracted from the total amount of seconds to make the interval exclusive of the "end_time"
                                end_time = int(end_time[0])*3600 + int(end_time[1])*60 + int(end_time[2])-1
                            else:
                                end_time = int(end_time[0])*60 + int(end_time[1])-1
                        else:
                            end_time = int(start_end[1])-1

                    #Should the user only have provided a starting point or and ending point (and not both),
                    #The following error message is provided.
                    elif len(start_end) == 1:
                        sys.exit('\nPlease specify both and start time and end time for your videoclip ' +
                        'by enclosing them within parentheses in your file name. The hours, seconds and ' +
                        'minutes need to be separated by a hyphen. \nFor example, a video clip starting at ' +
                        '1 hour 35 minutes and 5 seconds and ending at 1 hour 35 minutes and 10 seconds would ' +
                        'have the following parentheses: "A-videoname-(1-35-5)(1-35-10).mp4"')

                    #A "VideoCapture" object is instantiated.
                    video = cv2.VideoCapture(gif_files[i])
                    #The minimum number of frames per second between the default value of 25 (or the user-specified value)
                    #and the actual fps of the video is selected as the new value of "fps" (rounded up, as the video fps
                    #could be a float value), as the video cannot have more frames than its fps would allow.
                    video_frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                    video_fps = round(video.get(cv2.CAP_PROP_FPS))

                    fps = min(fps_setting, video_fps)

                    frame_durations.append(math.floor(1/fps*1000))
                    #The timestamps of the frames in-between the "start_time" and
                    #"end_time" are assembled in the list "frame_timestamps".
                    frame_timestamps = [start_time + x*1/fps for x in range((end_time-start_time+1)*fps)]
                    last_frame_timestamp = frame_timestamps[-1]
                    #The number of frames of the selected clip from the video is
                    #appended to the list "gif_number_of_frames". This needs to be
                    #done before the "for" loop below, given "frame_timestamps.pop(0)".
                    gif_number_of_frames.append(len(frame_timestamps))
                    #The following "for" loop loops through every frame
                    #of the video and selects those where the selected timestamps
                    #in "frame_timestamps" are smaller than the current loop timestamp,
                    #given by dividing the frame number by the actual video fps ("video_fps").
                    frame_counter = 0
                    for j in range(math.ceil(video_frame_count)):
                        frame_exists, frame = video.read()
                        if frame_timestamps and frame_timestamps[0] <= j/video_fps:
                            cv2.imwrite(os.path.join(cwd, 'PNGS', gif_names[i], gif_names[i] + "-" + str(frame_counter) + '.png'), frame)
                            frame_counter += 1
                            frame_timestamps.pop(0)
                        elif j/video_fps > last_frame_timestamp:
                            break
                    #The paths of the PNG files extracted from the GIFS are stored within the list "gif_png_paths".
                    #As the paths are strings, they need to be sorted numerically using a lambda function that
                    #splits the path strings along the hyphens, and indexing the last element, corresponding to
                    #the suffix (ex: 0.gif), and then excluding the extension and converting the resulting
                    #strings into integers.
                    gif_png_paths.append(sorted(glob.glob(path_pngs), key=lambda x:int(x.split("-")[-1].split(".")[0])))

                except Exception as e:
                    print(str(e))
                    sys.exit(file_extension + " files are not supported by this application." +
                    " Please use another file format such as GIF, WebP or MP4.")

            else:
                #The individual frames of every GIF are exported as PNG images
                #using the "Image.seek()" method to bring the GIF object to the
                #frame number "j".
                frame_durations.append([])
                with Image.open(gif_files[i]) as gif_object:
                    try:
                        for j in range(gif_object.n_frames):
                            gif_object.seek(j)
                            gif_object.save(os.path.join(cwd, 'PNGS', gif_names[i], gif_names[i] + "-" + str(j) + '.png'))
                            frame_durations[-1].append(int(gif_object.info['duration']))
                        #The paths of the PNG files extracted from the GIFS are stored within the list "gif_png_paths".
                        #As the paths are strings, they need to be sorted numerically using a lambda function that
                        #splits the path strings along the hyphens, and indexing the last element, corresponding to
                        #the suffix (ex: 0.gif), and then excluding the extension and converting the resulting
                        #strings into integers.
                        gif_png_paths.append(sorted(glob.glob(path_pngs), key=lambda x:int(x.split("-")[-1].split(".")[0])))
                        gif_number_of_frames.append(gif_object.n_frames)
                    except Exception as e:
                        print(str(e))
                        sys.exit(file_extension + " files are not supported for flipbook generation." +
                        " Please use another file format such as GIF or MP4.")
            bar()

    #The maximum number of frames for the longest
    #GIF is stored in "maximum_frame_number" and if
    #it is smaller or larger than "number_of_frames",
    #its value would be set to that of "number_of_frames".
    #This way, the user can truncate a GIF that has too
    #many frames or allow the GIFs to loop over until
    #the desired number of frames is reached.
    maximum_frame_number = max(gif_number_of_frames)

    if number_of_frames and maximum_frame_number != number_of_frames:
        maximum_frame_number = number_of_frames

    #The number of frames in every GIF is printed on screen to allow
    #the users to select GIFS of similar lengths for making flipbooks,
    #although this isn't striclty necessary, as the shorter GIFS will
    #simply be looped over until the "maximum_frame_number" is reached.
    print("\n\nHere are the number of frames and number of frames per second (fps) for your animated files:\n")
    gif_frame_duration_ms = []
    for i in range(len(gif_names)):
        #If the "frame_durations" at index "i" is a list, it means that
        #it is a GIF, as the durations for each frame were extracted, as
        #opposed to the frame duration of videos in milliseconds, which is
        #equivalent to 1/fps*1000. The "frame_durations[i] != []" is because
        #of the "try/except" statement above, in case the file type does not
        #have a "duration" element.
        if isinstance(frame_durations[i], list) and frame_durations[i] != []:
            animation_duration = sum(frame_durations[i])/1000
            animation_fps = round(gif_number_of_frames[i]/animation_duration)
        else:
            animation_fps = round(1/frame_durations[i]*1000)
        gif_frame_duration_ms.append(math.floor(1/animation_fps*1000))
        if frame_durations != []:
            print("- " + gif_names[i] + ": " + str(gif_number_of_frames[i]) + " frames, with a fps of " + str(animation_fps))
        else:
            print("- " + gif_names[i] + ": " + str(gif_number_of_frames[i]) + " frames")

    #The following nested "for" loops will populate the list
    #"png_index_list", which will determine when a shorter GIF
    #will need to loop over.
    png_index_list = []
    #The list "FrameNumber_PILImage" will contain the
    #3D frames for each animation that will be used to create a GIF
    #preview of the flipbook.
    FrameNumber_PILImage = []
    gif_indices_repeat = [0, 0, 0, 0, 0, 0, 0, 0]
    #For every new GIF, an empty list is appended to "png_index_list"
    #in order to add the PNG frame indices, up to the last index within
    #a given GIF, upon which it starts again at frame zero.
    #The list "gif_indices_repeat" (initialized at index zero
    #for each GIF) stores the current PNG frame indices. The
    #"gif_indices_repeat[i]" is added to the "png_index_list[-1]" list
    #in reverse order to make up for the fact that the first frame of
    #a flipbook is located at the bottom of it.
    for i in range(len(gif_png_paths)):
        png_index_list.append([])
        #A new empty list is appended for each animation, which will be
        #populated later in the code with the 3d frames with the red and
        #cyan channels separated by a certain number of pixels on the "x" axis.
        #Alternatively, if the 3D option isn't selected, the PIL image will
        #be appended instead.
        FrameNumber_PILImage.append([])
        for j in range(maximum_frame_number):
            if gif_indices_repeat[i] < len(gif_png_paths[i])-1:
                png_index_list[-1] = [gif_indices_repeat[i]] + png_index_list[-1]
                gif_indices_repeat[i] += 1
            else:
                png_index_list[-1] = [gif_indices_repeat[i]] + png_index_list[-1]
                if gif_indices_repeat[i] < len(gif_png_paths[i])-1:
                    gif_indices_repeat[i] += 1
                else:
                    gif_indices_repeat[i] = 0

    #If the user has included more than four GIFS within the "GIFS" subfolder
    #of the working folder, then the PNG frame indices within "png_index_list"
    #for odd-numbered GIFS will be reversed, as they GIFS will be printed on
    #both sides of the sheet of paper. That is to say that the GIFS on the two
    #sides of the page are progressing in opposite directions, as the flip book
    #needs to be "flipped" in order to watch the animation on the other side.
    if len(gif_files) > 4:
        for i in range(len(png_index_list)):
            if i%2 != 0:
                png_index_list[i] = png_index_list[i][::-1]

    print("\n\nCurrently generating a PDF document with a total of " + str(maximum_frame_number) + " frames.\n")
    with alive_bar(maximum_frame_number) as bar:
        #The width and height of the resized PNG images will be stored in the
        #list "gif_dimensions".
        gif_dimensions = []
        #The "unextended_gif_dimensions" will keep track of the original size of the frames
        #for a given animation, resized in order to fit within the available space on a
        #flipbook page. This will allow to crop the final anaglyph frames to remove the cyan
        #and red edges resulting from staggered red and cyan channels.
        #The "anaglyph_frame_dimensions" will factor in the extra pixels needed such that
        #the cropped frames would be equivalent in dimension to those generated for a non-3D
        #version of that animation.
        unextended_gif_dimensions = []
        anaglyph_frame_dimensions = []
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

        #Each frame will be saved as an individual PDF document, and these will
        #be merged together after the end of the "for i in range(maximum_frame_number):" loop.
        pdf_number = 0

        for i in range(maximum_frame_number):
            #A blank canvas (white US letter JPEG image, with a resolution of 300 ppi (2550x3300 px))
            #is generated for the first GIF and will contain frames from 4 different GIFS.
            blank_canvas = Image.open(os.path.join(cwd, "blank_canvas.jpg")).convert("RGB")
            blank_canvas_editable = ImageDraw.Draw(blank_canvas)
            #If there are more than four GIFS in "gif_files" it means that some of these will
            #be included on the reverse side of the pages. A reverse canvas therefore
            #needs to be created in order to pair up the GIF file names starting with
            #the same letters (ex: "a-name-1.gif" and "A-name-2.gif").
            if len(gif_files) > 4:
                blank_canvas_reverse = Image.open(os.path.join(cwd, "blank_canvas.jpg")).convert("RGB")
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

                    if list_three_dee[j] == True:
                        #If the flipbook will consist of anaglyph frames, the size needs to be scaled up to factor in
                        #the fact that the split cyan/red frames will need to be cropped to remove the red and cyan edges.
                        #The aspect ratio will allow to determine how many pixels to add to the height, so that the frames
                        #will be scaled up while retaining the aspect ratio.
                        aspect_ratio = height/width
                        frame_width = width + list_pixels_between_red_cyan[j]
                        height_pixel_adjustment = math.floor(list_pixels_between_red_cyan[j]*aspect_ratio)
                        frame_height = height + height_pixel_adjustment
                        gif_dimensions.append((frame_width, frame_height))
                        unextended_gif_dimensions.append((width, height))
                        anaglyph_frame_dimensions.append([frame_width + list_pixels_between_red_cyan[j], frame_height, height_pixel_adjustment])
                    #"None" needs to be appended to the lists "anaglyph_frame_dimensions"
                    #and "unextended_gif_dimensions" even if the animation is not to be
                    #generated in anaglyph format, so that the indexing of this list works
                    #well for the ones that are to be made into 3D flipbooks.
                    else:
                        anaglyph_frame_dimensions.append(None)
                        unextended_gif_dimensions.append(None)
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
                frame_k = Image.open(os.path.join(gif_png_paths[j][png_index_list[j][i]])).convert("RGB")

                #If "resize_factor" wasn't equal to one, it means that the PNG images for
                #the given GIF needs to be resized according to the updated width and height
                #values.
                if resize_factor != 1:
                    frame_k = frame_k.resize(gif_dimensions[j], resample=Image.Resampling.LANCZOS)

                #Flipbooks that are to be rendered in anaglyph 3D format may need to have their
                #frames brightened, as anaglyph images appear darker than regular frames. You may
                #specify a brightening ratio (inputted in percent form) specifically for a given
                #animation in its file name (parenthesized and followed by a percent symbol).
                #In addition to this, a brightening ratio may be specified for all animations other than
                #those that have a brightening ratio in their file name, by passing in the percent value after
                #the "brighten:" argument (example "brighten:50%" would brighten the frames by 50%, while -50%
                #would darken the frames by 50%).

                #By default, the extracted frames of the animations are not brightened in
                #creating the flipbooks. You may specify a brightening value applied to all
                #frames of all animations by passing in the percentage value after the "brighten:"
                #argument (ex: "brighten:70%" to brighten all frames of all animations by 70%),
                #or indicate the brightening value for a specific animation in its file name
                #(ex: "my_animation (-40%).gif", in which case this specific animation would be
                #darkened by 40%, the darkening being a result of the negative sign).
                if list_brighten_percent[j] != None:
                    brightener = ImageEnhance.Brightness(frame_k)
                    #The "1 + list_brighten_percent[j]" enables the image to be brightened if the value
                    #of list_brighten_percent[j] is positive (the sum being superior to one) and darkened
                    #if the value of list_brighten_percent[j] is negative (the sum being inferior to one).
                    frame_k = brightener.enhance(1+list_brighten_percent[j])

                if list_three_dee[j] == True:
                    #A new canvas larger on the horizontal axis than "frame_k" is created
                    #to accomodate for the larger space required for both red and cyan
                    #channels, which are staggered horizontally by a number of pixels equivalent to
                    #list_pixels_between_red_cyan[j], with the position of the red frame being on the
                    #right if list_red_right[j] == True.
                    anaglyph_frame = Image.new("RGB", anaglyph_frame_dimensions[j][:2], (255,255,255))

                    cyan_frame = frame_k.copy()
                    cyan_frame = np.array(cyan_frame)
                    #For the cyan frame, the "R" channel (channel index 0 for
                    #every "y" and "x" coordinates in the numpy array of the image) is
                    #converted to zero.
                    cyan_frame[:,:,0] *=0
                    #The numpy array is then converted back to a PIL image object.
                    cyan_frame = Image.fromarray(cyan_frame)

                    red_frame = frame_k.copy().convert("RGBA")
                    red_frame.putalpha(127)
                    red_frame = np.array(red_frame)
                    #For the red frame, the "G" and "B" channels (channel indices 1 and 2 for
                    #every "y" and "x" coordinates in the numpy array of the image) are
                    #converted to zero.
                    red_frame[:,:,1:3] *= 0
                    red_frame = Image.fromarray(red_frame)

                    if list_red_right[j] == False:
                        #If list_red_right[j] == False, it means that the cyan channel needs to
                        #be on the right, offset by list_pixels_between_red_cyan[j] pixels on the
                        #"x" axis.
                        anaglyph_frame.paste(cyan_frame, (list_pixels_between_red_cyan[j], 0))
                        anaglyph_frame.paste(red_frame, (0, 0), red_frame)
                    else:
                        #The reverse is true if list_red_right[j] == True
                        anaglyph_frame.paste(red_frame, (list_pixels_between_red_cyan[j], 0))
                        anaglyph_frame.paste(cyan_frame, (0, 0), red_frame)

                    #The red and cyan portions at the edges of the image are cropped out, with the
                    #cropped frame now being equivalent in size to that of a non-anaglyph frame for
                    #that animation.
                    frame_k = anaglyph_frame.crop((list_pixels_between_red_cyan[j],
                    math.floor(0.5*height_pixel_adjustment), list_pixels_between_red_cyan[j] + unextended_gif_dimensions[j][0],
                    math.floor(0.5*height_pixel_adjustment) + unextended_gif_dimensions[j][1]))

                #The current frame index followed by the PIL image of the frame "frame_k"
                #are appended to "FrameNumber_PILImage"
                FrameNumber_PILImage[j].append([png_index_list[j][i], frame_k])

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

            #The frame number in the top of each quadrant in order to facilitate flipbook assembly.
            #The function below creates an image with the number text, which will be pasted over
            #the "blank_canvas" and "blank_canvas_reverse". Such a function is used instead of
            #writing directly on "blank_canvas" and "blank_canvas_reverse", since two of the
            #numbers need to be flipped.
            def text_image(number, numbers_font):
                page_number_box = numbers_font.getbbox(str(number))
                page_number_size = [math.floor((page_number_box[2]-page_number_box[0])*2),
                math.floor((page_number_box[3]-page_number_box[1])*2)]
                page_number_text = Image.new('RGBA', page_number_size, (255, 255, 255, 0))
                page_number_text_editable = ImageDraw.Draw(page_number_text)
                page_number_text_editable.text((math.floor(page_number_size[0]/2), math.floor(page_number_size[1]/2)),
                str(number), font=numbers_font, fill="LightSlateGrey", anchor="mm")
                return page_number_text, page_number_size

            #The number text images are pasted onto "blank_canvas" in the top of each flipbook page,
            #with central horizontal alignment. The numbers of the upper two quadrants need to be
            #flipped (rotated 180 degrees), as the GIF frames are also flipped in these quadrants.
            #The page numbering corresponds to "maximum_frame_number-i", as the last frame is printed
            #first on odd-numbered pages of the PDF document.
            page_number_text, page_number_size = text_image(maximum_frame_number-i, numbers_font)
            page_number_half_width = page_number_size[0]/2
            blank_canvas.paste(page_number_text.rotate(180), (math.floor(2550*0.25-page_number_half_width), math.floor(3300/2-border-page_number_size[1])))
            blank_canvas.paste(page_number_text.rotate(180), (math.floor(2550*0.75-page_number_half_width), math.floor(3300/2-border-page_number_size[1])))
            blank_canvas.paste(page_number_text, (math.floor(2550*0.25-page_number_half_width), math.floor(3300/2+border)))
            blank_canvas.paste(page_number_text, (math.floor(2550*0.75-page_number_half_width), math.floor(3300/2+border)))

            #The numbers text images are pasted onto "blank_canvas_reverse" only if there are more than four GIFs,
            #meaning that they will be printed on both sides of the page. However, the ordering is reversed, so the
            #number written on "blank_canvas_reverse" corresponds to "i+1".
            if len(gif_files) > 4:
                page_number_text, page_number_size = text_image(i+1, numbers_font)
                page_number_half_width = page_number_size[0]/2
                blank_canvas_reverse.paste(page_number_text.rotate(180), (math.floor(2550*0.25-page_number_size[0]/2), math.floor(3300/2-border-page_number_size[1])))
                blank_canvas_reverse.paste(page_number_text.rotate(180), (math.floor(2550*0.75-page_number_size[0]/2), math.floor(3300/2-border-page_number_size[1])))
                blank_canvas_reverse.paste(page_number_text, (math.floor(2550*0.75-page_number_half_width), math.floor(3300/2+border)))
                blank_canvas_reverse.paste(page_number_text, (math.floor(2550*0.25-page_number_half_width), math.floor(3300/2+border)))

            #The "blank_canvas" and "blank_canvas_reverse" images are scaled according to the "pdf_resolution" dpi value,
            #taking into account that the initial canvas pixel size was 2550x3300 px for a 300 dpi canvas (typical quality
            #used in professional printing jobs).
            blank_canvas = blank_canvas.resize((round(2550*pdf_resolution/300), round(3300*pdf_resolution/300)), resample=Image.Resampling.LANCZOS)
            if len(gif_files) > 4:
                blank_canvas_reverse = blank_canvas_reverse.resize((round(2550*pdf_resolution/300), round(3300*pdf_resolution/300)), resample=Image.Resampling.LANCZOS)

            #The path "pdf_path" will store the separate PDF files for each frame,
            #and the merging of the PDF files will be done using the PdfMerger Class
            #from the pyPDF module, as otherwise the assembly of a large PDF file is
            #quite lengthy towards the end of the process with PIL, as the file rapidly
            #becomes too large.
            pdf_path = os.path.join(cwd, str(date.today()) + " flipbook", "PDF_parts")
            if not os.path.exists(pdf_path):
                os.makedirs(pdf_path)
            pdf_number += 1
            blank_canvas.save(os.path.join(pdf_path, str(date.today()) + " flipbook-" + str(pdf_number) + ".pdf"), resolution=pdf_resolution)
            #If there are more than four GIFs being converted into flipbooks, then it
            #means that at least one of them will be found on the reverse pages. The
            #frame of the reverse page ("blank_canvas_reverse") is then saved as a PDF file.
            if len(gif_files) > 4:
                pdf_number += 1
                blank_canvas_reverse.save(os.path.join(pdf_path, str(date.today()) + " flipbook-" + str(pdf_number) + ".pdf"),
                append=False, resolution=pdf_resolution)

            bar()

    final_pdf_path = os.path.join(cwd, str(date.today()) + " flipbook")
    #The list returned by "glob" is sorted, such that the number suffixes directly
    #preceding the ".pdf" file extension may be assembled in sequence in the resulting list.
    #For example: "['2023-10-05 flipbook-1.pdf', '2023-10-05 flipbook-2.pdf',
    #'2023-10-05 flipbook-3.pdf']. This is important in order merge the PDF documents
    #in the correct order.
    pdf_files = sorted(glob.glob(os.path.join(pdf_path, "*.pdf")), key=lambda x: int(x.split("-")[-1].split(".")[0]))
    pdf_merger = PdfMerger()
    for path in pdf_files:
        pdf_merger.append(path)
    pdf_merger.write(os.path.join(cwd, str(date.today()) + " flipbook", str(date.today()) + " flipbook.pdf"))

    #The folder containing the separate PDF parts is deleted.
    shutil.rmtree(os.path.join(pdf_path))

    #Lastly, the "PNGS" folder containing the PNGs and its contents is deleted.
    shutil.rmtree(os.path.join(cwd, "PNGS"))

    #The GIFS are created to give an preview of the finished flipbooks.
    for i in range(len(gif_names)):
        #If the first frame of the animation is located at the index 0 of "FrameNumber_PILImage[i]",
        #and the second frame is found at index 1 of "FrameNumber_PILImage[i]", then it means that
        #the frames are in increaing order and do not need to be reversed in creating the GIFS. It that is
        #not the case (the last frame of the flipbook could land on the first frame at index 0 if the GIF
        #repeats), then the frames will be assembled in reverse order to create the GIF.
        if FrameNumber_PILImage[i][0][0] == 0 and FrameNumber_PILImage[i][1][0] == 1:
            FrameNumber_PILImage[i] = [FrameNumber_PILImage[i][j][1] for j in range(0,gif_number_of_frames[i])]
        else:
            FrameNumber_PILImage[i] = [FrameNumber_PILImage[i][j][1] for j in range(gif_number_of_frames[i]-1, -1, -1)]
        print('\nCurrently generating the GIF for the animation: "' + gif_names[i] + '".')
        #The GIF is saved, with the "FrameNumber_PILImage" containing all of the frames, and "image_sequence_duration"
        #listing their duration in milliseconds.
        FrameNumber_PILImage[i][0].save(os.path.join(final_pdf_path, gif_names[i] + '.gif'), save_all=True,
        append_images=FrameNumber_PILImage[i][1:], duration = gif_frame_duration_ms[i], loop = 0)

else:
    print("Please include between one and eight GIF files inclusively within the GIFS folder.")
