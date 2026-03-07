####################################################################
# reproduce batch analysis on using a single file (i.e., no agents)
####################################################################

### batch analysis with anthropic's claude model

# claude w/o any input files; this will use hardcode prompts
uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl \
--model anthropic \
--output output/analyzed_entities/analyzed_entities_claude_no_files.tsv

# use PDF of Guarino's "Formal Ontology in Information Systems" paper as input file
uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl \
--model anthropic \
--background-file data/raw/01-guarino00formal.pdf \
--output output/analyzed_entities/analyzed_entities_claude_pdf.tsv

# use Guarino's PDF converted to text
uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl \
--model anthropic \
--background-file data/raw/converted_text_files/guarino_text_files/01-guarino00formal-converted.txt \
--output output/analyzed_entities/analyzed_entities_claude_text.tsv

# use Guarino's PDF converted to text but with correction made
uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl \
--model anthropic \
--background-file data/raw/converted_text_files/guarino_text_files/01-guarino00formal-converted.txt \
--output output/analyzed_entities/analyzed_entities_claude_corrected_text.tsv

### batch analysis with gemini

# gemini w/o any input files; this will use hardcode prompts
uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl \
--model gemini \
--output output/analyzed_entities/analyzed_entities_gemini_no_files.tsv

# use PDF of Guarino's "Formal Ontology in Information Systems" paper as input file
uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl \
--model gemini \
--background-file data/raw/01-guarino00formal.pdf \
--output output/analyzed_entities/analyzed_entities_gemini_pdf.tsv

# use Guarino's PDF converted to text
uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl \
--model gemini \
--background-file data/raw/converted_text_files/guarino_text_files/01-guarino00formal-converted.txt \
--output output/analyzed_entities/analyzed_entities_gemini_text.tsv

# use Guarino's PDF converted to text but with correction made
uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl \
--model gemini \
--background-file data/raw/converted_text_files/guarino_text_files/01-guarino00formal-converted.txt \
--output output/analyzed_entities/analyzed_entities_gemini_corrected_text.tsv

####################################################################
# evaluate batch analysis using a single file (i.e., no agents)
####################################################################

### evaluate anthropic's claude model

# evaluate output using no files (i.e., hardcoded prompts)
uv run python scripts/evaluate_analysis.py \
output/analyzed_entities/analyzed_entities_claude_no_files.tsv \
data/raw/ground_truth.tsv \
--agent anthropic \
--output output/evaluation_results/evaluate_claude_no_files.json

# evaluate output using PDF of Guarino's "Formal Ontology in Information Systems" paper as input file
uv run python scripts/evaluate_analysis.py \
output/analyzed_entities/analyzed_entities_claude_pdf.tsv \
data/raw/ground_truth.tsv \
--agent anthropic \
--output output/evaluation_results/evaluate_claude_pdf.json

# evaluate output using Guarino's PDF converted to text
uv run python scripts/evaluate_analysis.py \
output/analyzed_entities/analyzed_entities_claude_text.tsv \
data/raw/ground_truth.tsv \
--agent anthropic \
--output output/evaluation_results/evaluate_claude_text.json

# evaluate output using Guarino's PDF converted to text but with correction made
uv run python scripts/evaluate_analysis.py \
output/analyzed_entities/analyzed_entities_claude_corrected_text.tsv \
data/raw/ground_truth.tsv \
--agent anthropic \
--output output/evaluation_results/evaluate_claude_corrected_text.json

### evaluate gemini model

# evaluate output using no files (i.e., hardcoded prompts)
uv run python scripts/evaluate_analysis.py \
output/analyzed_entities/analyzed_entities_gemini_no_files.tsv \
data/raw/ground_truth.tsv \
--agent gemini \
--output output/evaluation_results/evaluate_gemini_no_files.json

# evaluate output using PDF of Guarino's "Formal Ontology in Information Systems" paper as input file
uv run python scripts/evaluate_analysis.py \
output/analyzed_entities/analyzed_entities_gemini_pdf.tsv \
data/raw/ground_truth.tsv \
--agent gemini \
--output output/evaluation_results/evaluate_gemini_pdf.json

