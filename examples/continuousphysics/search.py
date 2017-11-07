from IPython import embed
def search(x, arr):
    M = len(arr)
    if x > arr[M-1]:
        return M
    elif x <= arr[0]:
        return 0
    elif x > arr[M/2]:
        return search(x,arr[M/2:])
    else:
        return search(x,arr[:M/2])

if __name__ == '__main__':
	embed()