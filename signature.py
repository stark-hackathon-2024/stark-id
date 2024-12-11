###############################################################################
# Copyright 2019 StarkWare Industries Ltd.                                    #
#                                                                             #
# Licensed under the Apache License, Version 2.0 (the "License").             #
# You may not use this file except in compliance with the License.            #
# You may obtain a copy of the License at                                     #
#                                                                             #
# https://www.starkware.co/open-source-license/                               #
#                                                                             #
# Unless required by applicable law or agreed to in writing,                  #
# software distributed under the License is distributed on an "AS IS" BASIS,  #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    #
# See the License for the specific language governing permissions             #
# and limitations under the License.                                          #
###############################################################################

import hashlib
import json
import math
import os
import secrets
from typing import Optional, Tuple, Union


PEDERSEN_HASH_POINT_FILENAME = os.path.join(os.path.dirname(__file__), "pedersen_params.json")
PEDERSEN_PARAMS = json.load(open(PEDERSEN_HASH_POINT_FILENAME))

FIELD_PRIME = PEDERSEN_PARAMS["FIELD_PRIME"]
FIELD_GEN = PEDERSEN_PARAMS["FIELD_GEN"]
ALPHA = PEDERSEN_PARAMS["ALPHA"]
BETA = PEDERSEN_PARAMS["BETA"]
EC_ORDER = PEDERSEN_PARAMS["EC_ORDER"]
CONSTANT_POINTS = PEDERSEN_PARAMS["CONSTANT_POINTS"]

N_ELEMENT_BITS_ECDSA = math.floor(math.log(FIELD_PRIME, 2))
assert N_ELEMENT_BITS_ECDSA == 251

N_ELEMENT_BITS_HASH = FIELD_PRIME.bit_length()
assert N_ELEMENT_BITS_HASH == 252

# Elliptic curve parameters.
assert 2 ** N_ELEMENT_BITS_ECDSA < EC_ORDER < FIELD_PRIME

SHIFT_POINT = CONSTANT_POINTS[0]
MINUS_SHIFT_POINT = (SHIFT_POINT[0], FIELD_PRIME - SHIFT_POINT[1])
EC_GEN = CONSTANT_POINTS[1]

assert SHIFT_POINT == [
    0x49EE3EBA8C1600700EE1B87EB599F16716B0B1022947733551FDE4050CA6804,
    0x3CA0CFE4B3BC6DDF346D49D06EA0ED34E621062C0E056C1D0405D266E10268A,
]
assert EC_GEN == [
    0x1EF15C18599971B7BECED415A40F0C7DEACFD9B0D1819E03D723D8BC943CFCA,
    0x5668060AA49730B7BE4801DF46EC62DE53ECD11ABE43A32873000C36E8DC1F,
]


#########
# ECDSA #
#########

# A type for the digital signature.
ECSignature = Tuple[int, int]


