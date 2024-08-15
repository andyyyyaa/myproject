# Golf Motion Analysis
This is a program that can analysis people's slow golf motion and conpare it to Tiger Woods' swing and rate the similarity of their movement. This program can help you improve the swing and do better in golf.
# DIRECTION 
1, Download the Jetson-Inference package to run the code

2, drag the slow motion video of the golf swing in the front of you face to the directory(myproject)

 $ cd myproject 
 
3, run the code in VScode

4, There will be a hint that tells you to type in the file name and it can output a vedio with the posenet and rate the similarity with Tiger's motion
# Algorithm
The program uses the posenet and the cosine similarity algorithm, I can use it to compare the angle of each part of the body's articulation and find whether it overlaps.
# Jetson-Inference
https://github.com/andyyyyaa/jetson-inference
# Example
you can have a look of the example output in annotated_output.mp4 but make sure to delete the annotated_output.mp4 befor you run the code
