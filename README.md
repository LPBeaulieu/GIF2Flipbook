# GIF2Flipbook
This application lets you create up to eight flipbooks at a time from videos, GIFs and other animated image formats!

<p align="center">
  <img src="https://github.com/LPBeaulieu/GIF2Flipbook/blob/main/BettyBoopDemo.gif" alt="Betty Boop flipbook GIF" />
</p>
<h3 align="center">GIF2Flipbook</h3>
<div align="center">
  
  [![License: AGPL-3.0](https://img.shields.io/badge/License-AGPLv3.0-brightgreen.svg)](https://github.com/LPBeaulieu/GIF2Flipbook/blob/main/LICENSE)
  [![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
  [![macOS](https://svgshare.com/i/ZjP.svg)](https://svgshare.com/i/ZjP.svg)
  [![Windows](https://svgshare.com/i/ZhY.svg)](https://svgshare.com/i/ZhY.svg)
 
</div>

---

<p align="left"> <b>GIF2Flipbook</b> is a tool enabling you to create up to eight flipbooks at a time from videos, GIFs and other animated image formats, such as WebP files. Simply place you files within the designated folder and run the code, and you will soon have a PDF document ready for printing! 

A neat feature of this app is that you can "pair up" two different animations of your choosing on opposite sides of the flipbooks, so that you can continue on flippipng on the other side!
<br> 
</p>

## 📝 Table of Contents
- [Dependencies / Limitations](#limitations)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Author](#author)
- [Acknowledgments](#acknowledgments)

## ⛓️ Dependencies / Limitations <a name = "limitations"></a>
- It is important that the file names of the animated files that you will add to the "GIFS" folder within your working folder only contain letters,  numbers and hyphens, without any special characters or spaces (except for videos, more on that later), to enable the code to properly extract the file names. 

- The flipbook frames are printed in the corners of 8 1/2 by 11 inch pages, with a default margin measuring 0.25 inch. The first four animations that you generate simultaneously will be created in the four corners of a sheet of paper. However, when "pairing up" two different animations on opposite sides of a flipbook, you would need to print at least five animations at a time, such that they would be printed on both sides of the sheet of paper. Simply add a prefix consisting of the same letter and a hyphen at the start of the two paired animation file names (for example: "A-file1.gif and A-file2.gif"). You should then print your flipbooks in duplex mode, flipping on the long edge of the paper. Should you print double sided flipbooks on an inkjet printer, I would recommend using 24 lb or heavier grade paper, in order to limit ink bleeding to the other side of the sheet.


## 🏁 Getting Started <a name = "getting_started"></a>

The following instructions will be provided in great detail, as they are intended for a broad audience and will allow to run a copy of GIF2Flipbook on a local computer.

The instructions below are for Windows operating systems, but the code runs very nicely on Linux as well.

Start by downloading the zipped working folder, by going to the top of this github repo and clicking on the green "Code" button, and then click on the "Download Zip" option. Extract the zipped folder to your desired location. Next, hold the "Shift" key while right-clicking in your working folder, then select "Open PowerShell window here" to access the PowerShell in your working folder and enter the commands described below. Make sure that you keep the "GIFS" folder within your working folder, in which you will place between 1 and 8 videos, GIFs or other animated image files that you wish to convert into flipbooks.

<b>Step 1</b>- Install <b>Pillow</b> (Python module to handle the GIFS and other animated image files) using the following command:

```
py -m pip install --upgrade Pillow
```

<b>Step 2</b>- Install <b>OpenCV</b> (Python module to extract the frames of a video):
```
py -m pip install opencv-python
```

<b>Step 3</b>- Install <b>NumPy</b> (Python module handle the video frame timestamp data):
```
py -m pip install numpy
```

<b>Step 4</b>- Install <b>alive-Progress</b> (Python module for a progress bar displayed in command line):
```
py -m pip install alive-progress
```

<b>Step 5</b>- You're now ready to use <b>GIF2Flipbook</b>! 🎉

## 🎈 Usage <a name="usage"></a>
- As mentioned above, videos may also be converted into flipbooks. It is recommended to either select very short videos (less than 10 seconds) or a subclip of your favorite scene, as the number of frames adds up very quickly the longer the animation is. The default number of frames per second is set to 25 fps, and you can change it by inputting the fps of your choosing after the "fps:" argument when running the code. Should you only wish to convert a subclip of a video into a flipbook, you would then need to specify the starting and ending points of the clip by including them within parentheses in the video file name. The number of hours, minutes and seconds need to be separated by hyphens within these parentheses. For example, a MP4 video starting at 1 hour 35 minutes and 5 seconds and ending at 1 hour 35 minutes and 10 seconds would have the following file name (note the parentheses): "A-YourVideoName-(1-35-5)(1-35-10).mp4". As such, you should refrain from using parentheses in the file names, other than when indicating the starting and ending points of the subclips.

- Simply place between 1 and 8 animation files that you wish to convert into flipbooks into the "GIFS" subfolder within your working folder and enter the following in the Powershell within your working folder:
```
py gif2flipbook.py
```
Depending on the number of frames of your animations, it may take several minutes for the code to generate your PDF file, which may be very large in size.  

- The animation with the maximal number of frames will be selected to determine the numbert of pages in the PDF document, with the shorter animations looping over and over until the longest one completes. You can also input the number of frames that you wish the flipbooks to contain if you want a truncated or prolonged flipbook. Simply pass in the number of frames after the "number_of_frames:" argument when running the code.

- The size of the border (default of 0.25 inch) may be changed to another value. Simply pass in the number of inches (in decimal form and without units) after the "border:" argument. For borderless printing, enter "border:0" when running the code.

- The frames are automatically resized (either shrunk down or blown up) so that they could fit within the available space in every quadrant of the page. Should you not wish for their size to be increased, pass in the following argument when running the code: "no_size_increase".

- Two orthogonal central lines are drawn on one side of every sheet of paper to facilitate cutting the pages when you are assembling your flipbook. Make sure to line up the pages nicely along the precut edges (long and short sides of the 8 1/2 by 11 inch pages) so that the flipbook pages flip smoothly. Should you be using perforated printing paper, effectively dispensing you from needing to use scissors, you could then remove these lines by passing in the "no_lines" argument when running the code.

- Make sure that you include a space in-between arguments, and that you place each argument within quotes when running the Python code (for example: py gif2flipbook.py "border:0.5" "number_of_frames:100" "no_lines").   

- Flipbook page numbers are provided to help you assemble the flipbooks. Please keep in mind that the first page should be at the bottom of the flipbook, facing up, as it is the first frame that you will see when flipping the pages.

- Please be careful not to confuse the PDF page numbers with the frame numbers printed on the flipbook pages when printing your document.

- Once you are done printing and cutting your pages, you can perforate the pages and bind them with 1 inch plastic binder rings. Despite my shoddy scissor work, the flipbooks still turned out great!

![Figure 1](https://github.com/LPBeaulieu/GIF2Flipbook/blob/main/Flipbook%20binding.jpg)<hr> <b>Figure 1.</b> Simply bind your perforated page with binder rings for very nifty looking flipbooks!
        
<br><b>And there you have it!</b> You're now ready to convert your favorite videos and animated images into analog flipbook format! You can now enjoy your favorite animations when your phone's battery is dead or your internet connection is down! 📽📇
  
  
## ✍️ Authors <a name = "author"></a>
- 👋 Hi, I’m Louis-Philippe!
- 👀 I’m interested in natural language processing (NLP) and anything to do with words, really! 📝
- 🌱 I’m currently reading about deep learning (and reviewing the underlying math involved in coding such applications 🧮😕)
- 📫 How to reach me: By e-mail! LPBeaulieu@gmail.com 💻


## 🎉 Acknowledgments <a name = "acknowledgments"></a>
- Hat tip to [@kylelobo](https://github.com/kylelobo) for the GitHub README template!


<!---
LPBeaulieu/LPBeaulieu is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->
