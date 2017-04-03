from Explorer import BuildExplorer
from pandas import DataFrame

class DataExtractor(BuildExplorer):
    def __init__(self, builds_dir, build_prefix):
        super(DataExtractor, self).__init__(builds_dir, build_prefix)

    def get_test_names(self, build_indices):
        test_names = set([])
        for i in build_indices:
            names = self.get_data(i).get_evaluation_test_names()
            test_names.update(names)
        return sorted(list(test_names))

    def get_build_names(self, build_indices):
        return [self.get_build_name(index) for index in build_indices]

    def get_test_scores(self, build_indices, test_names):
        builds = self.get_build_names(build_indices)
        series = []
        for index in build_indices:
            scores = dict(self.get_data(index).get_evaluation_scores())
            series.append([scores[t] for t in test_names])
        return DataFrame(data=series, index=builds, columns=test_names)
