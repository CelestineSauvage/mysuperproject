#!/bin/bash

CLIENT_ID='PAR_jobmarketdatascientes_61aafad40553798b7d6198a1ece509eb5e20a3b1d239b478c3e09207209c9200'
CLIENT_SECRET='cdde83cbc9fb9d77ceb336af8d0dbacc1c11aaab3cd302f70792ab3c3a338e50'

xh post https://entreprise.pole-emploi.fr/connexion/oauth2/access_token\?realm\=%2Fpartenaire --form grant_type=client_credentials client_id=$CLIENT_ID client_secret=$CLIENT_SECRET scope='api_offresdemploiv2 o2dsoffre'

## OU
#curl --location 'https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire' \
#--header 'Content-Type: application/x-www-form-urlencoded' \
#--data-urlencode 'grant_type=client_credentials' \
#--data-urlencode 'scope=api_offresdemploiv2 o2dsoffre' \
#--data-urlencode 'client_id=PAR_jobmarketdatascientes_61aafad40553798b7d6198a1ece509eb5e20a3b1d239b478c3e09207209c9200' \
#--data-urlencode 'client_secret=cdde83cbc9fb9d77ceb336af8d0dbacc1c11aaab3cd302f70792ab3c3a338e50'
