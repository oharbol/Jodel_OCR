from typing import OrderedDict
from PIL import Image
import cv2
from time import sleep
import numpy as np
import subprocess
from Alphabet_Soup import *
import time

#The custom OCR utilized directly for images of Jodel
#Requires Android Phone to take screenshots

class Custom_OCR:
    
    #Constructor
    def __init__(self, filename_pre = "./raw_image.png", filename_post = "./processed_image.png"):
        self.X_DIMS = (0, 942)
        self.Y_DIMS = (400, 1287)
        self.filename_pre = filename_pre
        self.filename_post = filename_post
        self.BLACK = [0, 0, 0]
        self.WHITE = 255
    

    #Refreashes page, takes screenshot,
    def ScreenShot(self):
        #Refreash the page
        subprocess.call('adb shell input swipe 500 500 500 1000', shell=True)

        #ensures page refreashes before taking screenshot
        sleep(5)

        #Take screenshot
        subprocess.call('adb exec-out screencap -p > ./{}'.format(self.filename_pre), shell=True)


    #Converts the raw image into a black and white image
    def Process_Image(self):
        # Read image with opencv
        img = cv2.imread(self.filename_pre)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Write the image after apply opencv to do some ...

        new_img = thresh[400:1687, 0:942]

        cv2.imwrite(self.filename_post, new_img)
        # Remove template file
        #os.remove(temp)
        return new_img


    #Runs horizontal lines from left to right
    #until an empty space is reached
    def Find_Line(self, y_start, img):
        stop = False
        y = y_start
        y_upper, y_lower = 0, 0
        #loop until start and end of line is found or the max y value is hit
        while(not stop and y < self.Y_DIMS[1]):
            #upper bound found
            if((y_upper == 0) and np.isin(self.BLACK, img[y]).all()):
                y_upper = y
            #lower bound found
            if(y_upper != 0 and not np.isin(self.BLACK, img[y]).all()):
                y_lower = y
                stop = True
            #increment current y value
            y += 1
        
        if ((y_upper, y_lower) != (0,0)):
            return y_upper, y_lower + 1 #the y_lower + 1 is to compensate for different sized letters
        else: 
            return self.Y_DIMS[1], self.Y_DIMS[1]


    #Searches a given y boundary for all letters, numbers and special chars
    #Brute Force Method
    def Search_Line(self, y_upper, y_lower, img):
        #holds all tuples of (x, y, letter)
        line_data = []

        #image of the line
        #line_img = img[y_upper:y_lower, self.X_DIMS[0]:self.X_DIMS[1]]

        for i in master_key:
            dictionary, dictionary_dims = self.Find_Dictionary(i)
            x_offset, y_offset = 0, 0
            while(y_offset + dictionary_dims[i][0] + y_upper <= y_lower):
                #print((y_offset + dictionary_dims[i][0], max_y))
                new_img = img[y_offset:y_offset + dictionary_dims[i][0], x_offset:x_offset + dictionary_dims[i][1]]
                # if(i=="_" and y_offset + dictionary_dims[i][0] + y_upper == y_lower):
                    # cv2.imshow("picture{}".format(i), new_img)
                    # cv2.waitKey(0)

                #Check that image is inside 
                img_inside, index = self.Search_Block(i, new_img, dictionary)
                if(img_inside):
                    line_data.append((x_offset, y_offset, i))
                    #print("Match!!{}".format((x_offset, y_offset, i)))
                    img = self.PaintItWhite(i, (y_offset,x_offset), img, dictionary, index)
                    # cv2.imshow("picture{}".format(i), img)
                    # cv2.waitKey(0)
                #iterate offsets
                x_offset += 1
                if(x_offset + dictionary_dims[i][1] >= self.X_DIMS[1]):
                    x_offset = 0
                    y_offset += 1

        return line_data

        
    #Finds what dictionary to use for a given letter
    def Find_Dictionary(self, letter):
        dictionary = {}
        dictionary_dims = {}

        #find what dictionary to use
        if(letter.isalpha()):
            dictionary = alphabet
            dictionary_dims = alpahbet_dims
        elif(letter.isdigit()):
            dictionary = numbers
            dictionary_dims = numbers_dims
        else:
            dictionary = special_chars
            dictionary_dims = special_char_dims
        
        return dictionary, dictionary_dims

    #Checks the given letter at the specified x, y coordiante or image
    def Search_Block(self, letter, img, dictionary):
        broke = False
        index = 0

        for bitmaps in dictionary[letter]:
            broke = False
            length = len(bitmaps)
            tmp = length
            for i in bitmaps:
                if((img[i[0], i[1]] == self.WHITE)):
                    broke = True
                    #break
                    #return not broke, index
                    tmp -= 1
            #check if 
            # if(not broke):
            #     return not broke, index
            if(tmp / length > 0.9):
                return not broke, index
            index += 1

        #returns the index of the bitmap for the given letter
        return not broke, index

    #Paints the given letter found as white in place of the black pixels
    #(y_off,x_off)
    def PaintItWhite(self, letter, offset, img, dictionary, index):
        for i in dictionary[letter][index]:
            img[offset[0]+i[0],offset[1]+i[1]] = 255

        return img

    #Takes the coordinate data and translates it into a readable string
    def Organize_LineData(self, line_data):
        #created ordered list w/o spaces
        ordered_data = self.MergeSort(line_data)
        line = ""
        for i in range(len(ordered_data)):
            #ordered_data = (x,y,letter)
            _, diction = self.Find_Dictionary(ordered_data[i-1][2])

            #find gaps and add space to line
            #if(i > 1 and ordered_data[i][0] - (ordered_data[i-1][0] + diction[ordered_data[i-1][2]][1]) > 10):
            if(ordered_data[i][0] - (ordered_data[i-1][0] + diction[ordered_data[i-1][2]][1]) > 10):
                line += " "

            line += ordered_data[i][2]

            
        return line


    #Check for "@main." Signals start of post data
    #Note: Might not be needed since start and end are implied
    def Contains_Title(self, y_upper, y_lower, img):
        #holds all tuples of (x, y, letter)
        line_main = False
        main_str = "main_title"
        main_str_dims = "main_title_dims"
        x_offset, y_offset = 0, 0
        #image of the line
        #line_img = img[y_upper:y_lower, self.X_DIMS[0]:self.X_DIMS[1]]

        while(y_offset + titles[main_str_dims][0] + y_upper <= y_lower and not line_main):
            #print((y_offset + dictionary_dims[i][0], max_y))
            new_img = img[y_offset:y_offset + titles[main_str_dims][0], x_offset:x_offset + titles[main_str_dims][1]]

            #Check that image is inside 
            img_inside, index = self.Search_Block(main_str, new_img, titles)
            if(img_inside):
                line_main = True

            #iterate offsets
            x_offset += 1
            if(x_offset + titles[main_str_dims][1] >= self.X_DIMS[1]):
                x_offset = 0
                y_offset += 1

        return line_main


    #Checks for "..." Signals end of post data
    def Contains_Footer(self, y_upper, y_lower, img):
        #holds all tuples of (x, y, letter)
        line_main = False
        main_str = "footer"
        main_str_dims = "footer_dims"
        x_offset, y_offset = 0, 0
        #image of the line
        #line_img = img[y_upper:y_lower, self.X_DIMS[0]:self.X_DIMS[1]]

        while(y_offset + titles[main_str_dims][0] + y_upper <= y_lower and not line_main):
            #print((y_offset + dictionary_dims[i][0], max_y))
            new_img = img[y_offset:y_offset + titles[main_str_dims][0], x_offset:x_offset + titles[main_str_dims][1]]

            #Check that image is inside 
            if(self.Search_Block(main_str, new_img, titles)):
                line_main = True

            #iterate offsets
            x_offset += 1
            if(x_offset + titles[main_str_dims][1] >= self.X_DIMS[1]):
                x_offset = 0
                y_offset += 1

        return line_main

    #Dr.O I promise to make you proud!!!
    #O(nlog(n))
    def MergeSort(self, data):
        if(len(data) <= 1):
            return data
        
        half = len(data) // 2

        first = self.MergeSort(data[0:half])
        second = self.MergeSort(data[half:len(data)])
        ordered_list = []

        for i in range(0, len(first)+len(second)):
            if(len(first) == 0):
                ordered_list += second
                return ordered_list
            elif(len(second) == 0):
                ordered_list += first
                return ordered_list
            else:
                #for the original merge sort
                #if(first[0][1] < second[0][1]):
                if(first[0][1] < second[0][1]):
                    ordered_list.append(first.pop(0))
                else:
                    ordered_list.append(second.pop(0))
        return ordered_list



