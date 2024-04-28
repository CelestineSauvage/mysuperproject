from enum import Enum

list_num_mois = range(1, 11)
mois = [str(x) + " mois" for x in list_num_mois]

moins_1_an = ["debutant accepte", "tous niveaux d experience acceptes",
              "aucune experience exigee"] + mois

list_num = range(12, 50, 6)
list_an = range(1, 4)

mois_an = [str(x) + " mois" for x in list_num]
mini_an = ["minimum " + str(x) + " ans" for x in list_an]
ans = [str(x) + " an s " for x in list_an]
exp_1_4 = ["experience exigee", "experience souhaitee",
           "minimum 1 an"] + mini_an + mois_an + ans


class FastApiConstants(Enum):

    # LIST UNDER 1 YEAR OF EXPERIENCE

    MOINS_1_AN = moins_1_an

    # LIST BETWEEN 1 YEAR AND <4 YEARS
    EXP_1_4 = exp_1_4
