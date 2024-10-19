from monitor import Monitor

def main():
	T = 3 # update frequency
	monitor = Monitor(1, 1, T)
	monitor.start()

if __name__ == '__main__':
	main()