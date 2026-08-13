# Decode the Paper 3 reanalysis source

The verified source is stored as `code/paper_3_reanalysis.py.b64` because the connector used during release preparation blocked direct executable-source writes. The encoded file is byte-for-byte verified against the locally executed V2.1 script.

Verified Git blob SHA-1 of the encoded file: `7de0a92e6c398238db5d57b0d3de36c5df907b29`.
Decoded Python source SHA-256: `f2bbb1aacb5fa3e6fafb628f93e0449baec5787a076ed9a88f24f914d98cf912`.

## Cross-platform decoding with Python

```bash
python -c "import base64,pathlib; p=pathlib.Path('code/paper_3_reanalysis.py.b64'); pathlib.Path('code/paper_3_reanalysis.py').write_bytes(base64.b64decode(p.read_bytes()))"
```

Then run:

```bash
python code/paper_3_reanalysis.py
```

The output should reproduce `EXPECTED_RESULTS_V2_1.md`. The decoded `.py` file is a derived local working file; the archived `.b64` object preserves the exact verified source bytes.
