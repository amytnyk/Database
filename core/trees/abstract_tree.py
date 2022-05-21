class AbstractTree:
    def insert(self, key, value):
        """
        Inserts key-value pair into the tree
        Overwrites the existing record if the key is already in the tree
        :param key:
        :param value:
        :return: None
        """
        pass

    def get(self, key):
        """
        Returns value for the given key
        Raises KeyError if the tree does not contain the given key
        :param key:
        :return:
        """
        pass

    def contains(self, key) -> bool:
        """
        Check if the tree contains the given key
        :param key:
        :return:
        """
        pass

    def delete(self, key):
        """
        Deletes the given key from the tree
        :param key:
        :return:
        """
        pass

    def __iter__(self):
        pass

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.insert(key, value)

    def __contains__(self, item):
        return self.contains(item)
