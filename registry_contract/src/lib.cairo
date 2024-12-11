/// An Entity registry contract.
#[starknet::interface]
pub trait IEntityRegistry<TContractState> {
    /// Register a new {SN address -> entity} connection.
    /// The merkle tree is expected to have the SN address in its leftmost leaf, and the hash(ID)
    /// in its second leaf.
    fn register_account(
        ref self: TContractState,
        root: felt252,
        id_hash: felt252,
        id_hash_merkle_path: Span<felt252>,
        address_merkle_path: Span<felt252>,
        signature: Span<felt252>
    );
}


#[derive(Drop, Serde, starknet::Store)]
struct Entity {
    root: felt252,
    id_hash: felt252,
}

#[starknet::contract]
mod EntityRegistry {
    use super::Entity;
    use starknet::storage::{
        StoragePointerReadAccess, StoragePointerWriteAccess, StoragePathEntry, Map,
    };
    use core::starknet::{ContractAddress, get_caller_address};
    use core::ecdsa::check_ecdsa_signature;
    use core::pedersen::pedersen;

    const ADDRESS_INDEX: u8 = 0_u8;
    const ID_HASH_INDEX: u8 = 1_u8;


    #[storage]
    struct Storage {
        account_to_entity: Map<ContractAddress, Entity>,
        governance_public_key: felt252,
    }

    #[constructor]
    fn constructor(ref self: ContractState, governance_public_key: felt252) {
        self.governance_public_key.write(governance_public_key);
    }

    fn verify_merkle_path(
        root: felt252, merkle_path: Span<felt252>, mut index: u8, value: felt252
    ) -> bool {
        let mut current_hash = pedersen(value, 0);
        for i in 0
            ..merkle_path
                .len() {
                    let sibling = *merkle_path.at(i);
                    let (left, right) = if index & 1_u8 == 0_u8 {
                        (current_hash, sibling)
                    } else {
                        (sibling, current_hash)
                    };
                    current_hash = pedersen(left, right);
                    index /= 2;
                };
        current_hash == root
    }

    #[abi(embed_v0)]
    impl EntityRegistryImpl of super::IEntityRegistry<ContractState> {
        fn register_account(
            ref self: ContractState,
            root: felt252,
            id_hash: felt252,
            id_hash_merkle_path: Span<felt252>,
            address_merkle_path: Span<felt252>,
            signature: Span<felt252>
        ) {
            assert(signature.len() == 2_u32, 'INVALID_SIGNATURE_LENGTH'); // Check signature length.

            // Verify ECDSA signature.
            assert(
                check_ecdsa_signature(
                    message_hash: root,
                    public_key: self.governance_public_key.read(),
                    signature_r: *signature.at(0_u32),
                    signature_s: *signature.at(1_u32),
                ),
                'INVALID_SIGNATURE',
            );

            // Verify Merkle Paths.
            assert(id_hash_merkle_path.len() == 3_u32, 'INVALID_MERKLE_PATH_LENGTH');
            assert(address_merkle_path.len() == 3_u32, 'INVALID_MERKLE_PATH_LENGTH');
            let address = get_caller_address();
            assert(
                verify_merkle_path(
                    root: root,
                    merkle_path: address_merkle_path,
                    index: ADDRESS_INDEX,
                    value: 1926620936695478438856464323891613522855988234423992806332074754206677183311,
                ),
                'INVALID_ADDRESS',
            );
            assert(
                verify_merkle_path(
                    root: root,
                    merkle_path: id_hash_merkle_path,
                    index: ID_HASH_INDEX,
                    value: id_hash,
                ),
                'INVALID_ID_HASH',
            );
            let entity = Entity { root: root, id_hash };
            self.account_to_entity.entry(address).write(entity);
        }
    }
}
