from constants import RotationType, Axis
from auxiliary_methods import intersect, set_to_decimal
import copy

DEFAULT_NUMBER_OF_DECIMALS = 3
START_POSITION = [0, 0, 0]


class Item:
    def __init__(self, name, width, height, depth, weight):
        self.name = name
        self.width = width
        self.height = height
        self.depth = depth
        self.weight = weight
        self.rotation_type = 0
        self.position = START_POSITION
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS

    def format_numbers(self, number_of_decimals):
        self.width = set_to_decimal(self.width, number_of_decimals)
        self.height = set_to_decimal(self.height, number_of_decimals)
        self.depth = set_to_decimal(self.depth, number_of_decimals)
        self.weight = set_to_decimal(self.weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def string(self):
        return "%s (%s x %s x %s, weight: %s) pos(%s) rt(%s) vol(%s)" % (
            self.name, self.width, self.height, self.depth, self.weight,
            self.position, self.rotation_type, self.get_volume()
        )

    def get_volume(self):
        return set_to_decimal(
            self.width * self.height * self.depth, self.number_of_decimals
        )

    def get_dimension(self):
        if self.rotation_type == RotationType.RT_WHD:
            dimension = [self.width, self.height, self.depth]
        elif self.rotation_type == RotationType.RT_HWD:
            dimension = [self.height, self.width, self.depth]
        elif self.rotation_type == RotationType.RT_HDW:
            dimension = [self.height, self.depth, self.width]
        elif self.rotation_type == RotationType.RT_DHW:
            dimension = [self.depth, self.height, self.width]
        elif self.rotation_type == RotationType.RT_DWH:
            dimension = [self.depth, self.width, self.height]
        elif self.rotation_type == RotationType.RT_WDH:
            dimension = [self.width, self.depth, self.height]
        else:
            dimension = []

        return dimension


class Bin:
    def __init__(self, name, width, height, depth, max_weight):
        self.name = name
        self.width = width
        self.height = height
        self.depth = depth
        self.max_weight = max_weight
        self.items = []
        self.unfitted_items = []
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS

    def format_numbers(self, number_of_decimals):
        self.width = set_to_decimal(self.width, number_of_decimals)
        self.height = set_to_decimal(self.height, number_of_decimals)
        self.depth = set_to_decimal(self.depth, number_of_decimals)
        self.max_weight = set_to_decimal(self.max_weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def string(self):
        return "%s (%s x %s x %s , max_weight:%s) vol(%s)" % (
            self.name, self.width, self.height, self.depth, self.max_weight,
            self.get_volume()
        )

    def get_volume(self):
        return set_to_decimal(
            self.width * self.height * self.depth, self.number_of_decimals
        )

    def get_total_weight(self):
        total_weight = 0

        for item in self.items:
            total_weight += item.weight

        return set_to_decimal(total_weight, self.number_of_decimals)

    def put_item(self, item, pivot):
        fit = False
        valid_item_position = item.position
        item.position = pivot

        for i in range(0, len(RotationType.ALL)):
            item.rotation_type = i
            dimension = item.get_dimension()
            if (
                self.width < pivot[0] + dimension[0] or
                self.height < pivot[1] + dimension[1] or
                self.depth < pivot[2] + dimension[2]
            ):
                continue

            fit = True

            for current_item_in_bin in self.items:
                if intersect(current_item_in_bin, item):
                    fit = False
                    break

            if fit:
                if self.get_total_weight() + item.weight > self.max_weight:
                    fit = False
                    return fit

                self.items.append(item)

            if not fit:
                item.position = valid_item_position

            return fit

        if not fit:
            item.position = valid_item_position

        return fit


class Packer:
    def __init__(self):
        self.bins = []
        self.items = []
        self.unfit_items = []
        self.total_items = 0

    def add_bin(self, bin):
        return self.bins.append(bin)

    def add_item(self, item):
        self.total_items = len(self.items) + 1

        return self.items.append(item)

    def pack_to_bin(self, bin, item):
        fitted = False

        if not bin.items:
            response = bin.put_item(item, START_POSITION)

            if not response:
                bin.unfitted_items.append(item)

            return

        for axis in range(0, 3):
            items_in_bin = bin.items

            for ib in items_in_bin:
                pivot = [0, 0, 0]
                w, h, d = ib.get_dimension()
                if axis == Axis.WIDTH:
                    pivot = [
                        ib.position[0] + w,
                        ib.position[1],
                        ib.position[2]
                    ]
                elif axis == Axis.HEIGHT:
                    pivot = [
                        ib.position[0],
                        ib.position[1] + h,
                        ib.position[2]
                    ]
                elif axis == Axis.DEPTH:
                    pivot = [
                        ib.position[0],
                        ib.position[1],
                        ib.position[2] + d
                    ]

                if bin.put_item(item, pivot):
                    fitted = True
                    break
            if fitted:
                break

        if not fitted:
            bin.unfitted_items.append(item)

    def pack(
        self, bigger_first=False, distribute_items=False,
        number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS
    ):
        for bin in self.bins:
            bin.format_numbers(number_of_decimals)

        for item in self.items:
            item.format_numbers(number_of_decimals)

        self.bins.sort(
            key=lambda bin: bin.get_volume(), reverse=bigger_first
        )
        self.items.sort(
            key=lambda item: item.get_volume(), reverse=bigger_first
        )

        for bin in self.bins:
            for item in self.items:
                self.pack_to_bin(bin, item)

            if distribute_items:
                for item in bin.items:
                    self.items.remove(item)
    
    def pack_all_items(
        self, number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS
    ):
        # number formatting:
        for bin in self.bins:
            bin.format_numbers(number_of_decimals)

        # number formatting:
        for item in self.items:
            item.format_numbers(number_of_decimals)
        
        # List for saving all packed bins:    
        BinList = []
        
        #index for binlist
        pb = 0
        
        #list for saving volumes of all bins:
        VolumeBinList = []
        
        # List for saving all items to be processed:
        ItemList = []
        
        # Initial population of ItemList (All items)
        for item in self.items:
            ItemList.append(item)
            
        # Multiplier variable for testing if next bin is bigger than adding a new bin:
        M = 2
        
        # sorts bins in order from smallest to biggest:    
        self.bins = sorted(self.bins, key=lambda bin: bin.get_volume())
        
        # sorts items in order from biggest to smallest:
        self.items = sorted(self.items, key=lambda item: item.get_volume(), reverse=True)
        
        #Saving all bin volumes:
        for bin in self.bins:
            VolumeBinList.append(bin.get_volume())
        
        # checking for each bin type, starting with the smallest:
        for i in range(len(self.bins)):
            
            # infinite while loop for continuos testing of packing possibilities:
            # len(itemlist for bug testing:)
            while 1:
                
                #sort items in ItemList from smallest to biggest:
                ItemList = sorted(ItemList, key=lambda item: item.get_volume(), reverse=True) 
                
                for item in ItemList:
                    self.pack_to_bin(self.bins[i], item)
                    
                # Document the packed bin in BinList by creating a copy:
                BinList.insert(pb, copy.deepcopy(self.bins[i]))   
 
                # Reset list of items to be packed:
                ItemList.clear()
                # if no items where left unpacked:
                # print result and solution:
                if len(BinList[pb].unfitted_items) == 0 :
                    print("ALL ITEMS PACKED: \n")
                    
                    TotalWeight = 0
                    
                    ItemsTotalVolume = 0
                    
                    BinTotalVolume = 0     
                    print("AMOUNT OF BINS:", len(BinList))   
                    for b in range(len(BinList)):
                        BinTotalVolume += BinList[b].get_volume()
                        print(f"ITEMS PACKED IN BIN NUMBER {b+1}", BinList[b].string(),  ": \n")
                        for item in BinList[b].items:
                            ItemsTotalVolume += item.get_volume()
                            TotalWeight += item.weight
                            print("===>", item.string(),"\n")
                            
                        wastedSpace = BinTotalVolume - ItemsTotalVolume
                    
                    print("TOTAL WEIGHT:\n", TotalWeight ,"\n")
                        
                    print("TOTAL UNUSED VOLUME:\n", wastedSpace ,"\n")            
                           
                    exit()
                                
                # if some items where left unpacked:
                # then we are not done! :D            
                if len(BinList[pb].unfitted_items) > 0 :

                    # if there is no bigger bins to use:
                    if i+1 == len(self.bins):
                        
                        #if no remaining items could be packed in the biggest bin type:
                        #then we know that this items cannot fit into any bin type    
                        if len(BinList[pb].items) == 0:   
                            print("NOT ALL ITEMS COULD BE PACKED IN THE GIVEN BIN TYPES")
                            
                            for item in BinList[pb].unfitted_items:
                                    ItemList.append(item)
                                    print("IMPOSSIBLE ITEMS: \n====>", item.string(),"\n")     
                                    
                            exit()
                            
                        #reassign the missing items, in unfitted_items, to ItemList to be packed in a new bin:
                        for unfitted in BinList[pb].unfitted_items:
                            unfitted.rotation_type = 0
                            ItemList.append(unfitted)
                            
                        #self.bins.items has to be cleared before new items can fit in the given bin:
                        self.bins[i].items.clear()
                        #self.bins.unfitted_items must be cleared, else it will add dublicate items
                        self.bins[i].unfitted_items.clear()
                            
                        BinList[pb].unfitted_items.clear()
                        
                        pb += 1 
                            
                        continue
                        
                    # if using another bin of the same bin size result in less total bin volume than using the next bin:
                    # try packing remaining items in new bin (same bin type)
                    elif VolumeBinList[i] * M < VolumeBinList[i+1]:   
                            
                        for unfitted in BinList[pb].unfitted_items:
                            unfitted.rotation_type = 0
                            ItemList.append(unfitted)
                        
                        #unfitted items have been      
                        BinList[pb].unfitted_items.clear()
                        
                        #self.bins.items has to be cleared before new items can fit in the given bin:
                        self.bins[i].items.clear()
                        #self.bins.unfitted_items must be cleared, else it will add dublicate items
                        self.bins[i].unfitted_items.clear()
                                
                        pb += 1
                        
                        M += 1
                        
                        continue
                        
                    # if using another bin of the same bin size result in more total bin volume than using the next bin:
                    # try packing all items in new bin (bigger bin type)
                    elif VolumeBinList[i] * M >= VolumeBinList[i+1]:
                            
                        for item in self.items:
                            if item not in ItemList:
                                item.rotation_type = 0
                                ItemList.append(item)
                                
                        BinList.clear()
                        
                        M = 2
                            
                        pb = 0
                        
                        #self.bins.items has to be cleared before new items can fit in the given bin:
                        self.bins[i].items.clear()
                        #self.bins.unfitted_items must be cleared, else it will add dublicate items
                        self.bins[i].unfitted_items.clear()
                            
                        break
                        
                else:
                    print("ERROR")
                    exit()