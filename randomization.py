import random
import constant as const
import sys

sys.path.append('../tests/')
import mytest_data

W = '\033[0m'  # white (normal)
R = '\033[31m'  # red
G = '\033[32m'  # green
O = '\033[33m'  # orange
B = '\033[34m'  # blue

random.seed(21) 

# The randomization aims to reduce the influence of "potential" mass spec performance fluctuations over time.
#       Therefore, it is mostly important when running cohorts of e.g. > 1 day.
#       Within one day we can run ~ 12-16 samples.
#       Thus, the randomization is actually most important when we have more >12-16 samples.
#       For the randomization itself it makes sense to have a few criteria.

# The idea of randomizing in blocks is that each of them represents the overall
#       experimental design. So, e.g. if we have 100 patient samples - 40 recurrence and 60 without recurrence),
#       it would be good to have the same ratio reflected in each block as good as possible.
#       At least aiming to have the overall distribution of a variable over the cohort similarly reflected in each block.
#       This will for sure not always work, e.g. having uneven numbers


def get_blocks_number_and_size(cohort_size: int, criteria: dict):
    """
    # The number of blocks should be a minimum of 4.
    # The maximum block size should be 8 samples per block
    # The minimum block size should be 2 samples per block
    :param cohort_size: len of original_data
    :param criteria: dict with randomization criteria
    :return: number_of_blocks, block_size
    """

    if not isinstance(cohort_size, int):
        raise TypeError("Number of samples must be int")

    number_of_blocks = 4  # minimum
    block_size = 8  # maximum

    if (const.AGE_STRINT in criteria.values()) and len(criteria) == 1:
        if cohort_size <= 8:
            number_of_blocks = 1
            block_size = 8
        elif cohort_size <= 10:
            number_of_blocks = 4
            block_size = (cohort_size + number_of_blocks - 1) // number_of_blocks
        elif cohort_size <= 50:
            if cohort_size % 8 == 0:
                number_of_blocks = cohort_size // 8
            else:
                number_of_blocks = cohort_size // 8 + 1
            block_size = (cohort_size + number_of_blocks - 1) // number_of_blocks
        elif cohort_size <= 100:
            if cohort_size % 8 == 0:
                number_of_blocks = cohort_size // 8
            else:
                number_of_blocks = cohort_size // 8 + 1
            block_size = (cohort_size + number_of_blocks - 1) // number_of_blocks
        return number_of_blocks, block_size


    elif len(criteria) == 1:
        if cohort_size <= 8:
            number_of_blocks = 1
            block_size = 8
        elif cohort_size <= 10:
            number_of_blocks = 2
            block_size = (cohort_size + number_of_blocks - 1) // number_of_blocks
        elif cohort_size <= 50:
            if cohort_size % 8 == 0:
                number_of_blocks = cohort_size // 8
            else:
                number_of_blocks = cohort_size // 8 + 1
            block_size = (cohort_size + number_of_blocks - 1) // number_of_blocks
        elif cohort_size <= 100:
            if cohort_size % 8 == 0:
                number_of_blocks = cohort_size // 8
            else:
                number_of_blocks = cohort_size // 8 + 1
            block_size = (cohort_size + number_of_blocks - 1) // number_of_blocks

    if len(criteria) == 2:
        if const.GENDER_STRING in criteria.values() and const.IS_TISSUE_TUMOR_STRING in criteria.values():
            if cohort_size <= 8:
                number_of_blocks = 2
                block_size = 8
            elif cohort_size <= 10:
                number_of_blocks = 4
                block_size = (cohort_size + number_of_blocks - 1) // number_of_blocks
            elif cohort_size <= 50:
                number_of_blocks = 5
                block_size = (cohort_size + number_of_blocks - 1) // number_of_blocks
            elif cohort_size <= 100:
                if cohort_size % 10 == 0:
                    number_of_blocks = cohort_size // 10
                else:
                    number_of_blocks = cohort_size // 10 + 1
                block_size = (cohort_size + number_of_blocks - 1) // number_of_blocks

            return number_of_blocks, block_size

        return "we have more then 4 classes"  # TODO

    return number_of_blocks, block_size


