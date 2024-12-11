
import math
from fast_pedersen_hash import pedersen_hash
from utils import from_bytes, to_bytes
from ecdsa import SigningKey, SECP256k1
import json
from starkware.crypto.signature.signature import sign

# # Dummy implementation of pedersen_hash function
# def pedersen_hash(left, right):
#     return (left + right) % (2**256)

class PedersenMerkleTree:
    def __init__(self, data):
        self.data = data
        self.leaves = [self.hash_data(d) for d in data]  # Hash all leaves
        self.tree = self.build_tree(self.leaves)  # Build the tree from the leaves

    # Function to hash data using Pedersen hash
    def hash_data(self, data):
        # Convert string data to integers for Pedersen hashing
        if isinstance(data, int):
            data_as_int = data
        else:
            data_as_int = from_bytes(data.encode(), "big")
        return pedersen_hash(data_as_int, 0)  # Hash with an initial value of 0

    # Function to build the Merkle tree
    def build_tree(self, leaves):
        tree = []
        tree.append(leaves)
        while len(leaves) > 1:
            if len(leaves) % 2 != 0:
                leaves.append(leaves[-1])  # Duplicate the last node if odd number of leaves
            # Hash pairs of nodes to create the next level
            leaves = [pedersen_hash(leaves[i], leaves[i + 1]) for i in range(0, len(leaves), 2)]
            tree.append(leaves)
        return tree

    # Function to get the Merkle root
    def get_root(self):
        return self.tree[-1][0]  # The root is the last element in the tree structure

    # Function to get the decommitment path for a given leaf index
    def get_decommitment_path(self, index):
        path = []
        level_index = index
        for level in self.tree[:-1]:  # Exclude the root level
            if level_index % 2 == 0:  # Current node is even, sibling is the next node
                if level_index + 1 < len(level):
                    path.append(level[level_index + 1])
            else:  # Current node is odd, sibling is the previous node
                path.append(level[level_index - 1])
            level_index //= 2
        return path

    # Function to verify a proof
    @staticmethod
    def verify_proof(leaf_hash, decommitment_path, root, index):
        current_hash = leaf_hash
        for sibling in decommitment_path:
            if index % 2 == 0:  # Even index, sibling is on the right
                current_hash = pedersen_hash(current_hash, sibling)
            else:  # Odd index, sibling is on the left
                current_hash = pedersen_hash(sibling, current_hash)
            index //= 2
        return current_hash == root

    # Function to visualize the tree
    def visualize_tree(self):
        tree_representation = ""
        for level in self.tree:
            # tree_representation += " ".join(map(str, level)) + "\n"
            tree_representation += " ".join([f"{str(hex(x))}" for x in level]) + "\n"
        return tree_representation
    
def generate_merkle_tree_and_signature(**fields):
    # Create a Merkle tree
    tree = PedersenMerkleTree([value for key, value in fields.items()])

    # Get the root of the Merkle tree
    root_hash = tree.get_root()

    # Generate a signing key (use your persistent private key in production)
    # sk = SigningKey.generate(curve=SECP256k1)
    # vk = sk.get_verifying_key()
    with open('keys', 'r') as f:
        key_data = json.load(f)
        sk = key_data['private']
        
        vk = key_data['public']
    

    # Sign the root hash
    # signature = sk.sign_deterministic(to_bytes(root_hash))
    signature = sign(root_hash, int(sk))
    signature = (signature[0], signature[1])

    # Get a visualization of the tree
    tree_representation = tree.visualize_tree()

    return {
        'merkle_tree': tree,
        'root_hash': root_hash,
        'signature': signature,
        'verifying_key': vk,
        'tree_representation': tree_representation
    }

if __name__ == "__main__":
    # data = ["Alice", "Bob", "Charlie", "David", "Eve"]
    # merkle_tree = PedersenMerkleTree(data)
    # print("Merkle Tree Visualization:")
    # print(merkle_tree.visualize_tree())
    # print("Root Hash:", str(hex(merkle_tree.get_root()))[:5])
    # index = 2
    # decommitment_path = merkle_tree.get_decommitment_path(index)
    # print(f"Decommitment Path for Leaf {index}:", [str(hex(x))[:5] for x in merkle_tree.get_decommitment_path(index)])
    # print("Proof Verification:", merkle_tree.verify_proof(merkle_tree.leaves[index], decommitment_path, merkle_tree.get_root(), index))
    # print()

    first_name = "Gali"
    last_name = "Michlevich"
    id_number = 12345679
    date_of_birth = "2024-12-12"
    nationality = "Israeli"
    starknet_address = 1926620936695478438856464323891613522855988234423992806332074754206677183311
    favorite_color = "Red"
    favorite_animal = "Dog"

    fields = {
                "starknet_address": int(starknet_address),
                "id_number_hash": pedersen_hash(int(id_number), 0),
                "first_name": first_name,
                "last_name": last_name,
                "date_of_birth": str(date_of_birth),
                "nationality": nationality,
                "favorite_color": favorite_color,
                "favorite_animal": favorite_animal
            }

    result = generate_merkle_tree_and_signature(**fields)
    output_text = (f"Name: {first_name} {last_name}, ID: {id_number}, DOB: {date_of_birth}, Nationality: {nationality} \n"
                           f"Starknet Address: {starknet_address} \n Favorite Color: {favorite_color}, Favorite Animal: {favorite_animal} \n\n")
    output_text += (f"Hashed ID: {pedersen_hash(int(id_number), 0)}\n")
    output_text += (f"Root Hash: {result['root_hash']}\n\n")
    output_text += (f"Signature: {result['signature']} \n")
    output_text += (f"Verifying Key: {result['verifying_key']} \n")
    output_text += (f"\nMerkle Tree Visualization:\n{result['tree_representation']}")
    print(output_text)