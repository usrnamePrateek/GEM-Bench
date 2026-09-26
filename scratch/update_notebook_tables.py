import json

notebook_path = '/home/gpuuser7/gpuuser7_a/prateek/GEM-Bench/analysis/evaluation_analysis.ipynb'
with open(notebook_path, 'r') as f:
    nb = json.load(f)

# Find and remove "## Per-Judge Tables" and its code cell
cells_to_keep = []
skip_next = False
for i, cell in enumerate(nb['cells']):
    if skip_next:
        skip_next = False
        continue
    
    if cell['cell_type'] == 'markdown':
        source = "".join(cell['source'])
        if '## Per-Judge Tables' in source:
            skip_next = True # Skip the code cell that follows
            continue
            
    if cell['cell_type'] == 'code' and 'for judge in combined[\'judge\'].unique():' in "".join(cell['source']):
        # If it's the quantitative per-judge loop, remove those lines
        source = cell['source']
        new_source = []
        skip_loop = False
        for line in source:
            if 'for judge in combined[\'judge\'].unique():' in line:
                skip_loop = True
            if skip_loop and not line.startswith(' ') and line.strip() != '' and not line.startswith('for judge'):
                skip_loop = False
            
            if not skip_loop:
                new_source.append(line)
        cell['source'] = new_source
        
    cells_to_keep.append(cell)

nb['cells'] = cells_to_keep

# Insert new markdown and code cells for "## Per Base and Judge Tables" before LaTeX export
insert_idx = len(nb['cells'])
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown' and '## LaTeX Export' in "".join(cell['source']):
        insert_idx = i
        break

new_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## Per Base and Judge Tables\n",
        "\n",
        "Tables filtered to specific combinations of Base LLM and Judge LLM."
    ]
}

new_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "combinations = combined[['base_llm', 'judge']].drop_duplicates().values\n",
        "for base, judge in combinations:\n",
        "    subset = combined[(combined['base_llm'] == base) & (combined['judge'] == judge)]\n",
        "    if len(subset) > 0:\n",
        "        print(f\"\\n{'='*60}\\nBase: {base} | Judge: {judge}\\n{'='*60}\")\n",
        "        # Qualitative\n",
        "        qual_table = build_paper_table(subset)\n",
        "        display(style_table(qual_table, title=f'Qualitative Metrics (Base: {base}, Judge: {judge})'))\n",
        "        # Quantitative\n",
        "        quant_table = build_quant_paper_table(subset)\n",
        "        display(style_quant_table(quant_table, title=f'Quantitative Metrics (Base: {base}, Judge: {judge})'))\n"
    ]
}

nb['cells'].insert(insert_idx, new_md)
nb['cells'].insert(insert_idx + 1, new_code)

with open(notebook_path, 'w') as f:
    json.dump(nb, f, indent=1)