def randomize_gender(original_samples):
    """
    called when there is only one randomisation criteria - GENDER
    """
    cohort_size = len(original_samples)
    random.shuffle(original_samples)
    # todo: note, block_size is never used
    blocks_number, block_size = get_blocks_number_and_size(cohort_size,
                                                           const.GENDER_CRITERIA_DICT)
    male_samples = list(filter(lambda aliqout: aliqout[1] == 'MALE', original_samples))
    female_samples = list(filter(lambda aliqout: aliqout[1] == 'FEMALE', original_samples))
    num_male_samples, num_female_samples = len(male_samples), len(female_samples)
    male_ration = num_male_samples / cohort_size

    shuffled_list = spread_aliquots_gender(blocks_number, female_samples, male_samples)
    spread_leftovers_gender(blocks_number, female_samples, male_samples, shuffled_list)
    random.shuffle(shuffled_list)

    print_gender_randomization_info(cohort_size=cohort_size,
                                    blocks_number=len(shuffled_list),
                                    block_size=block_size,
                                    num_male_samples=num_male_samples,
                                    num_female_samples=num_female_samples,
                                    male_ration=male_ration,
                                    shuffled_list=shuffled_list)

    return shuffled_list, get_ids(shuffled_list)


def spread_aliquots_gender(blocks_number, female_samples, male_samples):
    len_male_samples, len_female_samples = len(male_samples), len(female_samples)
    shuffled_list = []
    for b_index in range(blocks_number):
        block = []
        for i in range(int(len_male_samples / blocks_number)):
            block.append(male_samples.pop(0))
        for i in range(int(len_female_samples / blocks_number)):
            block.append(female_samples.pop(0))
        random.shuffle(block)
        shuffled_list.append(block)
    return shuffled_list


def spread_leftovers_gender(blocks_number, female_samples, male_samples, shuffled_list):
    index = 0
    while male_samples:
        if index > blocks_number - 1:
            index = 0
        shuffled_list[index].append(male_samples.pop(0))
        random.shuffle(shuffled_list[index])
        index += 1
    while female_samples:
        if index > blocks_number - 1:
            index = 0
        shuffled_list[index].append(female_samples.pop(0))
        random.shuffle(shuffled_list[index])
        index += 1


def randomize_age(original_data):
    """
    called when there is only one randomisation criteria - AGE
    """
    age_groups = get_age_groups(3)
    cohort_size = len(original_data)
    random.shuffle(original_data)
    blocks_number, block_size = get_blocks_number_and_size(cohort_size,
                                                           const.AGE_CRITERIA)

    if len(age_groups) == 2:
        shuffled_list = randomize_age_for_2_groups(age_groups, blocks_number, cohort_size, original_data)

    elif len(age_groups) == 3:
        # add age_group information to aliquots
        age_data = []
        for aliquot in original_data:
            if int(aliquot[2]) <= 30:
                aliquot = aliquot + (const.AGE_GROUP_UNDER_30,)
            elif int(aliquot[2]) <= 60:
                aliquot = aliquot + (const.AGE_GROUP_UNDER_60,)
            else:
                aliquot = aliquot + (const.AGE_GROUP_OVER_60,)
            age_data.append(aliquot)

        age_1_samples = list(filter(lambda aliqout: aliqout[4] == str(age_groups[0]), age_data))
        age_2_samples = list(filter(lambda aliqout: aliqout[4] == age_groups[1], age_data))
        age_3_samples = list(filter(lambda aliqout: aliqout[4] == age_groups[2], age_data))
        num_age_1_samples = len(age_1_samples)
        num_age_2_samples = len(age_2_samples)
        num_age_3_samples = len(age_3_samples)
        age_1_ration = num_age_1_samples / cohort_size
        age_2_ration = num_age_2_samples / cohort_size
        age_3_ration = num_age_3_samples / cohort_size

        shuffled_list = []
        for b_index in range(blocks_number):
            block = []
            for i in range(int(num_age_1_samples / blocks_number)):
                block.append(age_1_samples.pop(0))
            for i in range(int(num_age_2_samples / blocks_number)):
                block.append(age_2_samples.pop(0))
            for i in range(int(num_age_3_samples / blocks_number)):
                block.append(age_3_samples.pop(0))
            random.shuffle(block)
            shuffled_list.append(block)

        spread_leftovers_age3(age_1_samples, age_2_samples, age_3_samples, blocks_number, shuffled_list)
        random.shuffle(shuffled_list)

    print_age_randomization_info(cohort_size=cohort_size,
                                 blocks_number=blocks_number,
                                 block_size=block_size,
                                 num_under30=num_age_1_samples,
                                 num_under60=num_age_2_samples,
                                 num_over60=num_age_3_samples,
                                 under30_ration=age_1_ration,
                                 shuffled_list=shuffled_list)

    return shuffled_list, get_ids(shuffled_list)


