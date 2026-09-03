# Experiment for LLM Prompts

## Goal 
The LLMs (ChatGPT, Claude, Gemini) have been tasked with revising the agents' instructions for determining the Ontoclean metaproperty values. We need to evaluate how well the revisions assigned the values compared to the ground truth.

## Method
For each type of metaproperty revision (LLM's response, edited response, synthesized prompt), use the LLM-specific revision to evaluate the ground-truth terms and calculate percent match with the ground-truth table. Output the percentages in table.

## Ground Truth

| Term | Rigidity | Identity | Own Identity | Unity | Dependence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Entity | +R | -I | -O | -U | -D |
| Location | +R | +I | +O | -U | -D |
| AmountOfMatter | +R | +I | +O | ~U | -D |
| Red | -R | -I | -O | -U | -D |
| Agent | ~R | -I | -O | -U | +D |
| Group | +R | +I | +O | -U | -D |
| PhysicalObject | +R | +I | +O | +U | -D |
| LivingBeing | +R | +I | +O | +U | -D |
| GroupOfPeople | +R | +I | -O | -U | -D |
| Fruit | +R | +I | +O | +U | -D |
| Food | ~R | +I | -O | ~U | +D |
| Animal | +R | +I | +O | +U | -D |
| SocialEntity | +R | +I | +O | +U | -D |
| Apple | +R | +I | +O | +U | -D |
| Vertebrate | +R | +I | -O | +U | -D |
| LegalAgent | ~R | +I | +O | -U | +D |
| Organization | +R | +I | +O | +U | +D |
| RedApple | ~R | +I | -O | +U | -D |
| Caterpillar | ~R | +I | -O | +U | -D |
| Butterfly | ~R | +I | -O | +U | -D |
| Person | +R | +I | +O | +U | -D |
| Country | +R | +I | +O | +U | +D |

## Output Table Format

| Revision Type    | LLM      | Rigidity | Identity | Own Identity | Unity | Dependence |
| :---             | :---     | :---:    | :---:    | :---:        | :---: | :---:      |
| Response         | Chat-GPT |   %      |     %    |      %       |   %   |    %       |
| Response         | Claude   |   %      |     %    |      %       |   %   |    %       |
| Response         | Gemini   |   %      |     %    |      %       |   %   |    %       |
|------------------|----------|----------|----------|--------------|-------|------------|
| Edited Response  | Chat-GPT |   %      |     %    |      %       |   %   |    %       |
| Edited Response  | Claude   |   %      |     %    |      %       |   %   |    %       |
| Edited Response  | Gemini   |   %      |     %    |      %       |   %   |    %       |
|------------------|----------|----------|----------|--------------|-------|------------|
| Synthesized      | Chat-GPT |   %      |     %    |      %       |   %   |    %       |
| Synthesized      | Claude   |   %      |     %    |      %       |   %   |    %       |
| Synthesized      | Gemini   |   %      |     %    |      %       |   %   |    %       |
