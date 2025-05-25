from itertools import chain, combinations
from collections import defaultdict, OrderedDict
from tqdm import tqdm

global viz_tree_dict
class Node:
    def __init__(self, itemName, frequency, parentNode):
        self.itemName = itemName    # tên item
        self.count = frequency      # tần suất xuất hiện
        self.parent = parentNode    # Nút cha
        self.children = {}          # Danh sách các nút con
        self.next = None            # Liên kết đến nút cùng item khác

    # phương thức tăng tần suất
    def increment(self, frequency):
        self.count += frequency

    # phươngphương thức hiển thị cây theo dạng text
    def display(self, ind=1):
        print('-' * ind, self.itemName, ' ', self.count)
        for child in list(self.children.values()):
            print('-' * ind, 'parent:', self.itemName)
            child.display(ind+1)

# Hàm xây dựng cậy
def constructTree(itemSetList, frequency, minSup):
    print("Building FP-Tree...")
    headerTable = defaultdict(int)

    print("Counting item frequencies...")
    # Đếm tuần suất xuất hiện và tạo bảng header
    for idx, itemSet in enumerate(tqdm(itemSetList, desc="Counting frequencies")):
        for item in itemSet:
            headerTable[item] += frequency[idx]

    print(f"Initial item frequencies: {dict(headerTable)}")

    # Bỏ những item nhỏ hơn minSup
    original_items = len(headerTable)
    headerTable = dict((item, sup) for item, sup in headerTable.items() if sup >= minSup)
    print(f"After filtering (minSup={minSup}): {len(headerTable)}/{original_items} items remain")
    print(f"Frequent items: {dict(headerTable)}")

    if(len(headerTable) == 0):
        print("❌ No frequent items found!")
        return None, None

    # Chuyển giá trị trong HeaderTable dạng [Item: [frequency]]
    # Thành HeaderTable dạng [Item: [frequency, headNode]]
    for item in headerTable:
        headerTable[item] = [headerTable[item], None]

    # Khởi tạo node đầu tiên là Null
    fpTree = Node('Null', 1, None)
    print("Root node created")

    print("Inserting transactions into FP-Tree...")
    # Cập nhật cây FP cho các mục
    for idx, itemSet in enumerate(tqdm(itemSetList, desc="Building tree")):
        # Lấy các item nhỏ hơn minSSup
        itemSet = [item for item in itemSet if item in headerTable]
        # Sắp xếp các item này theo thứ tự giảm dần của tần suất xuất hiện
        # itemSet.sort(key=lambda item: headerTable[item][0], reverse=True)
        itemSet.sort(key=lambda item: (-headerTable[item][0], item))

        if itemSet:  # Only process non-empty itemsets
            # Duyệt từ gốc đến lá, cập nhật cây với các item vừa lấy được
            currentNode = fpTree
            for item in itemSet:
                currentNode = updateTree(item, currentNode, headerTable, frequency[idx])

    print("✅ FP-Tree construction completed")
    return fpTree, headerTable

def updateHeaderTable(item, targetNode, headerTable):
    # Nếu đây là nút đầu tiên của item đang xét thì gán làm nút đầu tiên luôn
    if(headerTable[item][1] == None):
        headerTable[item][1] = targetNode
    else:
        # Ngược lại ta lấy nút đầu tiên trong danh sách các nút của item đang xét
        currentNode = headerTable[item][1]
        # Duyệt tới nút cuối cùng và thêm nó vào cuối danh sách
        while currentNode.next != None:
            currentNode = currentNode.next
        currentNode.next = targetNode

def updateTree(item, treeNode, headerTable, frequency):
    if item in treeNode.children:
        # Nếu node item đó đã có thì chỉ việc tăng tần suất xuất hiện của node đó lên
        treeNode.children[item].increment(frequency)
    else:
        # Ngược lại thì tạo ra một nhánh con mới
        newItemNode = Node(item, frequency, treeNode)
        # Thêm nút mới tạo vào danh sách nút con của nút cha gần nhất
        treeNode.children[item] = newItemNode
        # Liên kết nút mới vào bảng HeaderTable
        updateHeaderTable(item, newItemNode, headerTable)

    return treeNode.children[item]

# thu thập các item trên đường đi từ node lên đến gốc và lưu vào prefixPath
def ascendFPtree(node, prefixPath):
    if node.parent != None:
        prefixPath.append(node.itemName)
        ascendFPtree(node.parent, prefixPath)

# Tìm tất cả các đường đi tới nút basePat
def findPrefixPath(basePat, headerTable):
    # Lấy node đầu tiên của item basePat từ bảng headerTable
    treeNode = headerTable[basePat][1]
    # Chứa các đường dẫn tiền tố
    condPats = []
    # chứa tần suất xuất hiện của các item trong danh sách tiền tố
    frequency = []
    while treeNode != None:
        prefixPath = []
        # Lấy tất cả các item từ node treeNode đến nút gốc và lưu vào prefixPath
        ascendFPtree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            # Storing the prefix path and it's corresponding count
            condPats.append(prefixPath[1:])
            frequency.append(treeNode.count)

        # Tới nút tiếp theo
        treeNode = treeNode.next
    return condPats, frequency

