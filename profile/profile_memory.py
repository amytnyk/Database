""" Profile memory of the different trees """

import os
import random

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from memory_profiler import memory_usage

from core.trees.builtin_tree import BuiltinTree
from core.trees.two_three_tree import TwoThreeTree


class ProfileTreesMemory:
    """ Run the profiling """

    def __init__(self, trees, data_sizes):
        self.trees = trees
        self.data_sizes = data_sizes
        self.results = []
        self.create_folder_for_images()

    @classmethod
    def create_folder_for_images(cls):
        """ Create the folder for the images """
        if not os.path.exists("images"):
            os.makedirs("images")

    @classmethod
    def create_random_elements_list(cls, data_size):
        """ Create a list of random elements """
        # elements should not repeat in the list
        elements = []
        for _ in range(data_size):
            random_element = random.randint(0, data_size * 100)
            while random_element in elements:
                random_element = random.randint(0, data_size * 100)
            elements.append(random_element)
        return elements

    def profile_tree_memory(self, tree_type, data_size):
        """ Profile the memory of the tree """
        # profile a single tree of a given type on a given data size
        tree = tree_type()
        random_elements = self.create_random_elements_list(data_size)

        for random_element in random_elements:
            try:
                tree.insert(str(random_element), random_element)
            except Exception as e:
                pass

        for random_element in self.create_random_elements_list(data_size):
            try:
                tree.contains(str(random_element))
            except Exception as e:
                pass

        for random_element in random_elements[:len(random_elements) // 3 + 1]:
            try:
                tree.delete(str(random_element))
            except Exception as e:
                pass

    def visualize(self):
        """ Visualize the results of the profiling """
        # save the results as image using matplotlib
        print("Visualizing the results")

        # create a dataframe with the results
        df = pd.DataFrame(self.results, columns=["tree_type", "data_size", "memory"])

        # plot the results
        sns.lineplot(x="data_size", y="memory", hue="tree_type", data=df)

        # add a legend and plot name
        plt.title("Memory for different data sizes")
        plt.xlabel("Data size")
        plt.ylabel("Memory (MB)")

        # save the plot
        plt.savefig("images/profile_memory.png")

        # show the plot
        plt.show()

    def run_memory_profile(self):
        """ Run the memory profiling """
        # profile the trees of different types on different data sizes
        for tree_type in self.trees:
            for data_size in self.data_sizes:
                print(f"Profiling {tree_type.__name__} on {data_size} elements")
                profile_results = memory_usage((self.profile_tree_memory, (tree_type, data_size)))
                print(f"Results of {tree_type.__name__} on {data_size} elements: {profile_results}")

                self.results.append([tree_type.__name__, data_size, max(profile_results)])

        # visualize the results
        self.visualize()


if __name__ == '__main__':
    trees_to_profile = [BuiltinTree, TwoThreeTree]  # TODO [AVLTree, RedBlackTree, BTree, TwoThreeTree, SplayTree]
    data_sizes_to_test = [100, 150, 1000, 10000, 20000]
    profile = ProfileTreesMemory(trees_to_profile, data_sizes_to_test)
    profile.run_memory_profile()
    print(profile.results)
