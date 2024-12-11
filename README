## Overview

This application connects a government issued ID (or other verification process) with a Starknet wallet, 
so that other blockchain apps can check that you are a unique human. 
It will also store some basic information (like date of birth) for each wallet, so the user of that wallet
can sign up for services which are age limited. 
The other identifying characteristics of the user remain hidden, so a user can remain anonymous but still 
can't register multiple times to each service. 

Each wallet signed up to the app is mapped unto three properties:
1) Hash of some government ID (in other words, a unique identifier). 
2) Date of birth of the person. 
3) Nationality (the country that issued the ID document used for verification). 

That means, if a user signs up with a wallet to some service (e.g., a social network) 
that service can quickly check if the person has the appropriate age (e.g., over 18), 
isn't a citizen of a sanctioned country, and that the user only has a single login for the service
(e.g., cannot run a bot farm). 

## Components

1) The identity proving service. This is a private or government service that
checks the person holds an ID card that matches his appearance. 
The service calculates a string with all the relevant details, 
makes a Merkle tree of the data, and signs the root of the tree. 
It can also send the data and tree but those can be calculated by the user. 

2) The user registers the Merkle root and signature of the authorized identity service 
on a smart contract on Starknet. The user must provide Merkle decommitments on his date of birth, 
nationality, and unique id (this can be a hash of the government ID). 

3) Any application (either on-chain or in general) can be logged in using the wallet address. 
The application checks the smart contract for age, nationality and uniqueness of the user. 
The user maintains anonymity but cannot register multiple accounts and can't register 
for age-inappropriate accounts. 