# evaluate output using Guarino's PDF converted to text
uv run python scripts/evaluate_analysis.py \
output/analyzed_entities/analyzed_entities_gemini_text.tsv \
data/raw/ground_truth.tsv \
--agent gemini \
--output output/evaluation_results/evaluate_gemini_text.json

# evaluate output using Guarino's PDF converted to text but with correction made
uv run python scripts/evaluate_analysis.py \
output/analyzed_entities/analyzed_entities_gemini_corrected_text.tsv \
data/raw/ground_truth.tsv \
--agent gemini \
--output output/evaluation_results/evaluate_gemini_corrected_text.json

### save non-agent evaluation results in a single tsv file for easier reporting and visualization
uv run python scripts/collect_evaluations.py \
  --files output/evaluation_results/evaluate_claude_no_files.json \
  		  output/evaluation_results/evaluate_claude_pdf.json \
          output/evaluation_results/evaluate_claude_text.json \
          output/evaluation_results/evaluate_claude_corrected_text.json \
          output/evaluation_results/evaluate_gemini_no_files.json \
          output/evaluation_results/evaluate_gemini_pdf.json \
          output/evaluation_results/evaluate_gemini_text.json \
          output/evaluation_results/evaluate_gemini_corrected_text.json \
  --indexes no-files pdf text corrected no-files pdf text corrected \
  --output output/collect_non_agent_results.tsv

# save non-agent evaluation results as a markdown file
uv run python scripts/collect_evaluations.py \
  --files output/evaluation_results/evaluate_claude_no_files.json \
  		  output/evaluation_results/evaluate_claude_pdf.json \
          output/evaluation_results/evaluate_claude_text.json \
          output/evaluation_results/evaluate_claude_corrected_text.json \
          output/evaluation_results/evaluate_gemini_no_files.json \
          output/evaluation_results/evaluate_gemini_pdf.json \
          output/evaluation_results/evaluate_gemini_text.json \
          output/evaluation_results/evaluate_gemini_corrected_text.json \
  --indexes no-files pdf text corrected no-files pdf text corrected \
  --output output/collect_non_agent_results.md

# save markdow file as report in the reports folder
cp output/collect_non_agent_results.md docs/reports/NON_AGENT_BATCH_ANALYSIS_REPORT.md

####################################################################
# reproduce batch analysis on using agents
####################################################################

### agent batch analysis with anthropic's claude model

# claude w/o any input files; this will use hardcode prompts
uv run python scripts/batch_analyze_owl_agents.py output/ontologies/guarino_messy.owl \
--model anthropic \
--no-default-backgrounds \
--output output/analyzed_entities/analyzed_entities_claude_agents_no_files.tsv

# use specific sections of Guarino's file (no introduction section) 
# the sections are extracted from the converted text file with corrections made
uv run python scripts/batch_analyze_owl_agents.py output/ontologies/guarino_messy.owl \
--model anthropic \
--default-background-file-type simple \
--output output/analyzed_entities/analyzed_entities_claude_agents_using_files_no_intro.tsv

# use specific sections of Guarino's file, but include the introduction section as well 
# since it contains important context about the paper and ontology 
# the sections are extracted from the converted text file with corrections made
uv run python scripts/batch_analyze_owl_agents.py output/ontologies/guarino_messy.owl \
--model anthropic \
--default-background-file-type augmented \
--output output/analyzed_entities/analyzed_entities_claude_agents_using_files_with_intro.tsv

### agent batch analysis using gemini

# gemini w/o any input files; this will use hardcode prompts
uv run python scripts/batch_analyze_owl_agents.py output/ontologies/guarino_messy.owl \
--model gemini \
--no-default-backgrounds \
--output output/analyzed_entities/analyzed_entities_gemini_agents_no_files.tsv

# use specific sections of Guarino's file (no introduction section)
# the sections are extracted from the converted text file with corrections made
uv run python scripts/batch_analyze_owl_agents.py output/ontologies/guarino_messy.owl \
--model gemini \
--default-background-file-type simple \
--output output/analyzed_entities/analyzed_entities_gemini_agents_using_files_no_intro.tsv

# use specific sections of Guarino's file, but include the introduction section as well 
# since it contains important context about the paper and ontology
# the sections are extracted from the converted text file with corrections made
uv run python scripts/batch_analyze_owl_agents.py output/ontologies/guarino_messy.owl \
--model gemini \
--default-background-file-type augmented \
--output output/analyzed_entities/analyzed_entities_gemini_agents_using_files_with_intro.tsv