# Hàm khai thác hàm phổ biến
def mineTree(headerTable, minSup, preFix, freqItemList):
    stack = [(headerTable, minSup, preFix)]

    while stack:
        headerTable, minSup, preFix = stack.pop()

        # Sắp xếp các mục trong headerTable theo tần suất giảm dần
        sortedItemList = [item[0] for item in sorted(list(headerTable.items()), key=lambda p: p[1][0], reverse=True)]


        for item in sortedItemList:
            newFreqSet = preFix.copy()
            newFreqSet.add(item)
            freqItemList.append(newFreqSet)

            conditionalPattBase, frequency = findPrefixPath(item, headerTable)
            conditionalTree, newHeaderTable = constructTree(conditionalPattBase, frequency, minSup)

            if newHeaderTable:
                stack.append((newHeaderTable, minSup, newFreqSet))

# Hàm sinh ra tất cả các tập con không rỗng của tập hợp s (trừ rỗng và chính nó)
def powerset(s):
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)))

# Hàm đếm tần suất xuất hiện của một itemSet (testSet)
def getSupport(testSet, itemSetList):
    count = 0
    for itemSet in itemSetList:
        if(set(testSet).issubset(itemSet)):
            count += 1
    return count

# Xây dựng rule từ các tập mục thường xuyên
def associationRule(freqItemSet, itemSetList, minConf):
    rules = []
    for itemSet in tqdm(freqItemSet):
        # Lấy tất cả các tập con không rỗng của tập itemSet
        subsets = powerset(itemSet)
        # Tính độ support của itemset đó
        itemSetSup = getSupport(itemSet, itemSetList)
        # Kiểm tra nếu chính itemSet đó nhỏ hơn minConf thì bỏ qua luôn
        if itemSetSup <= minConf: continue
        for s in subsets:
            # dựa trên công thức tính confidence
            confidence = float(itemSetSup / getSupport(s, itemSetList))
            if(confidence > minConf):
                rules.append([set(s), set(itemSet.difference(s)), confidence])
    return rules

# Hàm gán cho mỗi itemSet xuất hiện 1 lần
# Không xử lý gộp các itemSet trùng nhau
def getFrequencyFromList(itemSetList):
    frequency = [1 for i in range(len(itemSetList))]
    return frequency


