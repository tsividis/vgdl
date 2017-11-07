from threading import Thread
from threading import Lock
from time import sleep

queue = range(1,10)

lock = Lock()

def pick1():
	while len(queue) > 0:
		lock.acquire()
		try:
			best = max(queue)
			print("Thread 1 found {}".format(best))
			queue.remove(best)
			if best > 1:
				queue.append(best-1)
			sleep(20)
		finally:
			lock.release()
		sleep(1)
		print("1 is waiting")

def pick2():
	while len(queue) > 0:
		lock.acquire()
		try:
			best = max(queue)
			print("Thread 2 found {}".format(best))
			queue.remove(best)
			if best > 1:
				queue.append(best-1)
		finally:
			lock.release()
		print("2 is waiting")

thread1 = Thread(target=pick1)
thread2 = Thread(target=pick2)

thread1.start()
thread2.start()

thread1.join()
thread2.join()
