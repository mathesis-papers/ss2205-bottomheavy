# Coefficient injections and equality for Sagan–Swanson bottom heaviness

This package gives an alternative interval-layer proof of the four-family
bottom-heaviness theorem of Shi-Mei Ma and Principia Math in Progress, answering
Sagan and Swanson's Conjecture 7.6, arXiv:2205.14078v1, Section 7.5, p. 40.
The bibliography identifies the prior proofs and the original journal article.
The note also proves an exact reflection-defect identity, classifies the
symmetric entries of all four families, and constructs rank injections on
their labeled product-of-chains encodings. Complex-group and ordered-family
consequences follow from nonnegative product expansions.
Ma's Lemmas 2--4 and Proposition 1 already imply the closure, upper-half
monotonicity, symmetric-function and displayed complex-group consequences.
The interval-layer treatment supplies explicit rank injections, the
reflection-defect identity and its equality criteria, and the classification
of symmetric entries. These conclusions have full written proofs in the note.

For the alternating sum in Conjecture 7.9 it establishes

```
sum_{k=0}^n (-1)^(n-k) q^(2(n-k)) [k]_q! S[n,k] - 1
  = (1-q)(1+q)^n - 1 + q^(n+1).
```

The coefficient at exponent j, for 1 <= j <= n, is
`binom(n,j)-binom(n,j-1)`; the signs pair under j -> n+1-j.
After the initial q is factored out, the absolute-coefficient polynomial
is palindromic for n >= 2.
This normalization is necessary: at n = 2 the sum is q-q^2,
whose absolute-coefficient polynomial q+q^2 is not palindromic
at its actual degree two. The sign assertions hold and the
support-normalized symmetry is exact.

## Contents

- `note.tex`: self-contained mathematical text and bibliography.
- `note.pdf`: readable typeset text.
- `metadata.json`: title, creators, license, and scientific coverage.
- `verify.py`: exact-integer finite checks, requiring Python 3.8 or later and no packages.
- `checker-output.json`: expected output of the checker.

## Build

Use Tectonic 0.17.0:

```sh
tectonic --untrusted note.tex
```

Alternatively, use a standard LaTeX distribution:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is included in `note.tex`; BibTeX is unnecessary.

## Exact finite checks

```sh
python3 -I -S verify.py > actual.json
python3 -I -S -c 'import json; assert json.load(open("actual.json")) == json.load(open("checker-output.json"))'
```

The checks reconstruct the four recurrences for `0 <= n <= 50` and
`-3 <= k <= 53`, compare elementary/complete homogeneous expansions through
`n = 8`, and test products, unequal-degree mixtures, and interval layers.
They include zero and constant polynomials and the two nonunimodal type-B examples.
Additional assertions check the symmetric-entry classification through n = 50,
the exact reflection-defect formula on the mixture range, symmetric-chain
injections for up to four factors of lengths 1 through 4, complex-group
recurrences for 2 <= m <= 5 and n <= 10 (including ordered products),
and the alternating-sum identity for 0 <= n <= 30.
The universal statements follow from the written proofs, not these finite ranges.

## Mathematical coverage

The declaration
`D5.S3.Combinatorics.QStirling.SaganSwansonBottomHeavy.result`
in the following version-specific source proves bottom heaviness of exactly the
four unshifted recurrence families over natural coefficients, for all natural
`n` and integer `k`, with the zero-polynomial natural-degree convention:

https://github.com/the-omega-institute/trureturing/blob/13f4288c2940bd2aa4020cec789956b9265769f5/D5/S3/Combinatorics/QStirling/SaganSwansonBottomHeavy.lean

The real-weight closure theorem, upper-half monotonicity, injections, equality
formulas, ordered-family and complex-group corollaries, symmetric-function
consequence, and alternating-sum identity have written proofs in the note.
Positivity throughout the support follows for every nonzero unshifted entry.
Coefficient and parity log-concavity and asymptotic normality have no claimed
coverage in this package. Previously established type-A superspace results
are cited rather than derived from bottom heaviness.

Creators: Haobo Ma (ChronoAI Pte Ltd, Singapore), followed by Wenlin Zhang
(National University of Singapore; ChronoAI Pte Ltd, Singapore).

License: Creative Commons Attribution 4.0 International (CC BY 4.0).
