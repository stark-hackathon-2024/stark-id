
import math
from fast_pedersen_hash import pedersen_hash
from utils import from_bytes

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
            tree_representation += " ".join([f"{str(hex(x))[:5]}" for x in level]) + "\n"
        return tree_representation

if __name__ == "__main__":
    data = ["Alice", "Bob", "Charlie", "David", "Eve"]
    merkle_tree = PedersenMerkleTree(data)
    print("Merkle Tree Visualization:")
    print(merkle_tree.visualize_tree())
    print("Root Hash:", str(hex(merkle_tree.get_root()))[:5])
    index = 2
    decommitment_path = merkle_tree.get_decommitment_path(index)
    print(f"Decommitment Path for Leaf {index}:", [str(hex(x))[:5] for x in merkle_tree.get_decommitment_path(index)])
    print("Proof Verification:", merkle_tree.verify_proof(merkle_tree.leaves[index], decommitment_path, merkle_tree.get_root(), index))