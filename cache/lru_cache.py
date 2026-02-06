from threading import Lock

class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class DoublyLinkedList:
    def __init__(self):
        self.head = Node(None, None)
        self.tail = Node(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def add_to_end(self, node):
        last = self.tail.prev
        last.next = node
        node.prev = last
        node.next = self.tail
        self.tail.prev = node

    def remove(self, node):
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node


class LRUCache:
    def __init__(self, capacity: int = 500):
        self.capacity = capacity
        self.map = {}
        self.dll = DoublyLinkedList()
        self.lock = Lock()

    def get(self, key):
        with self.lock:
            node = self.map.get(key)
            if not node:
                return None
            self.dll.remove(node)
            self.dll.add_to_end(node)
            return node.value

    def put(self, key, value):
        with self.lock:
            if key in self.map:
                node = self.map[key]
                self.dll.remove(node)
            else:
                if len(self.map) >= self.capacity:
                    lru = self.dll.head.next
                    self.dll.remove(lru)
                    self.map.pop(lru.key, None)
                node = Node(key, value)
                self.map[key] = node
            self.dll.add_to_end(node)

    def invalidate_prefix(self, prefix: str):
        with self.lock:
            for k in list(self.map.keys()):
                if k.startswith(prefix):
                    node = self.map.pop(k, None)
                    if node:
                        self.dll.remove(node)

    def clear(self):
        with self.lock:
            self.map.clear()
            self.dll = DoublyLinkedList()


# ✅ THIS MUST BE AT MODULE LEVEL
app_cache = LRUCache()
