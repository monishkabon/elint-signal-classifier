# ELINT Signal Classifier

A radar pulse deinterleaving and classification pipeline for Electronic Intelligence (ELINT) applications. The system ingests a time-sorted stream of interleaved radar pulses from multiple emitters, separates them into individual emitter tracks, and classifies each track against a known threat library.

## Overview

Modern electronic support measures (ESM) receivers intercept radar pulses from every emitter in the environment simultaneously. The resulting pulse stream is a chronologically merged sequence with no inherent labeling, making it difficult to determine which pulses belong to which emitter. This project addresses that problem through a three-stage pipeline:

1. **PRI Detection** — Identify candidate Pulse Repetition Intervals from the interleaved stream using multi-level Sequential Difference Interval Function (SDIF) histogramming.
2. **Track Extraction** — Chain individual pulses into coherent emitter tracks by matching Time of Arrival (ToA) sequences against detected PRIs within a configurable tolerance.
3. **Threat Classification** — Compute mean parametric vectors (PRI, RF, PW) for each extracted track and match them to a threat library using weighted Euclidean distance.

## Architecture

```
interleaved_signals_40k.csv
        |
        v
  +--------------+
  | Deinterleaver|  SDIF Levels 1-3, histogram thresholding
  +--------------+
        |
        v
  +--------------+
  |   Pipeline   |  ToA chaining with binary search, per-PRI extraction
  +--------------+
        |
        v
  +--------------+
  |  Classifier  |  Weighted Euclidean distance against threat library
  +--------------+
        |
        v
  Classification Result per Track
```

## Components

### Signal Generator (`src/genarator.py`)

Produces synthetic radar pulse data for development and validation. Models four emitter classes with configurable parameters:

| Emitter Type       | PRI (us) | RF (GHz) | PW (us) | Behavior |
|--------------------|----------|----------|---------|----------|
| Civilian Navigation| 1000     | 9.4      | 0.8     | Stable   |
| Early Warning      | 3000     | 3.2      | 2.5     | Stable   |
| Target Tracker     | 250      | 12.5     | 0.2     | Stable   |
| Frequency Hopper   | 850      | 9.5      | 0.5     | Hopping  |

Each pulse is generated with Gaussian jitter on ToA, RF, and PW to approximate real-world measurement noise. The frequency hopper additionally randomizes its RF within a ±0.5 GHz band around the nominal center frequency. All pulses are merged chronologically and written to a single CSV file.

### Deinterleaver (`src/deinterleaver.py`)

Implements a multi-level SDIF approach to extract candidate PRIs from the interleaved pulse stream:

- **Level 1**: First-order differences between consecutive ToAs.
- **Level 2**: Second-order differences (skip one pulse).
- **Level 3**: Third-order differences (skip two pulses).

The three difference arrays are concatenated into a master histogram. Bins exceeding a configurable occurrence threshold are extracted as candidate PRIs, then filtered to remove duplicates within a 10 us clustering window.

### Track Extraction Pipeline (`src/main.py`)

For each candidate PRI, the pipeline scans unallocated pulses and attempts to build a chain by stepping forward in time at the expected interval. Binary search (`np.searchsorted`) narrows the search window, and a linear scan within a small neighborhood checks for matches within tolerance. A chain of 50 or more pulses qualifies as an extracted track and its constituent pulses are marked as allocated, preventing reassignment in subsequent passes.

### Threat Classifier (`src/wvdClassifier.py`)

Each extracted track is reduced to a mean parametric vector (PRI, RF, PW) and compared against every entry in a predefined threat library. The comparison uses weighted Euclidean distance with the following weight scheme:

- **PRI weight**: 1.0
- **RF weight**: 100.0 (doubled if RF spread exceeds 0.4 GHz, indicating frequency agility)
- **PW weight**: 1000.0

The library entry with the shortest distance is returned as the classification result.

## Data Format

The input CSV file must contain the following columns:

| Column     | Description                                |
|------------|--------------------------------------------|
| `ToA`      | Time of Arrival in microseconds            |
| `RF`       | Radio Frequency in GHz                     |
| `PW`       | Pulse Width in microseconds                |
| `True_Label` | Ground truth label (used for validation) |

Rows must be sorted by `ToA` in ascending order.

## Dependencies

- Python 3
- NumPy
- pandas
- Matplotlib

## License

This project is licensed under the GNU Affero General Public License v3.0. See `LICENSE` for the full text.
