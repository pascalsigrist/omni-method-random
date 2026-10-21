import argparse
import json
import time
import anndata as ad
import numpy as np
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Random clustering baseline for Omnibenchmark")
    parser.add_argument("--input_file", type=str, required=True, help="Path to input data.h5ad")
    parser.add_argument("--clusters_truth_num", type=str, required=True, help="Path to numerical truth clusters file")
    parser.add_argument("--out_clusters", type=str, required=True, help="Path to output clusters tsv")
    parser.add_argument("--out_timings", type=str, required=True, help="Path to output timings json")
    parser.add_argument("--out_info", type=str, required=True, help="Path to output clustering info json")
    parser.add_argument("--out_pca", type=str, required=True, help="Path to output pca tsv")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--n_clusters", type=int, default=5, help="Number of random clusters to generate")
    
    args = parser.parse_args()
    
    start_time = time.time()
    
    # Read input dataset 
    adata = ad.read_h5ad(args.input_file)
    n_cells = adata.n_obs
    cell_names = adata.obs_index.values if hasattr(adata, "obs_index") else adata.obs.index.values
    
    # 2. Generate random cluster assignments
    np.random.seed(args.seed)
    random_labels = np.random.randint(0, args.n_clusters, size=n_cells)
    
    # 3. Format and save cluster output (.clusters.tsv)
    # Omnibenchmark methods.clusters expects a dataframe with cell IDs and assigned clusters
    clusters_df = pd.DataFrame({
        "cell_id": cell_names,
        "cluster": random_labels
    })
    clusters_df.to_csv(args.out_clusters, sep="\t", index=False)
    
    # 4. Create dummy PCA output (.pca.tsv) to satisfy output contract
    # Even if not evaluated for random baseline, the file must exist
    pca_df = pd.DataFrame(np.zeros((n_cells, 2)), columns=["PC1", "PC2"])
    pca_df.insert(0, "cell_id", cell_names)
    pca_df.to_csv(args.out_pca, sep="\t", index=False)
    
    # 5. Measure elapsed time and save timings (.timings.json)
    elapsed_time = time.time() - start_time
    timings = {"elapsed_time": elapsed_time}
    with open(args.out_timings, "w") as f:
        json.dump(timings, f)
        
    # 6. Save clustering metadata (.clustering_info.json)
    info = {"method": "random_baseline", "n_clusters": args.n_clusters, "seed": args.seed}
    with open(args.out_info, "w") as f:
        json.dump(info, f)

if __name__ == "__main__":
    main()
