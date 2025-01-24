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
    # ... [Previous weight handling and validation code remains unchanged] ...

    # ========== New Analysis Functions ==========
    def calculate_deprivation_proportions(df, indicators):
        """Calculate proportion deprived in each indicator"""
        return {ind: df[ind].mean() for ind in indicators}

    def calculate_indicator_contributions(df, indicator_weights, H):
        """Calculate each indicator's contribution to MPI"""
        if H == 0:
            return {ind: 0 for ind in indicator_weights}
        
        poor_df = df[df['Is_Poor']]
        contributions = {}
        total_mpi = 0
        
        for ind, weight in indicator_weights.items():
            # Contribution formula: H * (weight * prevalence_in_poor)
            ind_prevalence = poor_df[ind].mean()
            contributions[ind] = H * weight * ind_prevalence
            total_mpi += contributions[ind]
        
        # Normalize to account for floating point errors
        if not np.isclose(total_mpi, H * poor_df['Deprivation_Score'].mean()):
            raise ValueError("Contribution calculation error")
            
        return contributions

    # ========== Core Calculation ==========
    # ... [Previous MPI calculation code remains unchanged] ...

    # Calculate additional metrics
    deprivation_proportions = calculate_deprivation_proportions(df, all_indicators)
    indicator_contributions = calculate_indicator_contributions(df, indicator_weights, H)

    # Save comprehensive results
    output_path = output_path or os.path.splitext(data_path)[0] + "_full_analysis.csv"
    df.to_csv(output_path, index=False)
    
    return {
        'data': df,
        'H': H,
        'A': A,
        'MPI': MPI,
        'deprivation_proportions': deprivation_proportions,
        'indicator_contributions': indicator_contributions,
        'indicator_weights': indicator_weights
    }

