##########################
# Kevin Patton
# Art 2300 - 2D study
# Aaron Peters
# Hilbert Cruve Generator
##########################

import sys, getopt, math
import numpy as np  #REQUIRED pip install numpy
from PIL import Image #REQUIRED pip install pillow

#Globals
padtop = 0
padside = 0
width = 1

xwidth = 200
yheight = 200
class hilbert_pt:
    def __init__(self, i, x, y):
        self.i = i
        self.x = x
        self.y = y
    def copy(self):
        return hilbert_pt(self.i, self.x, self.y)
    def scale(self, factor):
        self.x = self.x * factor
        self.y = self.y * factor
    def translate(self, offsetx, offsety):
        self.x += offsetx
        self.y += offsety
    def rotateccw(self, turns):
        x = self.x * math.cos((math.pi/2) * turns) - self.y * math.sin((math.pi/2) * turns)
        y = self.x * math.sin((math.pi/2 * turns)) + self.y * math.cos((math.pi/2) * turns)
        self.x = x
        self.y = y
    def show(self):
        print("i=", self.i, "(x,y)= (", self.x, ',', self.y, ")")

#scales all points by factor f and returns list for function chaining
def scaleall(ls, f):
    for x in ls:
        x.scale(f)
    return ls

#translates all point a distance (offx, offy) returns list for function chaining
def transall(ls, offx, offy):
    for x in ls:
        x.translate(offx, offy)
    return ls

#rotate all points about the origin N counter clockwise turns returns list for funciton chaining
def rotall(ls, t):
    for x in ls:
        x.rotateccw(t)
    return ls

#incramenst the amount of each point by i returns list for function chaining
def incall(ls, i):
    for x in ls:
        x.i += i
    return ls

#renumbers points for correct draw order returns list for function chaining
def renum(ls):
    n = len(ls)
    for k in range(n):
        ls[k].i = n - k
    return ls

def deepcopy(ls):
    x = []
    for y in ls:
        x.append(y.copy())
    return x

def showall(ls):
    for x in ls:
        x.show()

# converts points in the cartesian plane to array indices
def xy2ij(pt, yheight, xwidth):
    xp = pt.x * (xwidth-padside)/2 + (xwidth)/2
    yp = abs(pt.y * (yheight-padtop)/2 - (yheight)/2)
    return (int(xp),int(yp))

#creates the image buffer
def makeimgbuff(ls, xwidth, yheight):
    arr = np.zeros((yheight, xwidth)) 
    for i in range(len(ls)-1):
        (k,n) = xy2ij(ls[i], yheight, xwidth)
        (m,l) = xy2ij(ls[i+1], yheight, xwidth)
        for g in range(width):
            for h in range(width):
                arr[n - int(width/2) + h, k - int(width/2) + g] = 255
        if (n-l) != 0 and (k-m) == 0:
            if n > l:
                for j in range(n-l):
                    for g in range(width):
                        arr[l + j, k - int(width/2) + g]= 255
            else:
                for j in range(l-n):
                    for g in range(width):
                        arr[n + j, k - int(width/2) + g]= 255
        elif (k-m) != 0 and n-l == 0:
            if k > m:
                for j in range(k - m):
                    for g in range(width):
                        arr[n - int(width/2) + g, m + j]= 255
                    arr[n, m + j]=255
            else:
                for j in range(m - k):
                    for g in range(width):
                        arr[n - int(width/2) + g, k + j]= 255
        else:
            print("Image too small to be accurate")
    return arr

# calculates the corners for n iterations of the hilbert curve
# keeps them numbered so we know which have to be connected to eachother
def hilbert(num): 
    pts = [hilbert_pt(1, 0, 0)]
    for i in range(0, num):
        scaleall(pts, 1/2)
        #3 CCW rotation = 1 CW rotation, moved to bottom left
        bl = renum(transall(rotall(deepcopy(pts), 3), -1/2, -1/2))
        bl.sort(key=lambda x: x.i)
        #moved to top left
        ul = incall(transall(deepcopy(pts), -1/2, 1/2), len(pts))
        #moved to top right
        ur = incall(transall(deepcopy(pts), 1/2, 1/2), 2*len(pts))
        #1 CCW rotation then moved to the bottom right
        br = incall(renum(transall(rotall(deepcopy(pts), 1),1/2, -1/2)), 3*len(pts))
        br.sort(key=lambda x: x.i)
        
        #combines all arrays back int pts
        pts = []
        pts.extend(bl)
        pts.extend(ul)
        pts.extend(ur)
        pts.extend(br)
    return pts

def main(argv):
    num = 2 # number of iterations
    size = 500 # size x size canvas
    fname='kevinpatton.jpg'
    try:
        opts, args = getopt.getopt(argv, "hn:x:y:o:t:s:w:", ["num=", "xwidth=","yheight=",\
        "ofile=","padding-top=", "padding-side=", "width="])
    except:
        print("hilbert.py -n [num_iterations] -p [size_in_pixel]")
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print("python hilbert.py\n \
            \t-n [num_iterations]\n\
            \t-x [width_in_pixles]\n\
            \t-y [height_in_pixles]\n\
            \t-o [out_file]\n\
            \t-t [padding_top]\n\
            \t-s [padding_side]\n\
            \t-w [stroke_width]\n")
            sys.exit()
        elif opt in ("-n", "--num"):
            num = int(arg)
        elif opt in ("-x", "--xsize"):
            global xwidth
            xwidth = int(arg)
        elif opt in ("-y", "--ysize"):
            global yheight
            yheight = int(arg)
        elif opt in ('-o', '--ofile'):
            fname = arg
        elif opt in ("-t", "--padding-top"):
            global padtop
            padtop = int(arg)
        elif opt in ("-s", "--padding-side"):
            global padside
            padside = int(arg)
        elif opt in ("-w", "--width"):
            global width
            width = int(arg)
    
    #computes points on hilbert curve
    pts = hilbert(num)
    a = makeimgbuff(pts, xwidth, yheight)
    
    #saves file to disk
    im = Image.fromarray(a)
    im = im.convert("L")
    im.save(fname)


if __name__=="__main__":
    main(sys.argv[1:])
