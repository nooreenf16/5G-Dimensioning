import numpy as np
import matplotlib.pyplot as plt
import math

minx = 13574281.85229575
maxx = 13578281.85229575
# miny = 4493269.422941204
# maxy = 4494193.183371907


def space(s, e, n):
    arr = [s]
    i = 1
    r = math.exp((np.log(e/s) / (n-1)))
    print(r)
    while i < n:
        arr.append(arr[-1] * r)
        i += 1
    return arr


# space(minx, maxx, 3)

arr = space(minx, maxx, 500)
print(arr, '\n\n', arr[0], arr[-1], len(arr))


def mesh():
    # nx, ny = (3, 2)
    x = np.array(space(-13578281.85229575, -13574281.85229575, 11))
    y = np.array(space(4493269.422941204, 4494193.183371907, 11))
    # xv, yv = np.meshgrid(x, y, sparse=False, indexing='ij')
    # print(x, '\n', y)
    print(len(x), len(y))
    # plt.plot(xv, yv, marker='o', color='k', linestyle='none')
    # plt.show()


def logg(minx, maxx, miny, maxy):
    arr = []
    # maxx, maxy = (maxx-minx)/minx*10000, (maxy-miny)/miny*10000
    # minx, miny = 0, 0
    minx, miny, maxx, maxy = np.log(minx), np.log(
        miny), np.log(maxx), np.log(maxy)
    x = np.logspace(minx,
                    maxx, num=10)
    y = np.logspace(miny,
                    maxy, num=10)
    # print([val for val in x])
    xv, yv = np.meshgrid(x, y, sparse=False, indexing='ij')
    plt.plot(xv, yv, marker='o', color='k', linestyle='none')
    plt.show()


# # logg(minx, maxx, miny, maxy)

# x = np.geomspace(1,
#                  2.9, num=10)
# y = np.geomspace(1,
#                  2.9, num=10)
# xv, yv = np.meshgrid(x, y, sparse=False, indexing='ij')


# x_axis = np.linspace(
#     minx, maxx, num=11
# )

# print(len(x_axis))
