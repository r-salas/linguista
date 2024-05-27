#
#
#   Types
#
#

class Categorical:

    def __init__(self, categories):
        self.categories = categories

    def __repr__(self):
        return f"Categorical({self.categories})"