def spread_leftovers_age3(age_1_samples, age_2_samples, age_3_samples, blocks_number, shuffled_list):
    index = 0
    while age_1_samples:
        if index > blocks_number - 1:
            index = 0
        shuffled_list[index].append(age_1_samples.pop(0))
        random.shuffle(shuffled_list[index])
        index += 1
    while age_2_samples:
        if index > blocks_number - 1:
            index = 0
        shuffled_list[index].append(age_2_samples.pop(0))
        random.shuffle(shuffled_list[index])
        index += 1
    while age_3_samples:
        if index > blocks_number - 1:
            index = 0
        shuffled_list[index].append(age_3_samples.pop(0))
        random.shuffle(shuffled_list[index])
        index += 1


def randomize_age_for_2_groups(age_groups, blocks_number, cohort_size, original_data):
    # add age_group information to aliquots
    age_data = []
    for aliquot in original_data:
        if int(aliquot[2]) <= 50:
            aliquot = aliquot + (age_groups[0],)
        else:
            aliquot = aliquot + (age_groups[1],)
        age_data.append(aliquot)
    first_age_samples = list(filter(lambda aliqout: aliqout[4] == str(age_groups[0]), age_data))
    second_age_samples = list(filter(lambda aliqout: aliqout[4] == age_groups[1], age_data))
    num_first_age_samples = len(first_age_samples)
    num_second_age_samples = len(second_age_samples)
    first_age_ration = num_first_age_samples / cohort_size
    second_age_ration = num_second_age_samples / cohort_size
    shuffled_list = []
    for b_index in range(blocks_number):
        block = []
        for i in range(int(num_first_age_samples / blocks_number)):
            block.append(first_age_samples.pop(0))
        for i in range(int(num_second_age_samples / blocks_number)):
            block.append(second_age_samples.pop(0))
        random.shuffle(block)
        shuffled_list.append(block)
    return shuffled_list


def get_age_groups(num: int):
    if num == 2:
        return [const.AGE_GROUP_UNDER_50, const.AGE_GROUP_OVER_50]
    else:
        return [const.AGE_GROUP_UNDER_30, const.AGE_GROUP_UNDER_60, const.AGE_GROUP_OVER_60]


def randomize_istumor(original_data):
    """
    called when there is only one randomisation criteria - IS_TUMOR
    """
    cohort_size = len(original_data)
    random.shuffle(original_data)
    # todo: note, block_size is never used
    blocks_number, block_size = get_blocks_number_and_size(cohort_size,
                                                           const.TUMOR_CRITERIA_DICT)
    tumor_samples = list(filter(lambda aliqout: aliqout[3] == 'true', original_data))
    nottumor_samples = list(filter(lambda aliqout: aliqout[3] == 'false', original_data))
    num_tumor_samples = len(tumor_samples)
    num_nottumor_samples = len(nottumor_samples)
    shuffled_list = spread_aliquots_tumor(blocks_number, nottumor_samples, tumor_samples)
    spread_leftovers_istumor(blocks_number, nottumor_samples, tumor_samples, shuffled_list)
    random.shuffle(shuffled_list)

    print_tumor_randomization_info(cohort_size=cohort_size,
                                   blocks_number=len(shuffled_list),
                                   block_size=block_size,
                                   num_tumor_samples=num_tumor_samples,
                                   num_nottumor_samples=num_nottumor_samples,
                                   tum_ration=num_tumor_samples / cohort_size,
                                   shuffled_list=shuffled_list)

    return shuffled_list, get_ids(shuffled_list)