# itemSetList: danh sách các transaction (mỗi phần tử là 1 tập các item)
# minSupRatio: ngưỡng hỗ trợ tối thiểu tính theo tỷ lệ %
# ngưỡng tin cậy tối thiểu cho rule
def fpgrowth(itemSetList, minSupRatio, minConf):
    """
    FP-Growth algorithm with detailed step-by-step output
    """
    print(f"{'#'*60}")
    print(f"FP-GROWTH ALGORITHM - DETAILED EXECUTION")
    print(f"{'#'*60}")
    print(f"Support threshold: {minSupRatio}")
    print(f"Confidence threshold: {minConf}")
    print(f"Total transactions: {len(itemSetList)}")

    global viz_tree_dict
    viz_tree_dict = dict()

    print(f"\n{'='*60}")
    print(f"STEP 1: DATA PREPROCESSING")
    print(f"{'='*60}")
    print(f"📊 Total transactions: {len(itemSetList)}")

    # Show first 5 transactions as examples
    print("📋 Sample transactions:")
    for i, transaction in enumerate(itemSetList[:5], 1):
        items_display = ', '.join(transaction[:5])  # Show first 5 items
        if len(transaction) > 5:
            items_display += f" ... (+{len(transaction)-5} more items)"
        print(f"  • Transaction {i}: [{items_display}]")

    if len(itemSetList) > 5:
        print(f"  ... and {len(itemSetList)-5} more transactions")

    # Đếm số lần tần suất xuất hiện của từng itemSet
    frequency = getFrequencyFromList(itemSetList)
    minSup = len(itemSetList) * minSupRatio

    print(f"\n⚙️ Minimum support count: {minSup:.1f} (threshold: {minSupRatio*100}%)")

    print(f"\n{'='*60}")
    print(f"STEP 2: BUILDING FP-TREE")
    print(f"{'='*60}")
    print("🌳 Constructing FP-Tree from transactions...")

    fpTree, headerTable = constructTree(itemSetList, frequency, minSup)

    if(fpTree == None):
        print('❌ No frequent item set found')
        return None, None
    else:
        print("✅ FP-Tree construction completed")

        print(f"\n{'='*60}")
        print(f"STEP 3: HEADER TABLE ANALYSIS")
        print(f"{'='*60}")
        print(f"📊 Frequent items found: {len(headerTable)}")

        # Show top 10 most frequent items
        sorted_items = sorted(headerTable.items(), key=lambda x: x[1][0], reverse=True)
        print("🔝 Top frequent items:")
        for i, (item, (freq, _)) in enumerate(sorted_items[:10], 1):
            support_pct = (freq / len(itemSetList)) * 100
            print(f"  {i}. {item}: {freq} times ({support_pct:.1f}%)")

        if len(headerTable) > 10:
            print(f"  ... and {len(headerTable)-10} more items")

        print(f"\n{'='*60}")
        print(f"STEP 4: MINING FREQUENT PATTERNS")
        print(f"{'='*60}")
        print("⛏️ Mining frequent itemsets from FP-Tree...")

        freqItems = []
        mineTree(headerTable, minSup, set(), freqItems)

        print(f"✅ Found {len(freqItems)} frequent itemsets")
        print(f"📈 Total frequent itemsets discovered: {len(freqItems)}")

        print(f"\n{'='*60}")
        print(f"STEP 5: FP-TREE STRUCTURE")
        print(f"{'='*60}")
        print("🌳 FP-Tree built successfully with frequent items")
        print(f"🌳 Tree contains {len(freqItems)} frequent items")

        # Show itemset size distribution
        size_dist = {}
        for itemset in freqItems:
            size = len(itemset)
            size_dist[size] = size_dist.get(size, 0) + 1

        print("📊 Itemset size distribution:")
        for size in sorted(size_dist.keys()):
            print(f"  • {size}-itemsets: {size_dist[size]} found")

        print(f"\n{'='*60}")
        print(f"STEP 6: GENERATING ASSOCIATION RULES")
        print(f"{'='*60}")
        print(f"🔗 Generating rules with confidence ≥ {minConf*100}%...")

        rules = associationRule(freqItems, itemSetList, minConf)

        print(f"✅ Generated {len(rules)} association rules")

        if rules:
            # Show confidence distribution
            conf_ranges = {"90-100%": 0, "80-90%": 0, "70-80%": 0, "60-70%": 0, "<60%": 0}
            for rule in rules:
                conf = rule[2] * 100
                if conf >= 90:
                    conf_ranges["90-100%"] += 1
                elif conf >= 80:
                    conf_ranges["80-90%"] += 1
                elif conf >= 70:
                    conf_ranges["70-80%"] += 1
                elif conf >= 60:
                    conf_ranges["60-70%"] += 1
                else:
                    conf_ranges["<60%"] += 1

            print("📊 Confidence distribution:")
            for range_name, count in conf_ranges.items():
                if count > 0:
                    print(f"  • {range_name}: {count} rules")

        print(f"\n{'='*60}")
        print(f"✅ ALGORITHM COMPLETED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"📈 Summary: {len(freqItems)} itemsets, {len(rules)} rules generated")

        return freqItems, rules

def print_header_links(headerTable):
    print("\n===== Header Table Links =====")
    print("{:<10} {:<10} {}".format("Item", "Frequency", "Linked Nodes"))
    print("-" * 40)
    for item, (frequency, node) in headerTable.items():
        current = node
        chain = []
        while current is not None:
            chain.append(f"{current.itemName}({current.count})")
            current = current.next  # hoặc current.link nếu bạn dùng 'link'
        linked_nodes = " -> ".join(chain) if chain else "None"
        print("{:<10} {:<10} {}".format(item, frequency, linked_nodes))

def print_fp_tree(node, indent=0):
    # Bỏ qua nút gốc vì không lưu item
    if node.itemName is not None:
        print('-' * indent + f"{node.itemName} ({node.count})")
    for child in node.children.values():
        print_fp_tree(child, indent + 1)

def printResults(freqItems, rules):
    print("=== Frequent Itemsets ===")
    for itemset in freqItems:
        print(f"Itemset: {set(itemset)}")

    print("\n=== Association Rules ===")
    for rule in rules:
        antecedent, consequent, confidence = rule
        print(f"Rule: {antecedent} => {consequent} (Confidence: {confidence:.4f})")

if __name__ == "__main__":
    transactions = [
        ['f', 'a', 'c', 'd', 'g', 'i', 'm', 'p'],  # TID 100
        ['a', 'b', 'c', 'f', 'l', 'm', 'o'],       # TID 200
        ['b', 'f', 'h', 'j', 'o'],                # TID 300
        ['b', 'c', 'k', 's', 'p'],                # TID 400
        ['a', 'f', 'c', 'e', 'l', 'p', 'm', 'n']   # TID 500
    ]
    minSup = 0.5
    min_support = 0.5 * len(transactions)
    minConf = 0.88

    frequency = getFrequencyFromList(transactions)
    fpTree, headerTable = constructTree(transactions, frequency, min_support)

    print("\nFrequency")
    print(frequency)

    print("\nHeader Table")
    print_header_links(headerTable)
    #print(headerTable)

    print_fp_tree(fpTree)


    freqItems, rules = fpgrowth(transactions, minSup, minConf)
    # # fpTree.display()

    printResults(freqItems, rules)