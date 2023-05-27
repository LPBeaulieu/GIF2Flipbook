# GIF2Flipbook
This application lets you create up to eight flipbooks at a time from GIFs and other animated image formats!

![Image RTF basic mode](https://github.com/LPBeaulieu/Typewriter-OCR-TintypeText/blob/main/TintypeText%20basic%20rtf%20mode%20screenshot.jpg)
<h3 align="center">Tintype¶Text</h3>
<div align="center">
  
  [![License: AGPL-3.0](https://img.shields.io/badge/License-AGPLv3.0-brightgreen.svg)](https://github.com/LPBeaulieu/TintypeText/blob/main/LICENSE)
  [![GitHub last commit](https://img.shields.io/github/last-commit/LPBeaulieu/TintypeText)](https://github.com/LPBeaulieu/TintypeText)
  [![GitHub issues](https://img.shields.io/github/issues/LPBeaulieu/TintypeText)](https://github.com/LPBeaulieu/TintypeText)
  
</div>

---

<p align="left"> <b>GIF2Flipbook</b> is a tool enabling you to create up to eight flipbooks at a time from GIFs and other animated image formats. Simply place you GIFs in the designated folder within the working folder and run the code from command line, and you will soon have a PDF document ready for printing! 

A neat feature of this app is that you can "pair up" two different GIFs of your choosing on opposite sides of the flipbooks!
<br> 
</p>

## 📝 Table of Contents
- [Dependencies / Limitations](#limitations)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Author](#author)
- [Acknowledgments](#acknowledgments)

## ⛓️ Dependencies / Limitations <a name = "limitations"></a>
- It is important that the file names of the GIFs that you will add to the "GIFS" folder within the working folder only contain letters,  numbers and hyphens, without any special characters or spaces, to enable the code to properly extract the file names. 

- The GIFs are printed in the corners of 8 1/2 by 11 inch pages, with a default margin measuring half an inch. The first four GIFs that you generate simultaneously will be created in the four corners of a sheet of paper. However, when "pairing up" two different GIFs on opposite sides of a flipbook, you need to print at least five GIFs at a time, such that they would be printed on both sides of the sheet of paper. Simply add a prefix consisting of the same letter and a hyphen at the start of the two paired GIF file names (for example: "A-file1.gif and A-file2.gif").


## 🏁 Getting Started <a name = "getting_started"></a>

The following instructions will be provided in great detail, as they are intended for a broad audience and will allow to run a copy of GIF2Flipbook on a local computer.

The instructions below are for Windows operating systems, but the code runs very nicely on Linux.

Start by downloading the zipped working folder by going to the top of this github repo and clicking on the green "Code" button, and then click on the "Download Zip" option. Extract the zipped folder to your desired location. Then, hold the "Shift" key while right-clicking in your working folder, then select "Open PowerShell window here" to access the PowerShell in your working folder and enter the commands described below. Make sure that you keep the "GIFS" folder within your working folder, in which you will place between 1 and 8 GIFs that you wich to convert into flipbooks.

<b>Step 1</b>- Install <b>Pillow</b> (Python module to handle the GIFS and other animated image files) using the following command:

```
py -m pip install --upgrade Pillow
```

<b>Step 2</b>- Install <b>alive-Progress</b> (Python module for a progress bar displayed in command line):
```
py -m pip install alive-progress
```

<b>Step 3</b>- You're now ready to use <b>GIF2Flipbook</b>! 🎉

## 🎈 Usage <a name="usage"></a>
- Simply place between 1 and 8 GIFs that you wish to convert into flipbooks into the "GIFS" subfolder within your working folder and enter the following in Powershell within your working folder:
```
py gif2flipbook.py
```
Depending on the number of frames of your GIFs, it may take a few minutes for the code to generate your PDF file.  

- The GIF with the maximal number of frames will be selected to determine the numbert of pages in the PDF document, with the shorter GIFs looping over and over until the longest one completes. You can also input the number of frames that you wish the flipbooks to contain if you want an even longer number of frames than the longest GIF contains. Simply pass in the number of frames after the "minimum_frame_number:" argument when running the code.

- The size of the border (default of 0.25 inch) may be changed to another value. Simply pass in the number of inches (in decimal form and without units) after the "border:" argument.

- The GIFs are automatically resized (either shrunk down or blown up) so that they could fit within the available space in every quadrant of the page. Should you not wish for their size to be increased, pass in the following argument when running the code: "no_size_increase".

- A horizontal and vertical central lines are drawn on one side of every sheet of paper to facilitate cutting them when you are assembling your flipbook. Make sure to line up the pages nicely along the precut edges (long and short sides of the 8 1/2 by 11 inch pages) so that the flipbook will flip smoothly. Should you be using perforated printing paper dispensing you from needing to use scissors, you could avoid having these lines by passing in the "no_lines" argument when running the code.

- Make sure that you include a space in-between arguments and that you frame each argument in quotes when running the Python code (for example: py gif2flipbook.py "border:0.5" "minimum_frame_number:100" "no_lines".   

        
<br><b>And there you have it!</b> You're now ready to convert your favorite GIFs in analog flipbook format! You can now watch your favorite GIFs even when your phone's battery is dead or your internet connection is down! 📽📇
  
  
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
