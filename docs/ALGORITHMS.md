# Algorithms & Mathematical Formulations
## AI-Based Campus Incident Intelligence & Response System

This document outlines the algorithms, mathematical models, and operational pipelines powering the Campus Incident Intelligence platform. Written in accessible academic language suitable for Computer Science and Engineering students and examiners.

---

## 1. Hybrid Incident Classification Pipeline

The incident classification pipeline translates natural language reports into structured campus facility disciplines (e.g., *Water & Plumbing*, *Electrical Hazards*, *Internet & Networking*, *Infrastructure & Building Damage*).

### A. Term Frequency - Inverse Document Frequency (TF-IDF)
To extract numerical feature representations from incident text descriptions, the system uses TF-IDF vectorization:

$$\text{TF}(t, d) = \frac{f_{t,d}}{\sum_{t' \in d} f_{t',d}}$$

Where $f_{t,d}$ is the raw count of term $t$ in incident document $d$.

$$\text{IDF}(t, D) = \ln\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$

Where $|D|$ is the total number of documents in the corpus, and the denominator represents the document frequency of term $t$.

The composite feature weight is:
$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$

We extract both unigrams and bigrams ($n \in [1, 2]$) to capture compound phrases such as *"water leak"*, *"exposed wire"*, *"circuit breaker"*, and *"wi-fi down"*.

### B. Multinomial Naive Bayes (MNB)
Given feature vector $\mathbf{x} = (x_1, x_2, \dots, x_m)$, the classifier calculates the posterior probability for each campus category $C_k$:

$$P(C_k \mid \mathbf{x}) \propto P(C_k) \prod_{i=1}^m P(x_i \mid C_k)^{x_i}$$

With Laplace smoothing ($\alpha = 0.1$):
$$\hat{P}(x_i \mid C_k) = \frac{N_{ki} + \alpha}{N_k + \alpha \cdot m}$$

Where $N_{ki}$ is the aggregate count of feature $i$ in category $C_k$, and $N_k$ is the total token count in category $C_k$.

### C. Hybrid Decision Arbitration
Because short student incident reports may contain sparse text, a supervised statistical classifier is paired with domain keyword verification. When strong keyword signals and statistical predictions align, confidence is boosted ($C \ge 0.90$). If the statistical classifier exhibits low posterior margin ($P < 0.45$), the report is routed to *"Other / Needs Review"*, ensuring valid student submissions are never rejected due to model uncertainty.

---

## 2. Automatic Severity & Priority Detection Engine

Rather than relying on opaque heuristics, priority scoring uses a transparent, auditable mathematical formula that returns a score $S \in [10, 100]$ and categorizes incidents into four operational tiers: **Critical**, **High**, **Medium**, or **Low**.

### Formula:
$$S = \text{clamp}\left( S_{\text{base}}(C) + \Delta_{\text{compound}} + \Delta_{\text{hazard}} + \Delta_{\text{loc}} + \Delta_{\text{recurrence}}, 10, 100 \right)$$

1. **Category Base Score ($S_{\text{base}}$)**:
   - Electrical Hazards: $75$ pts
   - Security & Safety: $70$ pts
   - Water & Plumbing: $55$ pts
   - Infrastructure Damage: $50$ pts
   - Lab Equipment: $40$ pts
   - Internet & Networking: $35$ pts
   - Cleanliness & Sanitation: $30$ pts
   - Transport & Parking: $25$ pts

2. **Compound Hazard Escalator ($\Delta_{\text{compound}}$)**:
   If water/flooding co-occurs near electrical equipment, transformers, or computer labs:
   $$\Delta_{\text{compound}} = +35\text{ pts}$$

3. **Immediate Hazard Signals ($\Delta_{\text{hazard}}$)**:
   High-risk tokens (e.g., *"exposed wire"*, *"burning smell"*, *"sparking"*, *"structural collapse"*):
   $$\Delta_{\text{hazard}} = \min(30, k \times 18)\text{ pts}$$

4. **Facility Sensitivity Weight ($\Delta_{\text{loc}}$)**:
   High-density academic environments (laboratories, student hostels, library, examination halls):
   $$\Delta_{\text{loc}} = +10\text{ pts}$$

5. **Recurrence Multiplier ($\Delta_{\text{recurrence}}$)**:
   If similar reports describe the same unresolved issue:
   $$\Delta_{\text{recurrence}} = +8\text{ to } +15\text{ pts}$$

### Severity Tier Thresholds:
- **Critical**: $S \ge 80$ (Immediate emergency dispatch)
- **High**: $60 \le S < 80$ (Action within 2 hours)
- **Medium**: $40 \le S < 60$ (Routine maintenance shift)
- **Low**: $S < 40$ (Scheduled upkeep)

---

## 3. Duplicate Incident Detection (Semantic Cosine Similarity)

To prevent duplicate work orders and detect multiple students reporting the same disruption, cosine similarity is computed across TF-IDF normalized vectors:

$$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \frac{\sum_{i=1}^n u_i v_i}{\sqrt{\sum_{i=1}^n u_i^2} \sqrt{\sum_{i=1}^n v_i^2}}$$

### Contextual Matching Bonuses:
$$\text{Sim}_{\text{final}} = \min\left(1.0, \text{Sim}_{\text{cosine}} + \delta_{\text{building}} + \delta_{\text{category}}\right)$$

- Same Building Match: $\delta_{\text{building}} = +0.12$
- Same Incident Category: $\delta_{\text{category}} = +0.08$

### Classification Thresholds:
- $\text{Sim}_{\text{final}} \ge 0.72$: **High-confidence duplicate** (Flagged for administrative one-click merge).
- $0.40 \le \text{Sim}_{\text{final}} < 0.72$: **Recurring related issue** (Linked as corroborating evidence).
- $\text{Sim}_{\text{final}} < 0.40$: **Distinct incident** (Preserved as independent ticket).

---

## 4. Unsupervised Pattern Discovery via DBSCAN

To discover hidden patterns across hundreds of incident reports, the platform employs **Density-Based Spatial Clustering of Applications with Noise (DBSCAN)**.

### Mathematical Formulation:
Given precomputed semantic distance matrix $D_{ij} = 1 - \text{CosineSimilarity}(\mathbf{d}_i, \mathbf{d}_j)$:

1. **$\varepsilon$-Neighborhood**:
   $$N_\varepsilon(p) = \{q \in D \mid \text{dist}(p, q) \le \varepsilon\}$$
   Where $\varepsilon = 0.45$ (corresponding to semantic similarity $\ge 0.55$).

2. **Core Points**:
   $p$ is a core point if $|N_\varepsilon(p)| \ge \text{MinPts}$ (configured to $\text{MinPts} = 3$).

3. **Direct Density-Reachability**:
   A point $q$ is directly density-reachable from $p$ if $q \in N_\varepsilon(p)$ and $p$ is a core point.

4. **Density-Connected Clusters**:
   All points density-connected to core points form a recurring incident cluster, while isolated reports with no nearby neighbors are treated as noise ($label = -1$).

This allows the platform to discover that 7 student reports in different words (e.g. *"slow internet"*, *"portal timeout"*, *"wifi dropped in 204"*) describe the same underlying switch malfunction.
