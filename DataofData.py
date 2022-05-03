# To the next Capstone group that may utilize this code, I wish
# my condolences to your sanity as I am too far gone having
# being the creator of this monstrosity. I plead with you,
# do not fall for its power for you will loose yourself.
# If you do find yourself looking at this code, destroy it.
# Leave no trace of it. It will only bring sorrow and death
# to those computer scientists foolish enough to attempt to 
# optimize it. Please have greater strength to do away with
# this code than I did. - OH '22.

from tkinter.tix import MAX
from Alphabet_Soup import *
from Custom_OCR import *
import networkx as nx
import time

#Custom_OCR methods
tester = Custom_OCR()

def Next_BFS(graph):
    #first = nodes[0]
    first = list(graph.edges)[0][0]
    fist_node = list(graph.edges)[0]
    # print("first ", first)
    # print("fist node ", fist_node)
    # print("first 10", list(graph.edges)[0:10])
    # print()
    edge_bfs = list(nx.edge_bfs(graph, source=first))
    F = nx.Graph()
    for i in edge_bfs:
        F.add_edge(i[0],i[1])
    #https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.traversal.breadth_first_search.bfs_successors.html#networkx.algorithms.traversal.breadth_first_search.bfs_successors
    # nodes =  [first] + [successor for successors in dict(nx.bfs_successors(graph, first)).values() for successor in successors]
    # return nodes
    return F


#function
#Remove the last set of 
def Remove_BFS(graph):
    #remove edges
    thing = list(graph.edges)[0][0]
    edge_bfs = list(nx.edge_bfs(graph, source=thing))
    # print(edge_bfs)
    # print()
    
    #remove_edges = [e for e in graph.edges if e in edge_bfs]
    for i in edge_bfs:
        graph.remove_edge(i[0],i[1])
    #graph.remove_edges_from()

    

    #remove nodes
    #https://stackoverflow.com/questions/29082681/using-networkx-bfs-tree-to-obtain-a-list-of-nodes-of-a-directed-graph-in-bfs-ord
    #[0] + [successor for successors in dict(nx.bfs_successors(graph, nodes[0])).values() for successor in successors]


#function
def Find_Bounds(letter_nodes):
    #find the min and max x and y values
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = -float('inf'), -float('inf')
    for i in letter_nodes:
        #mins
        if(i[0] < min_y):
            min_y = i[0]
        if(i[1] < min_x):
            min_x = i[1]
        #max
        if(i[0] > max_y):
            max_y = i[0]
        if(i[1] > max_x):
            max_x = i[1]
    
    return min_x, min_y, max_x, max_y


#function
def Normalize_Nodes(letter_nodes, min_y, min_x):
    #subtract the min values from the nodes
    for i in range(len(letter_nodes)):
        if(min_y > 0):
            letter_nodes[i] = (letter_nodes[i][0] - min_y, letter_nodes[i][1] - min_x)
        else:
            letter_nodes[i] = (letter_nodes[i][0], letter_nodes[i][1] - min_x)
    return letter_nodes


#function
#new searching function to compare coordinates of node list
def Compare(letter_nodes,y,x,diff):
    #print dimentions
    # print((y,x))
    #percent accurate thingy
    confidence = .07

    #iterate through all letters
    for letter in master_key:
        if(letter == "l" or letter == "I"):
            confidence = 0
        else:
            confidence = .07
        #get appropriate dictionary
        dictionary, dictionary_dims = tester.Find_Dictionary(letter)
        dictionary_dims[letter]
        #iterate through all bitmaps
        #if((y-10 <= dictionary_dims[letter][0] and y + 10 >= dictionary_dims[letter][0]) and (x-10 <= dictionary_dims[letter][1]) and x + 10 >= dictionary_dims[letter][1]):
        for bitmaps in dictionary[letter]:

            # tmp = 0
            # for j in bitmaps:
            #     if(j in letter_nodes):
            #         tmp += 1
            
            #compare the bitmap and the letter nodes with an XOR comparison
            #returns the nodes not overlaping
            tmp = set(bitmaps).symmetric_difference(set(letter_nodes))
            
            if(len(tmp) / len(letter_nodes) <= confidence):
                #print("Confidence: {} ".format(letter), tmp / len(letter_nodes))
                # confidence = tmp / len(letter_nodes)
                if(letter == "," and diff > 20):


                    return letter

                elif(letter != ","):
                    # if(letter == "l"):
                    #     print("confidence: {}".format(len(tmp) / len(letter_nodes)))
                    return letter
    #use "" for actual runs
    return "@"

