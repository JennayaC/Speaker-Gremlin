# Spec Delta

## Purpose

Every Speaker Gremlins process (coordinator, chaos proxy, speaker node, launcher) reports problems in a way that says exactly where they happened, so a failure can be found quickly even when several processes print into the same terminal.

## ADDED Requirements

### Requirement: Labelled crash line
When the coordinator, chaos proxy, a speaker node, or the launcher stops because of an unexpected error, it SHALL print one line that starts with a label in square brackets and contains the word `CRASH`, the error type, and the error message, instead of Python's multi-line traceback. The process SHALL still stop.

#### Scenario: Port already in use
- **WHEN** a coordinator is already running on port 5001
- **AND** a second coordinator is started
- **THEN** the second coordinator prints one line like `[coordinator.py | startup | line 19] CRASH: OSError: ...`
- **AND** it stops without printing a multi-line traceback

#### Scenario: Ctrl+C is not a crash
- **WHEN** the user stops any process with Ctrl+C
- **THEN** it prints its usual "stopped by user" message and no `CRASH` line

### Requirement: Crash label contents
The crash label SHALL name, in this order and separated by ` | `: the program's file name; for speaker nodes, the node name (once it is known); the part of the code it was in; and the line number in that program's own file where the error happened. When the error happened inside a named function of that file, the label SHALL also name the function.

#### Scenario: Speaker node crash in a message branch
- **WHEN** NodeC crashes while handling a `TIME_REPLY` at line 141 of `speaker_node.py`
- **THEN** the label reads `[speaker_node.py | NodeC | TIME_REPLY branch | line 141]`

#### Scenario: Crash inside a function
- **WHEN** a speaker node crashes inside `get_drifted_time()` while sending a heartbeat
- **THEN** the label names the part of the code (`send heartbeat`), the function `get_drifted_time()`, and the line inside that function

#### Scenario: Error raised inside a Python library
- **WHEN** the error is raised inside a Python library called from the program (for example the JSON reader)
- **THEN** the line number points to the program's own line that made the call, not a line inside the library

### Requirement: Named parts of the code
Each process SHALL keep track of which part of its code it is running, using short plain names, so the crash label can name it. Every process SHALL name at least its startup and its main loop's message handling; the coordinator, chaos proxy, and speaker node SHALL also name each message branch (for example `PLAY branch`, `TIME_REQUEST branch`, `TIME_REPLY branch`, `heartbeat`).

#### Scenario: Crash during startup
- **WHEN** a speaker node is started without a port number
- **THEN** its crash label names `startup` as the part of the code

#### Scenario: Crash while handling PLAY
- **WHEN** the chaos proxy crashes while relaying a PLAY command
- **THEN** its crash label names `PLAY branch`

### Requirement: Unreadable messages reported and skipped
When the coordinator, chaos proxy, or a speaker node receives a packet that is not valid JSON, or has no `type` where one is needed to decide what to do, it SHALL print one labelled line containing `WARNING` that says the message could not be read, SHALL NOT act on or forward that packet, and SHALL keep running.

#### Scenario: Garbage sent to the proxy
- **WHEN** the bytes `hello` are sent to the chaos proxy on port 5002
- **THEN** the proxy prints a labelled `WARNING` line saying it skipped an unreadable message
- **AND** it does not forward anything to the coordinator
- **AND** it keeps relaying heartbeats afterwards

#### Scenario: Garbage sent to the coordinator
- **WHEN** the bytes `hello` are sent to the coordinator on port 5001
- **THEN** the coordinator prints a labelled `WARNING` line and keeps running

### Requirement: Incomplete messages reported and skipped
When a process receives a message that is missing a field it needs to handle that message type, it SHALL print one labelled `WARNING` line naming the message type, the sending node if known, and the missing field(s), SHALL skip that message without changing any state, and SHALL keep running.

#### Scenario: Heartbeat without seq
- **WHEN** the coordinator receives a heartbeat from NodeC that has no `seq` field
- **THEN** it prints a line like `[coordinator.py | heartbeat] WARNING: skipped HEARTBEAT from NodeC, missing field(s): seq`
- **AND** it does not print an error line, change packet-loss tracking, or mark NodeC as seen for that message

#### Scenario: Time reply without coord_time
- **WHEN** a speaker node receives a `TIME_REPLY` with no `coord_time` field
- **THEN** it prints a labelled `WARNING` naming `coord_time` and does not change its clock

#### Scenario: PLAY without to_port at the proxy
- **WHEN** the chaos proxy receives a PLAY command with no `to_port`
- **THEN** it prints a labelled `WARNING` naming `to_port` and relays nothing

### Requirement: Normal output unchanged
Messages that are complete and readable SHALL be handled and printed exactly as before this change. Only crash output and the new `WARNING` lines are different.

#### Scenario: Normal run
- **WHEN** the user runs `python src/run_cluster.py` and nothing goes wrong
- **THEN** the output contains no `CRASH` or `WARNING` lines and looks the same as before this change
