""" Profile speed of the different trees """

import os
import random
import time

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from core.trees.builtin_tree import BuiltinTree
from core.trees.two_three_tree import TwoThreeTree


class ProfileTreesSpeed:
    """ Run the speed profiling """

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

    def profile_tree_speed(self, tree_type, data_size):
        """ Profile the speed of the tree """
        # profile a single tree of a given type on a given data size
        result = {}
        tree = tree_type()

        # profile insertion
        random_elements = self.create_random_elements_list(data_size)
        start_time = time.time()

        for random_element in random_elements:
            tree.insert(str(random_element), random_element)

        end_time = time.time()
        result["insertion"] = end_time - start_time

        # profile the tree speed
        start_time = time.time()

        for random_element in self.create_random_elements_list(data_size):
            tree.contains(str(random_element))

        end_time = time.time()
        result["search"] = end_time - start_time

        # profile deletion
        start_time = time.time()

        for random_element in random_elements[:len(random_elements) // 3 + 1]:
            tree.delete(str(random_element))

        end_time = time.time()
        result["deletion"] = end_time - start_time

        return result

    def visualize(self, type_to_visualize="search"):
        """ Visualize the results of the profiling """
        # save the results as image using matplotlib
        print(f"Visualizing the results: {type_to_visualize}")

        # create a dataframe with the results
        df = pd.DataFrame(
            self.results,
            columns=["tree_type", "data_size", "insertion", "search", "deletion"]
        )

        # plot the results
        sns.lineplot(x="data_size", y=type_to_visualize, hue="tree_type", data=df)

        # add a legend and plot name
        plt.title(f"{type_to_visualize.capitalize()} time for different data sizes")
        plt.xlabel("Data size")
        plt.ylabel("Time")

        # save the plot
        plt.savefig(f"images/profile_speed_{type_to_visualize}.png")

        # show the plot
        plt.show()

    def run_speed_profile(self):
        """ Run the speed profiling """
        # profile the trees of different types on different data sizes
        for tree_type in self.trees:
            for data_size in self.data_sizes:
                print(f"Profiling {tree_type.__name__} on {data_size} elements")
                profile_results = self.profile_tree_speed(tree_type, data_size)
                print(f"Results of {tree_type.__name__} on {data_size} elements: {profile_results}")

                self.results.append(
                    [tree_type.__name__, data_size] + list(profile_results.values())
                )

        # visualize the results
        self.visualize("insertion")
        self.visualize("search")
        self.visualize("deletion")


if __name__ == '__main__':
    trees_to_profile = [BuiltinTree, TwoThreeTree]  # TODO [AVLTree, RedBlackTree, BTree, TwoThreeTree, SplayTree]
    data_sizes_to_test = [100, 150, 1000, 10000, 20000]
    profile = ProfileTreesSpeed(trees_to_profile, data_sizes_to_test)
    profile.run_speed_profile()
    print(profile.results)
