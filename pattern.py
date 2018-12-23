import matplotlib.pyplot as plt
import numpy as np


class Pattern:
    """
    Pattern is a configuration of tiles from the input image.
    """
    index_to_pattern = {}
    color_to_index = {}
    index_to_color = {}

    def __init__(self, data, index):
        self.index = index
        self.data = np.array(data)
        self.legal_patterns_index = {}  # offset -> [pattern_index]

    def get(self, index=None):
        if index is None:
            return self.data.item(0)
        reversed_index = index[::-1]
        return self.data[reversed_index]

    def set_legal_patterns(self, offset, legal_patterns):
        self.legal_patterns_index[offset] = legal_patterns

    @property
    def shape(self):
        return self.data.shape

    def is_compatible(self, candidate_pattern, offset):
        """
        Check if pattern is compatible with a candidate pattern for a given offset
        :param candidate_pattern:
        :param offset:
        :return: True if compatible
        """
        assert (self.shape == candidate_pattern.shape)

        # Precomputed compatibility
        if offset in self.legal_patterns_index:
            return candidate_pattern.index in self.legal_patterns_index[offset]

        # Computing compatibility
        ok_constraint = True
        start = tuple(max(offset[i], 0) for i, _ in enumerate(offset))
        end = tuple(min(self.shape[i] + offset[i], self.shape[i]) for i, _ in enumerate(offset))
        for index in np.ndindex(end):  # index = (x, y, z...)
            start_constraint = True
            for i, d in enumerate(index):
                if d < start[i]:
                    start_constraint = False
                    break
            if not start_constraint:
                continue

            if candidate_pattern.get(tuple(np.array(index) - np.array(offset))) != self.get(index):
                ok_constraint = False
                break

        # Old code, only for 2D
        # start_x = max(offset[0], 0)
        # start_y = max(offset[1], 0)
        #
        # end_x = min(self.shape[0] + offset[0], self.shape[0])
        # end_y = min(self.shape[1] + offset[1], self.shape[1])
        # ok_constraint = True
        # for x in range(start_x, end_x):
        #     for y in range(start_y, end_y):
        #         if candidate_pattern.get((x - offset[0], y - offset[1])) != self.get((x, y)):
        #             ok_constraint = False
        #             break

        return ok_constraint

    @staticmethod
    def from_sample(sample):
        """
        Compute patterns from sample
        :param sample:
        :return: list of patterns
        """
        if len(sample.shape) < 3:
            plt.imshow(np.expand_dims(sample, axis=0))
        else:
            plt.imshow(sample)
        plt.show()

        sample = Pattern.sample_img_to_indexes(sample)

        shape = sample.shape
        patterns = []
        pattern_size = (2, 2)
        pattern_index = 0

        for index, _ in np.ndenumerate(sample):
            # Checking if index is out of bounds
            out = False
            for i, d in enumerate(index):  # d is a dimension, e.g.: x, y, z
                if d > shape[i] - pattern_size[i]:
                    out = True
                    break
            if out:
                continue

            pattern_location = [range(d, pattern_size[i] + d) for i, d in enumerate(index)]
            pattern_data = sample[np.ix_(*pattern_location)]

            datas = [pattern_data]
            if len(index) > 1:
                datas.append(np.fliplr(pattern_data))
                datas.append(np.flipud(pattern_data))
                datas.append(np.rot90(pattern_data))
                datas.append(np.rot90(pattern_data, 2))

            # Checking existence
            # TODO: more probability to multiple occurrences when observe phase
            for data in datas:
                exist = False
                for p in patterns:
                    if (p.data == data).all():
                        exist = True
                        break
                if exist:
                    continue

                pattern = Pattern(data, pattern_index)
                patterns.append(pattern)
                Pattern.index_to_pattern[pattern_index] = pattern
                pattern_index += 1

        Pattern.plot_patterns(patterns)
        return patterns

    @staticmethod
    def sample_img_to_indexes(sample):
        """
        Convert a rgb image to a 2D array with pixel index
        :param sample:
        :return: pixel index sample
        """
        Pattern.color_to_index = {}
        Pattern.index_to_color = {}
        sample_index = np.zeros(sample.shape[:-1])  # without last rgb dim
        color_number = 0
        for index in np.ndindex(sample.shape[:-1]):
            color = tuple(sample[index])
            if color not in Pattern.color_to_index:
                Pattern.color_to_index[color] = color_number
                Pattern.index_to_color[color_number] = color
                color_number += 1

            sample_index[index] = Pattern.color_to_index[color]

        print('Unique color count = ', color_number)
        return sample_index

    @staticmethod
    def index_to_img(sample):
        image = np.zeros(sample.shape + (3,))
        for index in np.ndindex(sample.shape):
            pattern_index = sample[index]
            if pattern_index == -1:
                image[index] = [0.5, 0.5, 0.5]  # Grey
            else:
                image[index] = Pattern.index_to_color[pattern_index]
        return image

    @staticmethod
    def plot_patterns(patterns, title=''):
        fig = plt.figure(figsize=(8, 8))
        fig.suptitle(title, fontsize=16)
        columns = 4
        rows = 5
        for i in range(1, columns * rows + 1):
            if i > len(patterns):
                break
            fig.add_subplot(rows, columns, i)

            image = Pattern.index_to_img(patterns[i - 1].data)

            if len(image.shape) < 3:
                plt.imshow(np.expand_dims(image, axis=0))
            else:
                plt.imshow(image)

        plt.show()

    @staticmethod
    def from_index(pattern_index):
        return Pattern.index_to_pattern[pattern_index]