####################################################################
# evaluate batch analysis using agents
####################################################################

### evaluate agent batch analysis with anthropic's claude model

# evaluate output using no files (i.e., hardcoded prompts)
uv run python scripts/evaluate_analysis.py \
output/analyzed_entities/analyzed_entities_claude_agents_no_files.tsv \
data/raw/ground_truth.tsv \
--agent anthropic \
--output output/evaluation_results/evaluate_claude_agents_no_files.json

# evaluate output using specific sections of Guarino's file (no introduction section)
# the sections are extracted from the converted text file with corrections made
uv run python scripts/evaluate_analysis.py \
output/analyzed_entities/analyzed_entities_claude_agents_using_files_no_intro.tsv \
data/raw/ground_truth.tsv \
--agent anthropic \
--output output/evaluation_results/evaluate_claude_agents_using_files_no_intro.json 

# evaluate output using specific sections of Guarino's file, but include the introduction section as well 
# since it contains important context about the paper and ontology
# the sections are extracted from the converted text file with corrections made
uv run python scripts/evaluate_analysis.py \
output/analyzed_entities/analyzed_entities_claude_agents_using_files_with_intro.tsv \
data/raw/ground_truth.tsv \
--agent anthropic \
--output output/evaluation_results/evaluate_claude_agents_using_files_with_intro.json

### evaluate agent batch analysis with gemini

# evaluate output using no files (i.e., hardcoded prompts)
uv run python scripts/evaluate_analysis.py \
output/analyzed_entities/analyzed_entities_gemini_agents_no_files.tsv \
data/raw/ground_truth.tsv \
--agent gemini \
--output output/evaluation_results/evaluate_gemini_agents_no_files.json

# evaluate output using specific sections of Guarino's file (no introduction section)
# the sections are extracted from the converted text file with corrections made
uv run python scripts/evaluate_analysis.py \
output/analyzed_entities/analyzed_entities_gemini_agents_using_files_no_intro.tsv \
data/raw/ground_truth.tsv \
--agent gemini \
--output output/evaluation_results/evaluate_gemini_agents_using_files_no_intro.json

# evaluate output using specific sections of Guarino's file, but include the introduction section as well 
# since it contains important context about the paper and ontology
# the sections are extracted from the converted text file with corrections made
uv run python scripts/evaluate_analysis.py \
output/analyzed_entities/analyzed_entities_gemini_agents_using_files_with_intro.tsv \
data/raw/ground_truth.tsv \
--agent gemini \
--output output/evaluation_results/evaluate_gemini_agents_using_files_with_intro.json

### save agent evaluation results in a single tsv file for easier reporting and visualization
uv run python scripts/collect_evaluations.py \
  --files output/evaluation_results/evaluate_claude_agents_no_files.json \
          output/evaluation_results/evaluate_claude_agents_using_files_no_intro.json \
          output/evaluation_results/evaluate_claude_agents_using_files_with_intro.json \
          output/evaluation_results/evaluate_gemini_agents_no_files.json \
          output/evaluation_results/evaluate_gemini_agents_using_files_no_intro.json \
          output/evaluation_results/evaluate_gemini_agents_using_files_with_intro.json \
  --indexes no-files no-intro with-intro no-files no-intro with-intro \
  --output output/collect_agent_results.tsv

# save both agent evvaluation results as a markdown file
uv run python scripts/collect_evaluations.py \
  --files output/evaluation_results/evaluate_claude_agents_no_files.json \
          output/evaluation_results/evaluate_claude_agents_using_files_no_intro.json \
          output/evaluation_results/evaluate_claude_agents_using_files_with_intro.json \
          output/evaluation_results/evaluate_gemini_agents_no_files.json \
          output/evaluation_results/evaluate_gemini_agents_using_files_no_intro.json \
          output/evaluation_results/evaluate_gemini_agents_using_files_with_intro.json \
  --indexes no-files no-intro with-intro no-files no-intro with-intro \
  --output output/collect_agent_results.md

  # save markdow file as report in the reports folder
  cp output/collect_agent_results.md docs/reports/AGENT_BATCH_ANALYSIS_REPORT.md