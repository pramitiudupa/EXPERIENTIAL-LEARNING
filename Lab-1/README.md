# Lab-1 — Requirements Engineering & UML Use-Case Modelling

**Course:** Software Engineering · PES University, Dept. of CSE
**Problem Statement #27:** Warehouse Inventory & Pallet Location Tracker
**Name:** Pramiti Ragavendra Udupa  **SRN:** PES1UG24CS331

An automated warehouse management system that tracks 3D shelf pallet positions,
enforces shelf maximum weight limits, and logs stock movements captured through
barcode/RFID scanning.

## Contents

| File | Deliverable |
|---|---|
| `Requirements_Table.docx` | Requirements table — 5 FRs and 2 NFRs with ID, Type, Description, Priority, Acceptance Criteria and Rationale |
| `UseCase_Diagram.pdf` | UML use-case diagram (exported) |
| `UseCase_Diagram.drawio` | Editable draw.io source for the diagram |
| `UseCase_Flow.pdf` | Use-case flow specification for UC-02 (exported) |
| `UseCase_Flow.docx` | Editable Word source for the flow |

## Actors

| Actor | Type |
|---|---|
| Warehouse Operator | Primary (human) |
| Logistics Supervisor | Primary (human) |
| Barcode / RFID Scanner | Secondary (device) |

## Use cases

| ID | Use case | Traces to |
|---|---|---|
| UC-01 | Register inbound pallet | FR-002 |
| UC-02 | Store pallet in bin | FR-003 |
| UC-03 | Validate rack load capacity | FR-001 |
| UC-04 | Suggest alternative bin | FR-001 (failure path) |
| UC-05 | Dispatch pallet | FR-004 |
| UC-06 | Log stock movement | FR-004 |
| UC-07 | Search pallet by SKU | FR-005, constrained by NFR-001 |
| UC-08 | Manage movement log records | NFR-002 |

## Relationships modelled

- UC-02 «include» UC-03 — a put-away always validates the rack load first
- UC-02 «include» UC-06 — a completed put-away always writes a log entry
- UC-05 «include» UC-06 — a dispatch always writes a log entry
- UC-04 «extend» UC-02 — an alternative bin is offered only when validation rejects the placement

## Use-case flow

`UseCase_Flow.pdf` specifies **UC-02 Store pallet in bin**, covering preconditions,
postconditions, the main success scenario, and two alternate flows
(7a — rack capacity exceeded; 3a — pallet tag unreadable).
