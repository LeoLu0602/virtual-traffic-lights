from monitor import Monitor

def main():
	T = 10 # update frequency
	monitor = Monitor(1, 2, T)
	monitor.start()

if __name__ == '__main__':
	main()