def spread_aliquots_tumor(blocks_number, nottumor_samples, tumor_samples):
    len_tumor_samples, len_nottumor_samples = len(tumor_samples), len(nottumor_samples)
    shuffled_list = []
    for b_index in range(blocks_number):
        block = []
        for i in range(int(len_tumor_samples / blocks_number)):
            block.append(tumor_samples.pop(0))
        for i in range(int(len_nottumor_samples / blocks_number)):
            block.append(nottumor_samples.pop(0))
        random.shuffle(block)
        shuffled_list.append(block)
    return shuffled_list


def spread_leftovers_istumor(blocks_number, nottumor_samples, tumor_samples, shuffled_list):
    index = 0
    while tumor_samples:
        if index > blocks_number - 1:
            index = 0
        shuffled_list[index].append(tumor_samples.pop(0))
        random.shuffle(shuffled_list[index])
        index += 1
    while nottumor_samples:
        if index > blocks_number - 1:
            index = 0
        shuffled_list[index].append(nottumor_samples.pop(0))
        random.shuffle(shuffled_list[index])
        index += 1


def randomize_gender_age():
    return "todo GENDER and AGE"


def randomize_gender_istumor(original_data):
    randomize_istumor_gender(original_data)
    return "todo GENDER and IS_TUMOR"


def randomize_age_gender(original_data):
    return "todo AGE and GENDER"


def randomize_age_istumor(original_data):
    return "todo AGE and IS_TUMOR"


def randomize_istumor_age():
    return "todo IS_TUMOR and AGE"


def randomize_istumor_gender(original_data):
    """
    called when randomization criteria are IS_TUMOR and GENDER
    """

    cohort_size = len(original_data)
    random.shuffle(original_data)

    for sample in original_data:
        print(sample)


    blocks_number, block_size = get_blocks_number_and_size(cohort_size,
                                                           {'RANDOMIZATION_1': 'IS_TUMOR',
                                                            'RANDOMIZATION_2': 'GENDER'})
    class_data = add_classname(original_data)
    for sample in class_data:
        print(sample)


    ind = 0
    for sample in class_data:
        ind += 1
        if sample[4] == const.CLASS_1:
            print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5}  ==>  {R + sample[4] + W:10}')
        elif sample[4] == const.CLASS_2:
            print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5}  ==>  {G + sample[4] + W:10}')
        elif sample[4] == const.CLASS_3:
            print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5}  ==>  {O + sample[4] + W:10}')
        elif sample[4] == const.CLASS_4:
            print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5}  ==>  {B + sample[4] + W:10}')
        else:
            print("WTF")



    classes = filter_classes(class_data)
    lens = len(classes[0]), len(classes[1]), len(classes[2]), len(classes[3])
    shuffled_list = spread_aliquots_tumor_gender(blocks_number, classes)
    spread_leftovers_istumor_gender(blocks_number, classes, shuffled_list)
    random.shuffle(shuffled_list)
    print_tumorGender_randomization_info(cohort_size=len(original_data),
                                         blocks_number=blocks_number,
                                         block_size=block_size,
                                         lens=lens,
                                         shuffled_list=shuffled_list)

    return shuffled_list, get_ids(shuffled_list)


def filter_classes(class_data):
    class_1 = list(filter(
        lambda aliquot: aliquot[3] == 'true' and aliquot[1] == 'MALE',
        class_data), )
    class_2 = list(filter(
        lambda aliquot: aliquot[3] == 'true' and aliquot[1] == 'FEMALE',
        class_data))
    class_3 = list(filter(
        lambda aliquot: aliquot[3] == 'false' and aliquot[1] == 'MALE',
        class_data))
    class_4 = list(filter(
        lambda aliquot: aliquot[3] == 'false' and aliquot[1] == 'FEMALE',
        class_data))
    return class_1, class_2, class_3, class_4


