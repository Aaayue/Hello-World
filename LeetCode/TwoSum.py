"""
给定一个整数数组和一个目标值，找出数组中和为目标值的两个数。

你可以假设每个输入只对应一种答案，且同样的元素不能被重复利用。
"""
import numpy as np


# class Solution:
class Solution:
    def __init__(self):
        pass

    def twoSum(self, nums, target):
        nums = np.array(nums)
        for i in range(len(nums)):
            dist = target - nums[i]
            tmp = np.where(nums == dist)[0]
            print(type(dist), type(nums), tmp)
            # print(len(tmp))
            if len(tmp) == 0:
                print('None')
                continue
            else:
                if i not in tmp:
                    # print([i, tmp[0]])
                    return [i, tmp[0]]
        return False
