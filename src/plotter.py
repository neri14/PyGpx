import matplotlib.pyplot as plt


def plot(*figures):
    for (data, label) in figures:
        plt.plot(data, label=label)
    plt.legend()
    plt.show()