def spread_aliquots_tumor_gender(blocks_number, classes):
    lens = len(classes[0]), len(classes[1]), len(classes[2]), len(classes[3])
    shuffled_list = []
    for b_index in range(blocks_number):
        block = []
        for i in range(int(lens[0] / blocks_number)):
            block.append(classes[0].pop(0))
        for i in range(int(lens[1] / blocks_number)):
            block.append(classes[1].pop(0))
        for i in range(int(lens[2] / blocks_number)):
            block.append(classes[2].pop(0))
        for i in range(int(lens[3] / blocks_number)):
            block.append(classes[3].pop(0))
        random.shuffle(block)
        shuffled_list.append(block)
    return shuffled_list


def add_classname(original_data):
    class_data = []
    for aliquot in original_data:
        if aliquot[3] == 'true' and aliquot[1] == 'MALE':
            aliquot = aliquot + (const.CLASS_1,)
        elif aliquot[3] == 'true' and aliquot[1] == 'FEMALE':
            aliquot = aliquot + (const.CLASS_2,)
        elif aliquot[3] == 'false' and aliquot[1] == 'MALE':
            aliquot = aliquot + (const.CLASS_3,)
        elif aliquot[3] == 'false' and aliquot[1] == 'FEMALE':
            aliquot = aliquot + (const.CLASS_4,)
        class_data.append(aliquot)
    return class_data


def spread_leftovers_istumor_gender(blocks_number, classes, shuffled_list):
    index = 0
    while classes[0]:
        if index > blocks_number - 1:
            index = 0
        shuffled_list[index].append(classes[0].pop(0))
        random.shuffle(shuffled_list[index])
        index += 1
    while classes[1]:
        if index > blocks_number - 1:
            index = 0
        shuffled_list[index].append(classes[1].pop(0))
        random.shuffle(shuffled_list[index])
        index += 1
    while classes[2]:
        if index > blocks_number - 1:
            index = 0
        shuffled_list[index].append(classes[2].pop(0))
        random.shuffle(shuffled_list[index])
        index += 1
    while classes[3]:
        if index > blocks_number - 1:
            index = 0
        shuffled_list[index].append(classes[3].pop(0))
        random.shuffle(shuffled_list[index])
        index += 1


def randomize_gender_age_istumor():
    return "todo GENDER, AGE, IS_TUMOR"


def randomize_gender_istumor_age():
    return "todo GENDER, IS_TUMOR, AGE"


def randomize_age_gender_istumor():
    return "todo AGE, GENDER, IS_TUMOR"


def randomize_age_istumor_gender():
    return "todo AGE, IS_TUMOR, GENDER"


def randomize_istumor_gender_age():
    return "todo IS_TUMOR, GENDER, AGE"


def randomize_istumor_age_gender():
    return "todo IS_TUMOR, AGE, GENDER"


