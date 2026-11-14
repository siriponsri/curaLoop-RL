# Reusing the ENV-STABLE-LR installed artifact

The authoritative mapping is [profile-adapter-contract-v1.json](../evidence/env-stable-lr-20261114-v1/profile-adapter-contract-v1.json).
Read the [final owner report](ENV_STABLE_LR_FINAL_OWNER_REPORT_20261114.md) before use.

The local ignored account `.local/env-stable-lr-20261114-v1/remote-return-v1/`
contains the full compressed archive and content/metadata manifest. Check both
hashes against `owned-return-verification-v1.json`. Inside the archive, `env/`
contains the installed profiles and `systemlibs-v2/` their prepared native-library
overlay. The independently copied `reconstructed/` artifact passed all 13
workloads under two fresh worker/cache sets on the pinned shared base image.
The full lock and resolved package-version manifest are in
`leases/offline-reconstruct-v1/`.

Do not run the closed account's controller as a fresh research release. A future
authorized release must use a new owned root and accounting, retain protected
roles, verify the content lock, use the mapping's profile/addon precedence and
prepare library/cache directories before the fresh worker starts. Mount package
and scientific inputs read-only, keep grader gold separate from actors/reference
workers, and apply resource/conflict checks before any job. Reuse successful
development evidence; do not reinstall/search packages merely to start over.

The transfer archive stores identical bytes once and may refer to an earlier
member. A restoring program must validate member paths and manifest hashes,
copy alias bytes independently when metadata differs, and not follow arbitrary
symlinks. Blind extraction is not a demonstrated restoration procedure. Local
stream verification is complete; full restoration from that transfer archive on
a second host and fresh online dependency resolution were NOT_RUN. The retained
shared base image was not deleted; cross-host image provisioning was NOT_RUN.

These artifacts establish engineering behavior in the tested image. Only four
development references ran once. They do not establish thirty-task native
admission, agent reliability, scientific effect, independent expert validation,
user benefit, or manuscript readiness.
