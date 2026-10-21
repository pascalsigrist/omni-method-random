import argparse
import json
import os
import time
import anndata as ad
import numpy as np
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Random clustering baseline for Omnibenchmark")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save outputs")
    parser.add_argument("--name", type=str, required=True, help="Dataset name prefix")
    parser.add_argument("--data.h5ad", dest="data_h5ad", type=str, required=True, help="Path to input data.h5ad")
    parser.add_argument("--data.clusters_truth_num", dest="data_clusters_truth_num", type=str, required=True, help="Path to numerical truth clusters file")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--n_clusters", type=int, default=5, help="Number of random clusters to generate")
    
    args = parser.parse_args()
    
    start_time = time.time()
    
    # 1. Read input dataset to find out how many cells there are
    adata = ad.read_h5ad(getattr(args, "data_h5ad"))
    cell_names = adata.obs_index.values if hasattr(adata, "obs_index") else adata.obs.index.values
    n_cells = len(cell_names)
    
    # 2. Generate random cluster assignments
    np.random.seed(args.seed)
    random_labels = np.random.randint(0, args.n_clusters, size=n_cells)
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 3. Format and save cluster output (.clusters.tsv)
    clusters_path = os.path.join(args.output_dir, f"{args.name}.clusters.tsv")
    clusters_df = pd.DataFrame({
        "cell_id": cell_names,
        "cluster": random_labels
    })
    clusters_df.to_csv(clusters_path, sep="\t", index=False)
    
    # 4. Create dummy PCA output (.pca.tsv) to satisfy output contract
    pca_path = os.path.join(args.output_dir, f"{args.name}.pca.tsv")
    pca_df = pd.DataFrame(np.zeros((n_cells, 2)), columns=["PC1", "PC2"])
    pca_df.insert(0, "cell_id", cell_names)
    pca_df.to_csv(pca_path, sep="\t", index=False)
    
    # 5. Measure elapsed time and save timings (.timings.json)
    timings_path = os.path.join(args.output_dir, f"{args.name}.timings.json")
    elapsed_time = time.time() - start_time
    with open(timings_path, "w") as f:
        json.dump({"elapsed_time": elapsed_time}, f)
        
    # 6. Save clustering metadata (.clustering_info.json)
    info_path = os.path.join(args.output_dir, f"{args.name}.clustering_info.json")
    with open(info_path, "w") as f:
        json.dump({"method": "random_baseline", "n_clusters": args.n_clusters, "seed": args.seed}, f)

if __name__ == "__main__":
    main()