def randomize_it(original_data, criteria_dict: dict):
    """
    This is an umbrella method for randomization
    """
    if len(criteria_dict) == 1:
        if criteria_dict["RANDOMIZATION_1"] == const.GENDER_STRING:
            return randomize_gender(original_data)
        if criteria_dict["RANDOMIZATION_1"] == const.AGE_STRINT:
            return randomize_age(original_data)
        if criteria_dict["RANDOMIZATION_1"] == const.IS_TISSUE_TUMOR_STRING:
            return randomize_istumor(original_data)

    if len(criteria_dict) == 2:
        if (criteria_dict["RANDOMIZATION_1"] == const.GENDER_STRING) and (
                criteria_dict["RANDOMIZATION_2"] == const.AGE_STRINT):
            return randomize_gender_age()  # "todo GENDER and AGE"
        if (criteria_dict["RANDOMIZATION_1"] == const.GENDER_STRING) and (
                criteria_dict["RANDOMIZATION_2"] == const.IS_TISSUE_TUMOR_STRING):
            return randomize_gender_istumor(original_data)

        if (criteria_dict["RANDOMIZATION_1"] == const.AGE_STRINT) and (
                criteria_dict["RANDOMIZATION_2"] == const.GENDER_STRING):
            return randomize_age_gender()  # "todo AGE and GENDER"
        if (criteria_dict["RANDOMIZATION_1"] == const.AGE_STRINT) and (
                criteria_dict["RANDOMIZATION_2"] == const.IS_TISSUE_TUMOR_STRING):
            return randomize_age_istumor()  # "todo AGE and IS_TUMOR"

        if (criteria_dict["RANDOMIZATION_1"] == const.IS_TISSUE_TUMOR_STRING) and (
                criteria_dict["RANDOMIZATION_2"] == const.AGE_STRINT):
            return randomize_istumor_age()  # "todo IS_TUMOR and AGE"
        if (criteria_dict["RANDOMIZATION_1"] == const.IS_TISSUE_TUMOR_STRING) and (
                criteria_dict["RANDOMIZATION_2"] == const.GENDER_STRING):
            return randomize_istumor_gender(original_data)

    if len(criteria_dict) == 3:
        if criteria_dict["RANDOMIZATION_1"] == const.GENDER_STRING:
            if (criteria_dict["RANDOMIZATION_2"] == const.AGE_STRINT) and (
                    criteria_dict["RANDOMIZATION_3"] == const.IS_TISSUE_TUMOR_STRING):
                return randomize_gender_age_istumor()  # "todo GENDER, AGE, IS_TUMOR"
            if (criteria_dict["RANDOMIZATION_2"] == const.IS_TISSUE_TUMOR_STRING) and (
                    criteria_dict["RANDOMIZATION_3"] == const.AGE_STRINT):
                return randomize_gender_istumor_age()  # "todo GENDER, IS_TUMOR, AGE"

        if criteria_dict["RANDOMIZATION_1"] == const.AGE_STRINT:
            if (criteria_dict["RANDOMIZATION_2"] == const.GENDER_STRING) and (
                    criteria_dict["RANDOMIZATION_3"] == const.IS_TISSUE_TUMOR_STRING):
                return randomize_age_gender_istumor()  # "todo AGE, GENDER, IS_TUMOR"
            if (criteria_dict["RANDOMIZATION_2"] == const.IS_TISSUE_TUMOR_STRING) and (
                    criteria_dict["RANDOMIZATION_3"] == const.GENDER_STRING):
                return randomize_age_istumor_gender()  # "todo AGE, IS_TUMOR, GENDER"

        if criteria_dict["RANDOMIZATION_1"] == const.IS_TISSUE_TUMOR_STRING:
            if (criteria_dict["RANDOMIZATION_2"] == const.GENDER_STRING) and (
                    criteria_dict["RANDOMIZATION_3"] == const.AGE_STRINT):
                return randomize_istumor_gender_age()  # "todo IS_TUMOR, GENDER, AGE"
            if (criteria_dict["RANDOMIZATION_2"] == const.AGE_STRINT) and (
                    criteria_dict["RANDOMIZATION_3"] == const.GENDER_STRING):
                return randomize_istumor_age_gender()  # "todo IS_TUMOR, AGE, GENDER"
        else:
            return "didn't work"
    else:
        return "didn't work"


def process(original_samples):
    """service method. called from outside"""
    return randomize_gender(original_samples)



def print_age_randomization_info(cohort_size=None,
                                 blocks_number=None,
                                 block_size=None,
                                 num_under30=None,
                                 num_under60=None,
                                 num_over60=None,
                                 under30_ration=None,
                                 shuffled_list=None):
    print("\n\nTotal_samples: ", cohort_size)
    print("Blocks_number: ", blocks_number)
    print("Block_size: ", block_size)
    print("Number under 30: ", num_under30)
    print("Number under 60:", num_under60)
    print("Number over 60:", num_over60)
    print("Under30 ration", under30_ration)
    for b_index in range(blocks_number):
        print("block ", b_index, ": ")
        ind = 0
        for sample in shuffled_list[b_index]:
            ind += 1
            if sample[4] == get_age_groups(3)[0]:
                print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5}  ==>  {R + sample[4] + W:10}')
            elif sample[4] == get_age_groups(3)[1]:
                print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5}  ==>  {G + sample[4] + W:10}')
            elif sample[4] == get_age_groups(3)[2]:
                print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5}  ==>  {O + sample[4] + W:10}')
            else:
                print("WTF")


