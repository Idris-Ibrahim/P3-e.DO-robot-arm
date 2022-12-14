#Function definiton:
def DefineBoxes(BoxList):

    class Box:
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z
            self.volume = self.x * self.y * self.z

    #Amount of box types:
    BoxTypeAmount = int(input("Amount of box types: "))

    #Insert measurement for each axes for each box:
    for i in range(BoxTypeAmount) :
        x = float(input(f"Box {i} x length: "))
        y = float(input(f"Box {i} y length: "))
        z = float(input(f"Box {i} z length: "))

        BoxList.append(Box(x, y, z))

        print("\n")
    
    #Sorting all boxes from smallest to biggest volume
    BoxList = sorted(BoxList, key=lambda Box: Box.volume)

    #print all the boxes and the measurement:
    for i in range (0,len(BoxList)):

        print(f"Box {i} measurements:", BoxList[i].x, BoxList[i].y, BoxList[i].z)
        print(f"Box {i} volume: {BoxList[i].volume}\n")