use starknet::contract_address_const;

use snforge_std::{declare, ContractClassTrait, DeclareResultTrait, start_cheat_caller_address};

use stark_id_registry::IEntityRegistryDispatcher;
use stark_id_registry::IEntityRegistryDispatcherTrait;

const CALLER_ADDRESS: felt252 =
    1926620936695478438856464323891613522855988234423992806332074754206677183311;

fn deploy_contract() -> IEntityRegistryDispatcher {
    let contract = declare("EntityRegistry").unwrap().contract_class();
    let public_key = 0xa9f759e6432919d58733fef1cfd9f03d3942cda5d9a81d3a47205193e5de3b;
    let (contract_address, _) = contract.deploy(@array![public_key]).unwrap();
    let caller_address = contract_address_const::<CALLER_ADDRESS>();
    start_cheat_caller_address(contract_address, caller_address);
    IEntityRegistryDispatcher { contract_address }
}

#[test]
fn test_register_account() {
    let dispatcher = deploy_contract();
    let root_hash = 0x402ba99b21668afd3616d33ee925664fd553710e55e6c609b2f4bd94fce512a;
    let id_hash = 0x719394e8395aa3ccc0b93cd438d3f3eff1c16c880e1a9069b5aeaaec6b3d639;
    let id_hash_merkle_path = array![
        0x42612868095f22ced7bd6e6be9daa7215889246b0e174e4f4e49e70027ae59c,
        0x7096c5ffb4b209b3f1c5c566e871890ebb27d9cb6e5da6083c08c43e90931a1,
        0x53f4b1b6f1b096beaf8f297b85ccf903177cae44edece2a5a07f66e007a24f6
    ]
        .span();
    let address_merkle_path = array![
        0x2f3544e0082cadc135827922c83fb0d5fdd070f26a64094c7630d3e23e231e1,
        0x7096c5ffb4b209b3f1c5c566e871890ebb27d9cb6e5da6083c08c43e90931a1,
        0x53f4b1b6f1b096beaf8f297b85ccf903177cae44edece2a5a07f66e007a24f6
    ]
        .span();
    let signature = array![
        0xba478beedfeb849a62add751fb26b71f42e8e6a59e157a4a9e7e6a5946b39e,
        0x6fe66f40f28415bc94496bdabe26df929c1017c590953267afa6f6e8e5e145e
    ]
        .span();

    dispatcher
        .register_account(root_hash, id_hash, id_hash_merkle_path, address_merkle_path, signature);
}