def FindCenter(nodes):
    x, y = 0, 0
    length = len(nodes)
    for i in nodes:
        y += i[0]
        x += i[1]
    return (y // length, x // length)

#create a graph of edges
def GraphEdges(graph, img, y_lo):
    #find the next line of text
    y_up, y_lo = tester.Find_Line(y_lo, img)

    #frame the image of pixels
    line_img = img[y_up:y_lo, 0:942]

    #get the height of the image
    y_max = y_lo - y_up

    for y in range(y_max):
        for x in range(942):
            #check pixel is black
            if(line_img[y,x] == 0):
                #check value below pixel
                if(y < y_max and line_img[y+1,x] == 0):
                    graph.add_edge((y,x),(y+1,x))

                #check value right of pixel
                if(x < 942 and line_img[y,x+1] == 0):
                    graph.add_edge((y,x),(y,x+1))
    
    return y_lo

#loop through graph object to find all graphs of pixels
def GraphLetters(line_data):
    while(len(G.edges) > 0):
        #gets the graph of the next letter
        letter_graph = Next_BFS(G)
        #letter_nodes = list(letter_graph.nodes)

        #find center for debugging
        center = FindCenter(list(letter_graph.nodes))

        #add graph and center to list
        line_data.append((letter_graph, center[1], 0,0,0,0))

        #remove the selected edges from the original graph
        Remove_BFS(G)

#loop through each value and find any letters with disconnected sections
def Combine_Disconnected_Graphs(line_data, other_line_data):
    skip = False
    for i in range(len(line_data)):
        if(not skip):
            #min_x, min_y, max_x, max_y = Find_Bounds(list(line_data[i][0].nodes)) #change this to min_x_1
            G_new = line_data[i][0]

            #if the center x value of the graph is less than or equal to 4 then add 
            if(i+1 < len(line_data) and abs(line_data[i][1] - line_data[i+1][1]) <= 4):
                G_new = nx.compose(line_data[i][0], line_data[i+1][0])
                
                #line_data.remove(line_data[i+1])
                skip = True


            #Find the min and max values of the letter's bounds
            min_x, min_y, max_x, max_y = Find_Bounds(list(G_new.nodes))

            #update the line data at i
            #line_data[i] = (G_new, line_data[i][1], min_x, min_y, max_x, max_y)
            other_line_data.append((G_new, line_data[i][1], min_x, min_y, max_x, max_y))
        else:
            skip = False

#find output for line
def Find_Line_Outputs(other_line_data):
    tmp = 0
    line = ""
    for j in range(len(other_line_data)):
        #   0    1    2      3      4      5
        #(Graph, x, min_x, min_y, max_x, max_y)
        tmp+= 1
        #normalize node coordinates to mimic in box
        normalized_nodes = Normalize_Nodes(list(other_line_data[j][0].nodes), other_line_data[j][3], other_line_data[j][2])

        #show the image for debuging
        # picture = line_img[other_line_data[j][3]:other_line_data[j][5], other_line_data[j][2]:other_line_data[j][4]]
        # cv2.imshow("picture{}".format(str(tmp)), picture)
        # print(normalized_nodes)
        # print()
        # cv2.waitKey(0)

        #Get the letter output from a confidence threashold
        line += Compare(normalized_nodes,other_line_data[j][5]-other_line_data[j][3],other_line_data[j][4]-other_line_data[j][2], other_line_data[j][5])
        
        #find spaces in the lines
        # print("{} {}".format(output, ))
        if(j+1 != len(other_line_data) and other_line_data[j+1][2] - other_line_data[j][4] > 10):
            line += " "
    return line + " "

#used with the memory variable
def Check_Repititions(memory, post):
        #check memory list
        #print(self.memory)
        if(post in memory):
            # print("Returned")
            # print(post)
            return True
        
        #add post to memory
        #print(post)
        #self.memory.insert(0, post)
        #pop latest value if 
        if(len(memory) > 4):
            memory.pop(len(memory) - 1)
        return False

#Loop through all individual postdata and write data to csv file
#TODO: Change Name
def Write_To_CSV(postdata, memory):
    #temporary memory to store for 
    tmp_mem = []
    #keeps track of how many posts were added to the csv
    num_posts = 0
    #open csv file to continue adding to filename
    # print("start")
    # print(self.memory)

    for post in postdata:
        # Fix lines
        line = post.replace(',', '')

        # If repeated value then stop adding
        if(Check_Repititions(memory, line)):
            for i in tmp_mem:
                memory.insert(0, i)
            # print("after same memory")
            # print(self.memory)
            # print("after same temp")
            # print(tmp_mem)
            return num_posts
        
        #save post to temporary memory
        tmp_mem.insert(0, line)

        #write to csv file
        print(line)
        num_posts += 1
    for i in tmp_mem:
        memory.insert(0, i)
    return num_posts
    # print("all new")
    # print(self.memory)

#used to prevent repeated values
memory = []

#main loop
while(True):
    #first line to look up
    #use (0, 100) for testing
    y_up, y_lo = 0, 100 #100

    #timer start
    start = time.time()
    MAX_HEIGHT = 1287
    output = ""
    line_of_letters = ""

    #Outside loop to take next screenshot
    #Screen shot and saved image
    tester.ScreenShot()

    img = tester.Process_Image()

    #accumulates all posts
    all_lines = []

    #loop to read all lines
    while(y_lo < MAX_HEIGHT and img[86,539] == 255):
        #create all needed variables
        #create new graph
        G = nx.Graph()

        #list of letter graphs and center x value
        #(Graph, x, min_x, min_y, max_x, max_y)
        line_data = []
        min_x, min_y, max_x, max_y = 0,0,0,0

        #use after finding disjoint letters
        other_line_data = []
        

        #exit if circulated back to 1
        # if(y_lo == 1):
        #     print("FIRST")
        #     break

        # if("~~~" in line_of_letters):
        #     output = ""
        #     y_lo = GraphEdges(G, img, y_lo)


        #create graph of edges
        y_lo = GraphEdges(G, img, y_lo)

        #exit if circulated back to 1
        if(y_lo == 1):
            break

        #loop through graph object to find all graphs of pixels
        GraphLetters(line_data)

        #sort the line_data list on the x center
        line_data = tester.MergeSort(line_data)

        #loop through each value and find any letters with disconnected sections
        Combine_Disconnected_Graphs(line_data, other_line_data)

        #find output for all lines
        line_of_letters = Find_Line_Outputs(other_line_data)

        #print line or save line
        if("~~~" in line_of_letters):
            #print(output[0:-1].replace('\'\'', '\"'))
            all_lines.append(output[0:-1].replace('\'\'', '\"'))
            #print()
            output = ""
            y_lo = GraphEdges(G, img, y_lo)
        else:
            output += line_of_letters
        

        
    end = time.time()
    #print("Time: {}\n".format(str(end-start)))
    #print(all_lines)
    Write_To_CSV(all_lines, memory)



#Before Orrin had a "Good" idea to change the stupid code
#he had working code below now pray that the stuff above works
"""
i = 0
while(len(G.edges) > 0):
    #REMOVE: Only for displaying images
    i+=1


    #gets the graph of the next letter
    letter_nodes = Next_BFS(G)
    min_x, min_y, max_x, max_y = Find_Bounds(letter_nodes)
    
    #show the image for debuging
    picture = line_img[min_y:max_y, min_x:max_x]
    cv2.imshow("picture{}".format(str(i)), picture)
    cv2.waitKey(0)

    #find center for debugging
    center = FindCenter(letter_nodes)

    #normalize node coordinates to mimic in box
    normalized_nodes = Normalize_Nodes(letter_nodes, min_y, min_x)
    
    print("DIMS: ", (max_y-min_y,max_x-min_x))
    print("Center: ", center)
    #Get the letter output from a confidence threashold
    output = Compare(normalized_nodes,max_y-min_y,max_x-min_x)
    #testing
    if(output == "No Letter Found"):
        print("Normal", normalized_nodes)
    print(output)

    Remove_BFS(G)"""