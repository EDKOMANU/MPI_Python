# Multidimensional Poverty Index (MPI) Analyzer

A Python toolkit for calculating and analyzing the Multidimensional Poverty Index (MPI) using customizable weights and domains.

![read from the oxpohord poverty and human development initative of the oxford university](ophi.org.uk) 


## Features

- **MPI Calculation**: Compute MPI scores (H, A, and MPI) from deprivation data
- **Flexible Weighting**: Specify weights at domain or indicator level
- **Analysis Tools**:
  - Deprivation proportions across indicators
  - Indicator contributions to MPI
  - Poverty classification for individuals/households
- **CSV Output**: Save results with deprivation scores and poverty status

## Usage

### Basic Execution
```bash
python mpi_analyzer.py \
    --data poverty_data.csv \
    --dimensions '{"Health": ["Nutrition", ...], "Education": [...]}' \
    --output results
```

### Example Dataset Structure
| Nutrition | Child_Mortality | Years_Schooling | ... | 
|-----------|-----------------|-----------------|-----|
| 1         | 0               | 1               | ... |
| 0         | 0               | 0               | ... |

### Sample Outputs
1. **Scored Data** (`results_scored.csv`):
   ```csv
   Nutrition,Child_Mortality,...,Deprivation_Score,Is_Poor
   1,0,...,0.45,True
   0,0,...,0.15,False
   ```

2. **Analysis Files**:
   - `deprivation_analysis.csv`: Indicator-level deprivation rates
   - `contribution_analysis.csv`: MPI contribution breakdown

## Customization

### Weight Specification
```python
# Domain weights example
python mpi_analyzer.py ... --domain_weights '{"Health": 0.4, "Education": 0.4}'

# Direct indicator weights
python mpi_analyzer.py ... --indicator_weights '{"Nutrition": 0.2, ...}'
```

### Advanced Options
- `--threshold`: Change poverty threshold (default=0.33)
- `--validate_weights`: Strict weight validation (default=True)

## Output Interpretation

| Metric                | Description                                  |
|-----------------------|----------------------------------------------|
| **H** (Headcount)     | Proportion of population in poverty          |
| **A** (Intensity)     | Average deprivation intensity among the poor |
| **MPI**               | H × A (Overall poverty measure)             |
| **Contribution_Pct**  | % of MPI attributable to each indicator      |



# Weight Application Scenarios

### 1. Domain Weights Only
**Concept**: Specify weights for domains, automatically divided equally among their indicators.

```python
# Dimensions structure
dimensions = {
    "Health": ["Nutrition", "Child_Mortality"],
    "Education": ["Years_Schooling", "School_Attendance"],
    "Living_Standards": ["Cooking_Fuel", "Sanitation", "Water", 
                        "Electricity", "Housing", "Assets"]
}

# Domain weights (sum must = 1)
domain_weights = {
    "Health": 0.4,          # Each health indicator gets 0.4/2 = 0.2
    "Education": 0.4,       # Each education indicator gets 0.4/2 = 0.2
    "Living_Standards": 0.2 # Each LS indicator gets 0.2/6 ≈ 0.033
}

# Command-line execution
calculate_mpi( 
    data = "data.csv",
    dimensions = dimensions,
    domain_weights = domain_weights)
```

### 2. Direct Indicator Weights
**Concept**: Explicitly set weights for individual indicators.

```python
indicator_weights = {
    # Health (total = 0.3)
    "Nutrition": 0.15,
    "Child_Mortality": 0.15,
    
    # Education (total = 0.3)
    "Years_Schooling": 0.2,
    "School_Attendance": 0.1,
    
    # Living Standards (total = 0.4)
    "Cooking_Fuel": 0.1,
    "Sanitation": 0.1,
    "Water": 0.05,
    "Electricity": 0.05,
    "Housing": 0.05,
    "Assets": 0.05
}

# Command-line execution
calculate_mpi( 
    data =  "data.csv",
    dimensions,
    indicator_weights)
```

### 3. Equal Weights (Default)
**Concept**: Equal weights for all indicators when no weights are specified.

```python
# 10 indicators total → each gets 0.1 weight
# Domains receive weights based on indicator count:
# Health: 2 indicators → 0.2 total
# Education: 2 → 0.2
# Living Standards: 6 → 0.6

# Command-line execution (no weight arguments)
calculate_mpi( 
    data =  "data.csv",
    dimensions)
```

## Validation Rules
- **Domain Weights Mode**:
  ```python
  sum(domain_weights.values()) == 1
  ```
- **Indicator Weights Mode**:
  ```python
  sum(indicator_weights.values()) == 1
  all(ind in dimensions for ind in indicator_weights)
  ```
- **Equal Weights Mode**:
  ```python
  Automatically enforced when no weights provided
  ```
```
## License
MIT License - See [LICENSE](LICENSE)

---

**References**:
- Methodology based on [OPHI MPI Standards](https://ophi.org.uk/multidimensional-poverty-index/)
- Dataset format adapted from World Bank poverty surveys

*This is an unofficial tool - Always validate results against official methodologies*
```