def print_tumorGender_randomization_info(cohort_size=None,
                                         blocks_number=None,
                                         block_size=None,
                                         lens=None,
                                         shuffled_list=None):
    print("\n\nTotal_samples: ", cohort_size)
    print("Blocks_number: ", blocks_number)
    print("Block_size: ", block_size)
    print("Class ", R + const.CLASS_1 + W, ": ", lens[0])
    print("Class ", G + const.CLASS_2 + W, ": ", lens[1])
    print("Class ", O + const.CLASS_3 + W, ": ", lens[2])
    print("Class ", B + const.CLASS_4 + W, ": ", lens[3])
    for b_index in range(blocks_number):
        print("block ", b_index + 1, ": ")
        ind = 0
        for sample in shuffled_list[b_index]:
            ind += 1
            if sample[4] == const.CLASS_1:
                print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5}  ==>  {R + sample[4] + W:10}')
            elif sample[4] == const.CLASS_2:
                print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5}  ==>  {G + sample[4] + W:10}')
            elif sample[4] == const.CLASS_3:
                print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5}  ==>  {O + sample[4] + W:10}')
            elif sample[4] == const.CLASS_4:
                print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5}  ==>  {B + sample[4] + W:10}')
            else:
                print("WTF")


def print_tumor_randomization_info(cohort_size=None,
                                   blocks_number=None,
                                   block_size=None,
                                   num_tumor_samples=None,
                                   num_nottumor_samples=None,
                                   tum_ration=None,
                                   shuffled_list=None):
    print("\n\nTotal_samples: ", cohort_size)
    print("Blocks number: ", blocks_number)
    print("Block size: ", block_size)
    print("Tumor samples: ", num_tumor_samples)
    print("Nottumor samples:", num_nottumor_samples)
    print("Tum_ration", tum_ration)
    print("int(tum_ration * cohort_size)", int(tum_ration * cohort_size))
    print("int(int(tum_ration * cohort_size) / blocks_number)", int(int(tum_ration * cohort_size) / blocks_number))
    for b_index in range(blocks_number):
        ind = 0
        print("block", b_index + 1, ": ")
        for sample in shuffled_list[b_index]:
            ind += 1
            if sample[3] == 'true':
                print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5} {R + "TUMOR" + W:5}')
            elif sample[3] == 'false':
                print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5} {G + "NOT_TUMOR" + W:5}')
            else:
                print("WTF")


def print_gender_randomization_info(cohort_size=None,
                                    blocks_number=None,
                                    block_size=None,
                                    num_male_samples=None,
                                    num_female_samples=None,
                                    male_ration=None,
                                    shuffled_list=None):
    print("\n\nTotal_samples: ", cohort_size)
    print("Blocks number: ", blocks_number)
    print("Block size: ", block_size)
    print("Male samples: ", num_male_samples)
    print("Female samples:", num_female_samples)
    print("Male_ration", male_ration)
    for b_index in range(blocks_number):
        print("block", b_index + 1, ": ")
        ind = 0
        for sample in shuffled_list[b_index]:
            ind += 1
            if sample[1] == 'MALE':
                print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5} {R + "MALE" + W:5}')
            elif sample[1] == 'FEMALE':
                print(f' {ind:2} {sample[0]:15} {sample[1]:7} {sample[2]:3} {sample[3]:5} {G + "FEMALE" + W:5}')
            else:
                print("WTF")


def get_ids(shuffled_list):
    """Returns list containing only ids"""
    shuffled_ids = []
    for block in shuffled_list:
        ids = []
        for aliquot in block:
            ids.append(aliquot[0])
        shuffled_ids.append(ids)
    return shuffled_ids
