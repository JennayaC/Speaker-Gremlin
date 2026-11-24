# Spec Delta

## ADDED Requirements

### Requirement: SYNC setup
When started with `--experiment SYNC`, the launcher SHALL start the coordinator, a plain chaos proxy, and the three speaker nodes with sync on and larger drift: NodeA 0, NodeB +5000, NodeC −10000 PPM.

#### Scenario: Run SYNC
- **WHEN** the user runs `python src/run_cluster.py --experiment SYNC`
- **THEN** the coordinator and a chaos proxy with no extra switches start
- **AND** NodeA, NodeB, NodeC start with drift 0, 5000, −10000 and `--sync`

### Requirement: SYNC-DELAY setup
When started with `--experiment SYNC-DELAY`, the launcher SHALL start the same processes as SYNC, except that the chaos proxy is started with `--sync-delay 0.5`.

#### Scenario: Run SYNC-DELAY
- **WHEN** the user runs `python src/run_cluster.py --experiment SYNC-DELAY`
- **THEN** the coordinator and the three nodes start as in SYNC
- **AND** the chaos proxy starts with `--sync-delay 0.5`

### Requirement: Other setups keep normal nodes
The normal run and Experiments A, B, and C SHALL start the nodes with drift 0, 50, −100 and without `--sync`, as before this change.

#### Scenario: Experiment A nodes unchanged
- **WHEN** the user runs `python src/run_cluster.py --experiment A`
- **THEN** NodeA, NodeB, NodeC start with drift 0, 50, −100 and no `--sync`

## MODIFIED Requirements

### Requirement: Unknown experiment name rejected
When given an `--experiment` name it does not know, the launcher SHALL print an error that lists the valid names and SHALL start no processes.

#### Scenario: Typo in name
- **WHEN** the user runs `python src/run_cluster.py --experiment Z`
- **THEN** an error is printed naming the valid choices (A, B, C, SYNC, SYNC-DELAY)
- **AND** no coordinator, proxy, or node process is started
