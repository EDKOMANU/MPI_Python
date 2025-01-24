import pandas as pd
import numpy as np
import os

def calculate_mpi(
    data_path,
    dimensions,
    domain_weights=None,
    indicator_weights=None,
    poverty_threshold=1/3,
    output_path=None
):
    """
    Computes MPI with flexible weight inputs and automatic equal weighting fallback.
    
    Args:
        data_path (str): Path to CSV file with deprivation indicators (1 = deprived, 0 = not deprived)
        dimensions (dict): Dictionary mapping domains to their indicators
        domain_weights (dict): Weights for domains (must sum to 1)
        indicator_weights (dict): Direct weights for indicators (must align with domain_weights if both provided)
        poverty_threshold (float): Poverty classification threshold
        output_path (str): Path to save results
        
    Returns:
        df (pd.DataFrame): Data with deprivation scores
        H (float): Headcount ratio
        A (float): Intensity of deprivation
        MPI (float): MPI value
    """
    # Load data and validate columns
    df = pd.read_csv(data_path)
    all_indicators = [ind for d in dimensions.values() for ind in d]
    missing = set(all_indicators) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # ========== Weight Validation Logic ==========
    # Case 1: Both weight types provided
    if domain_weights and indicator_weights:
        for domain, indicators in dimensions.items():
            domain_total = domain_weights.get(domain, 0)
            indicator_total = sum(indicator_weights.get(ind, 0) for ind in indicators)
            
            if not np.isclose(domain_total, indicator_total, atol=0.001):
                raise ValueError(f"Domain '{domain}' weight mismatch: {domain_total} vs {indicator_total}")

    # Case 2: Only domain weights provided        
    elif domain_weights:
        indicator_weights = {}
        for domain, indicators in dimensions.items():
            weight = domain_weights.get(domain, 0)
            if len(indicators) == 0:
                raise ValueError(f"Domain '{domain}' has no indicators to apply weights to")
            per_indicator = weight / len(indicators)
            for ind in indicators:
                indicator_weights[ind] = per_indicator

    # Case 3: Only indicator weights provided
    elif indicator_weights:
        domain_weights = {}
        for domain, indicators in dimensions.items():
            domain_weights[domain] = sum(indicator_weights.get(ind, 0) for ind in indicators)

    # Case 4: No weights provided - equal weighting
    else:
        total_indicators = len(all_indicators)
        if total_indicators == 0:
            raise ValueError("No indicators defined in dimensions")
        indicator_weights = {ind: 1/total_indicators for ind in all_indicators}
        domain_weights = {domain: sum(indicator_weights[ind] for ind in indicators) 
                         for domain, indicators in dimensions.items()}

    # Final validation checks
    if domain_weights:
        if not np.isclose(sum(domain_weights.values()), 1.0, atol=0.001):
            raise ValueError(f"Domain weights sum to {sum(domain_weights.values()):.3f} (should be 1)")
            
    if indicator_weights:
        missing_indicators = set(all_indicators) - set(indicator_weights.keys())
        if missing_indicators:
            raise ValueError(f"Missing weights for: {missing_indicators}")

    # ========== Core MPI Calculation ==========
    df['Deprivation_Score'] = df[all_indicators].apply(
        lambda row: sum(row[ind] * indicator_weights[ind] for ind in all_indicators),
        axis=1
    )
    
    df['Is_Poor'] = df['Deprivation_Score'] >= poverty_threshold
    
    H = df['Is_Poor'].mean()
    A = df.loc[df['Is_Poor'], 'Deprivation_Score'].mean() if H > 0 else 0
    MPI = H * A

    output_path = output_path or os.path.splitext(data_path)[0] + "_scored.csv"
    df.to_csv(output_path, index=False)
    
  # ========== New Analysis Functions ==========
    def get_deprivation_proportions(df, indicators):
        """DataFrame with indicator deprivation rates"""
        prop_df = pd.DataFrame({
            'Indicator': indicators,
            'Proportion_Deprived': [df[ind].mean() for ind in indicators]
        })
        return prop_df.sort_values('Proportion_Deprived', ascending=False)

    def get_contribution_analysis(df, indicator_weights, H):
        """DataFrame with MPI contribution analysis"""
        contribution_data = []
        poor_df = df[df['Is_Poor']] if H > 0 else pd.DataFrame()
        
        for ind, weight in indicator_weights.items():
            ind_prevalence = poor_df[ind].mean() if H > 0 else 0
            contribution = H * weight * ind_prevalence
            
            contribution_data.append({
                'Indicator': ind,
                'Weight': weight,
                'Contribution': contribution,
                'Prevalence_Among_Poor': ind_prevalence
            })
            
        contrib_df = pd.DataFrame(contribution_data)
        contrib_df['Contribution_Pct'] = (contrib_df['Contribution'] / MPI * 100) if MPI > 0 else 0
        return contrib_df.sort_values('Contribution', ascending=False)

    # ========== Core Calculation ==========
    # ... [Previous MPI calculation code remains unchanged] ...

    # Generate analysis DataFrames
    deprivation_df = get_deprivation_proportions(df, all_indicators)
    contribution_df = get_contribution_analysis(df, indicator_weights, H)

    # Save comprehensive results
    output_path = output_path or os.path.splitext(data_path)[0] + "_full_analysis.csv"
    df.to_csv(output_path, index=False)
    
    return {
        'data': df,
        'mpi_stats': {'H': H, 'A': A, 'MPI': MPI},
        'deprivation_analysis': deprivation_df,
        'contribution_analysis': contribution_df,
        'weights': pd.DataFrame({
            'Indicator': list(indicator_weights.keys()),
            'Weight': list(indicator_weights.values())
        })
    }