#Tests
######

    """
    if(test == 0):
        start = time.time()
        #First functions
        #filename_pre = "./processed_image.png"
        tester = Custom_OCR()


        #Screen shot and saved image
        tester.ScreenShot()
        img = tester.Process_Image()
        #img = cv2.imread("./abcimage")
        #print(img[0])
        

        y_up, y_lo = 0, 0
        main_found = False
        footer_found = False
        line_data = ""

        #main line
        #Second line
        # y_up, y_lo = tester.Find_Line(y_lo, img)

        # line_img = img[y_up:y_lo, 0:942]
        # # cv2.imshow("picture{}".format("a"), line_img)
        # # cv2.waitKey(0)
        # print(tester.Contains_Title(y_up, y_lo, line_img))
        y_up, y_lo = tester.Find_Line(y_lo, img)
        line_img = img[y_up:y_lo, 0:942]


        #first line
        for i in range(15):
            y_up, y_lo = tester.Find_Line(y_lo, img)

            line_img = img[y_up:y_lo, 0:942]
            # cv2.imshow("picture{}".format("a"), line_img)
            # cv2.waitKey(0)

            thingy = tester.Search_Line(y_up, y_lo, line_img)
            print(tester.Organize_LineData(thingy))
        end = time.time()
        print("\ntime {:.2f} sec(s)".format(end - start))
        """
    ##########################################################
    #loop until main is found or max y is reached
    # while(y_lo < tester.Y_DIMS[1]):
    #     main_found = False
    #     footer_found = False
    #     line_data = ""
    #     #find next line 
    #     y_up, y_lo = tester.Find_Line(y_lo, img)

    #     line_img = img[y_up:y_lo, 0:942]

    #     if((y_up, y_lo) == (tester.Y_DIMS[1], tester.Y_DIMS[1])):
    #         break
    #     #Find first @main instance
    #     main_found = tester.Contains_Title(y_up, y_lo, line_img)

    #     #loop until footer is found 
    #     while(y_lo < tester.Y_DIMS[1] and main_found and not footer_found):
    #         #find next line
    #         y_up, y_lo = tester.Find_Line(y_lo, img)

    #         if((y_up, y_lo) == (tester.Y_DIMS[1], tester.Y_DIMS[1])):
    #             break

    #         line_img = img[y_up:y_lo, 0:942]

    #         #determine if line is footer first
    #         if(tester.Contains_Footer(y_up, y_lo, line_img)):
    #             footer_found = True
    #         #otherwise find line data and add to running string
    #         else:
    #             line_data += tester.Organize_LineData(tester.Search_Line(y_up, y_lo, line_img)) + " "

    #     print(line_data)


    # #print(tester.Organize_LineData(linedata))
    # end = time.time()
    # print("Time elapsed: {:.2f} sec".format(end-start))
    # # cv2.imshow("picture{}".format(i), img)
    # # cv2.waitKey(0)




    #########################################
    #Code used to map black pixels of letters
    test = 0
    if(test == 1):
        img = cv2.imread('processed_image.png')
        #img = cv2.resize(img, (400, 450))

        #white = [255,255,255]
        WHITE = [255,255,255]
        #black = [0,0,0]
        BLACK = [0,0,0]

        #IMPORTANT!
        #Change these values to get bitmap of letter
        y1, y2 = 164, 202
        x1, x2 = 623, 646
        num_rows, num_columns = y2 - y1, x2 - x1

        #img[(range y),(range x)]
        cropped_image = img[y1:y2, x1:x2]
        pixels = []
        tmp = ""
        for i in range(num_rows): # rows
            for j in range(num_columns): # columns
                
                if((cropped_image[i][j] == WHITE).all()):
                    tmp += "/"
                else:
                    tmp += "0"
                    pixels.append((i,j))
            print(tmp)
            tmp = ""
        #cv2.imshow('image',cropped_image)
        #cv2.waitKey(0)
        print(pixels)
        print((num_rows, num_columns))
    