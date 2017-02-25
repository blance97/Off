from queue import PriorityQueue

q = PriorityQueue(maxsize=2)
for i in range(15):
    q.put(i,i)

print(q.get())
print(q.get())