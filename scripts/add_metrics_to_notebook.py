import json
import os

def main():
    notebook_path = os.path.join("notebooks", "2_model_development_and_comparison.ipynb")
    if not os.path.exists(notebook_path):
        print(f"Error: {notebook_path} not found.")
        return

    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # We want to find the cell that contains: "### 4. Ranking Metric: MAP@10 Evaluation"
    # and insert our new cells after its execution cell.
    cells = nb["cells"]
    insert_idx = -1
    for i, cell in enumerate(cells):
        if cell["cell_type"] == "code" and "calculate_map_at_k" in "".join(cell["source"]):
            # Find the next code cell which executes it, and insert after it
            for j in range(i + 1, len(cells)):
                if cells[j]["cell_type"] == "code" and "svd_map" in "".join(cells[j]["source"]):
                    insert_idx = j + 1
                    break
            break

    if insert_idx == -1:
        print("Could not find the target cell to insert metrics evaluation.")
        return

    # Create new cells to insert
    new_markdown_cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 4.1. Additional Metrics Evaluation (Optional)\n",
            "\n",
            "We evaluate several additional metrics to provide a comprehensive comparison:\n",
            "- **MAE** (Mean Absolute Error) to measure rating prediction accuracy.\n",
            "- **Precision@10** and **Recall@10** to measure retrieval relevancy.\n",
            "- **NDCG@10** (Normalized Discounted Cumulative Gain) to evaluate ranking quality.\n",
            "- **Hit Rate@10** to determine what percentage of users get at least one relevant recommendation.\n",
            "- **Coverage** to check what percentage of users get recommendations.\n",
            "- **Diversity** (Intra-List Diversity) to measure the differences among recommendations."
        ]
    }

    new_code_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import math\n",
            "\n",
            "def evaluate_all_metrics(predictions, knn_model=None):\n",
            "    user_preds = defaultdict(list)\n",
            "    for uid, iid, true_r, est_r, _ in predictions:\n",
            "        user_preds[uid].append((iid, est_r, true_r))\n",
            "    \n",
            "    maes, precisions, recalls, ndcgs, ilds = [], [], [], [], []\n",
            "    hits, covered_users = 0, 0\n",
            "    \n",
            "    for uid, ratings in user_preds.items():\n",
            "        user_mae = np.mean([abs(true_r - est_r) for _, est_r, true_r in ratings])\n",
            "        maes.append(user_mae)\n",
            "        \n",
            "        n_rel = sum(1 for _, _, true_r in ratings if true_r >= 3.5)\n",
            "        if n_rel == 0: continue\n",
            "        covered_users += 1\n",
            "        \n",
            "        ratings.sort(key=lambda x: x[1], reverse=True)\n",
            "        top_k = ratings[:10]\n",
            "        \n",
            "        n_rel_k = sum(1 for _, _, true_r in top_k if true_r >= 3.5)\n",
            "        precisions.append(n_rel_k / 10.0)\n",
            "        recalls.append(n_rel_k / n_rel)\n",
            "        if n_rel_k > 0: hits += 1\n",
            "        \n",
            "        dcg = sum(1.0 / math.log2(i + 2) for i, (_, _, true_r) in enumerate(top_k) if true_r >= 3.5)\n",
            "        actual_sorted = sorted(ratings, key=lambda x: x[2], reverse=True)\n",
            "        idcg = sum(1.0 / math.log2(i + 2) for i, (_, _, true_r) in enumerate(actual_sorted[:10]) if true_r >= 3.5)\n",
            "        ndcgs.append(dcg / idcg if idcg > 0 else 0.0)\n",
            "        \n",
            "        # Calculate diversity using item similarity from KNN matrix\n",
            "        if knn_model is not None and len(top_k) > 1:\n",
            "            div_sum, pairs = 0.0, 0\n",
            "            for i in range(len(top_k)):\n",
            "                for j in range(i + 1, len(top_k)):\n",
            "                    iid1, _, _ = top_k[i]\n",
            "                    iid2, _, _ = top_k[j]\n",
            "                    try:\n",
            "                        inner1 = knn_model.trainset.to_inner_iid(iid1)\n",
            "                        inner2 = knn_model.trainset.to_inner_iid(iid2)\n",
            "                        sim = knn_model.sim[inner1, inner2]\n",
            "                    except ValueError:\n",
            "                        sim = 0.0\n",
            "                    div_sum += (1.0 - sim)\n",
            "                    pairs += 1\n",
            "            ilds.append(div_sum / pairs if pairs > 0 else 1.0)\n",
            "            \n",
            "    return {\n",
            "        'MAE': np.mean(maes),\n",
            "        'Precision@10': np.mean(precisions),\n",
            "        'Recall@10': np.mean(recalls),\n",
            "        'NDCG@10': np.mean(ndcgs),\n",
            "        'Hit Rate': hits / covered_users,\n",
            "        'Coverage': covered_users / len(user_preds),\n",
            "        'Diversity': np.mean(ilds) if ilds else 1.0\n",
            "    }\n",
            "\n",
            "print(\"Evaluating SVD metrics...\")\n",
            "svd_metrics = evaluate_all_metrics(svd_predictions, knn_model=knn_model)\n",
            "print(\"\\nEvaluating KNN metrics...\")\n",
            "knn_metrics = evaluate_all_metrics(knn_predictions, knn_model=knn_model)\n",
            "\n",
            "print(\"\\nSVD Additional Metrics:\", svd_metrics)\n",
            "print(\"KNN Additional Metrics:\", knn_metrics)"
        ]
    }

    # Insert cells
    cells.insert(insert_idx, new_markdown_cell)
    cells.insert(insert_idx + 1, new_code_cell)

    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)

    print("Notebook successfully updated with additional evaluation metrics!")

if __name__ == "__main__":
    main()
