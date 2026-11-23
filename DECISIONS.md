## Decision: compare B's value with A's total_value
- Rejected: compare B against base_value or base plus adjustment in the frontend.
- Why: A's total_value is the authoritative calculated amount and matching data confirms B reports it.

## Decision: blank and unparsable values remain null
- Rejected: convert blank or junk values to zero.
- Why: zero can falsely agree with a zero total and hides the original dirty input; raw text is preserved.

## Decision: split entries sum to the A total without an error
- Rejected: flag every record with more than one B entry as a duplicate.
- Why: multiple entries are legitimate when their Decimal sum equals A's total.

## Decision: equal duplicate amounts are a duplicate disagreement
- Rejected: treating every repeated amount as a part split.
- Why: repeated entries are only allowed when their sum equals the A total.

## Decision: date and location mismatches are separate disagreements
- Rejected: only compare values.
- Why: they reveal two of the extra mismatch types explicitly in the brief and are cheap to test.

## Decision: expose matched rows under A's tenant side
- Rejected: show the B-side location for a cross-org row or merge both org filters.
- Why: for a matched record, the visible location and tenant ownership come from A's location through locations.csv; B location details stay outside the payload.

## Decision: treat voided A records normally
- Rejected: exclude every voided record from comparison.
- Why: the same mismatch rules are still useful for auditing; a voided record with matching B data produces no disagreement.
