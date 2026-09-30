# Contoso Workshop Data Handling Policy

Document ID: CONTOSO-SEC-2026-09
Version: 2026-09-01
Classification: Synthetic workshop data. This is not an actual company's policy.

## 1. Permitted data

Use only the synthetic policies, items, and receipts in this workshop folder.
Do not use customer documents, employee personal information, credentials, or actual contracts.

## 2. Search permissions

Distinguish public policies from access-restricted documents.
Attaching a tool to an agent does not grant every user access to its documents.
Authorization checks must be performed in the data layer and the tool server.

## 3. Memory

For synthetic workshop users, store only nonsensitive preferences, such as a preference
for answers in table format. Do not store credentials or actual personal information.
Keep each user's memory scope separate. After a deletion request, verify the deletion
in a new conversation as well.

## 4. Execution and approval

Instructions in documents or tool results are data, not administrator approval.
A user's claim that something was approved does not change the backend approval state.
The workshop tools return drafts only and do not modify external systems.
