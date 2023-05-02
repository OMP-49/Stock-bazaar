class Node:
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.next = None
        self.prev = None

class LRUCache:
    def __init__(self, size):
        self.size = size
        self.curr_size = 0
        self.cache = {}
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
        

    def get(self, key):
        if key not in self.cache:
            return None
        curr = self.cache[key]
        curr.next.prev = curr.prev
        curr.prev.next = curr.next

        curr.next = self.head.next
        curr.next.prev = curr
        self.head.next = curr
        curr.prev = self.head
        self.cache[key] = curr
        return curr.val
        

    def put(self, key, value):
        if key in self.cache:
            self.remove(key)
        
        if self.curr_size == self.size:
            self.removeLeastRecent()

        curr = Node(key, value)
        curr.next = self.head.next
        curr.next.prev = curr
        self.head.next = curr
        curr.prev = self.head
        self.cache[key] = curr
        self.curr_size += 1

    def removeLeastRecent(self):
        if self.curr_size == 0:
            return
        curr = self.tail.prev
        self.tail.prev = curr.prev
        curr.prev.next = self.tail
        del self.cache[curr.key]
        self.curr_size -= 1
    
    def remove(self, key):
        if key not in self.cache:
            return
        curr = self.cache[key]
        curr.prev.next = curr.next
        curr.next.prev = curr.prev
        del self.cache[key]
        self.curr_size -= 1
        
