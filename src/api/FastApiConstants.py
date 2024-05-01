from enum import Enum

# list_num_mois = range(1, 11)
# mois = [str(x) + " mois" for x in list_num_mois]

# moins_1_an = ["debutant accepte", "tous niveaux d experience acceptes",
#               "aucune experience exigee"] + mois

# list_num = range(12, 50, 6)
# list_an = range(1, 4)

# mois_an = [str(x) + " mois" for x in list_num]
# mini_an = ["minimum " + str(x) + " ans" for x in list_an]
# ans = [str(x) + " an s " for x in list_an]
# exp_1_4 = ["experience exigee", "experience souhaitee",
#            "minimum 1 an"] + mini_an + mois_an + ans


class FastApiConstants(Enum):

    # LIST UNDER 1 YEAR OF EXPERIENCE

    MOINS_1_AN = ['debutant accepte', 'tous niveaux d experience acceptes', 'aucune experience exigee', '1 mois',
                  '2 mois', '3 mois', '4 mois', '5 mois', '6 mois', '7 mois', '8 mois', '9 mois', '10 mois', '11 mois']

    # LIST BETWEEN 1 YEAR AND <4 YEARS
    EXP_1_4 = ['experience exigee',
               'experience souhaitee',
               'minimum 1 an',
               'minimum 1 ans',
               'minimum 2 ans',
               'minimum 3 ans',
               '12 mois',
               '18 mois',
               '24 mois',
               '30 mois',
               '36 mois',
               '42 mois',
               '48 mois',
               '1 an s ',
               '2 an s ',
               '3 an s ']

    REGION_LIST = ["84", "32", "93", "44", "76", "28", "75", "24",
                   "27", "53", "94", "52", "11", "01", "02", "03", "04", "06"]
