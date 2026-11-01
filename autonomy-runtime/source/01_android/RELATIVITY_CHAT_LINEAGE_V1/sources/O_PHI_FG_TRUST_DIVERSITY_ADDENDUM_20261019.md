# O-PHI-FG Trust Diversity Addendum — 2026-10-19

Status: PROPOSED; research-only extension.

## New abstraction from Trusting-Trust / bootstrappable-build work
Define two environment sets:
R = REQUIRED_SAMENESS: the minimal facts that must match to reproduce an artifact (source, dependency/toolchain identities, declared epoch, required build parameters).
D = WITNESSED_DIVERSITY: facts allowed or encouraged to differ across independent witnesses (node, architecture where applicable, OS/base image, CPU model/features, firmware, physical host, builder implementation).

Desired direction:
MINIMIZE(R) while MAXIMIZE(D) subject to verified artifact/equivalence acceptance.

This changes O-PHI-FG from 'two hashes match' into 'the same claim survives independent worlds.'

## Compiler provenance extension
COMPILER_TRUST := compiler_source_sha256 + compiler_binary_sha256 + bootstrap_chain_sha256 + stage_comparison_receipts + builder_diversity

Optional DDC/bootstrappable tribunal:
trusted_or_bootstrapped_A -> build compiler_B1 -> compiler_B1 builds B2
compiler_B builds B_ref
COMPARE(B2, B_ref)

A passing byte comparison strengthens the claim that compiler source corresponds to the compiler binary, under the assumptions of the independent path.

## Witness syntax extension
REPRODUCTION_CONTRACT := {required_sameness[], permitted_variance[], forbidden_variance[]}
DIVERSITY_RECEIPT := {node, architecture, os, base_image, cpu, firmware_if_known, builder_implementation}

CONFIDENCE is not a probability in v1. It is an evidence vector:
{byte_identity, equivalence_level, required_sameness_count, witnessed_diversity_count, independent_witness_count, provenance_verified, execution_verified, compiler_chain_verified}

## Next-form design rule
A receipt must say BOTH:
1. what had to be the same; and
2. what was actually different.

Without (1), reproduction cannot be reconstructed.
Without (2), independent replication strength cannot be evaluated.
