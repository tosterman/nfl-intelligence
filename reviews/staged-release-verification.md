# Native release contents check

The native publisher previously validated working data and then staged an
explicit list of generated files. An omitted artifact could leave an older
version in the Git release despite a successful local verification. This was
observed and fixed for weather history; the new guard checks the general case.

Before committing or pushing, `verify_staged_release` compares all direct-release
paths with Git's staged contents. It rejects untracked/missing artifacts,
unresolved index entries, non-file entries, out-of-workspace paths and changed
contents. It hashes each working file with repository filters instead of trusting
Git's cached stat information or assume-unchanged flags. Indexed source, public
asset and root-config files absent from the working release also fail.

Five tests exercise actual temporary Git repositories, including Windows/Linux
line endings, omitted new data, assume-unchanged edits, missing paths and default
enumeration of source/config deletions. Independent review identified the deletion
gap in the first implementation; it is fixed with a default-enumeration regression.
Fifteen orchestration tests, one release-packaging test and ten release-binding
tests passed. The new orchestration failure case confirms no commit, push or
public capture occurs after rejection.

A read-only check of the actual workspace confirmed 132 release files matched
the index before the deletion follow-up; the subsequent full check is recorded
in this task's tool evidence. No public deployment or main-branch mutation occurred.
This checks release contents at verification time; it is not an atomic filesystem
snapshot and does not establish successful public publication or scheduler health.
