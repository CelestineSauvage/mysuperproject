from FranceEmploiApiCaller import FranceEmploiApiCaller


france_emploi_client_id = "PAR_francetravailpourproj_07af7086caa6684d7bfdeb93773ac2232bcab87c28126890c3dd2c3a7d41ae23"
france_emploi_client_secret = "61bd84de5eacdf9e4654c8bd3e67faff2781e5a93fa9c1186baa274a2bf933d3"

franceEmploi = FranceEmploiApiCaller(france_emploi_client_id, france_emploi_client_secret)

# Authenticate to the France Emploi services
access_token = franceEmploi.get_access_token("api_offresdemploiv2 o2dsoffre", {"realm": "/partenaire"})

# Gets the jobs list with the criteria (=filter) on 'departement' with value '30'
jobs = franceEmploi.get_offres_demploi_par_criteres(access_token, {"departement":"30"})

# Showing the first job from the obtained list
print(jobs['resultats'][0])