# Conversion of Guarino PDF  

The [01-guarino00formal.pdf](01-guarino00formal.pdf) was converted to text using claude-code. The converted file ([01-guarino00formal-converted.txt](guarino_text_files/01-guarino00formal-converted.txt)) was then manually corrected and important sections were saved in separate file. These sections include:
* Introduction
* Constraints and Assumptions
* Rigidity
* Identity
* Unity
* Dependence

Saving these sections allows to test the LLM using a specific section of the article (e.g., Rigidity) as well as test combined sections of the article; e.g., Introduction compbined with Rigidity and Constrains.

Steps used to convert [01-guarino00formal.pdf](01-guarino00formal.pdf) in to a text file.

## 1. Claude Conversion   
Using the claude-sonnet-4-5 modle, the following prompt was given (see [claude-prompt.txt](claude-prompt.txt)):
```
convert the file 01-guarino00formal.pdf to text. when you see a greek symbol use the ASCII equivalent word, such as phi or psi. For the unviersal quantification symbol, which looks like an upside down A, use the phrase 'forall'. For the existential quantification symbol, which looks like a backward E, use the phrase 'some'.
```
This produced the file [01-guarino00formal-converted.txt](guarino_text_files/01-guarino00formal-converted.txt).

## 2. Corrections to Claude conversion   
Not all the logic definitions were quite right. These were manually edited to make them more clear. In many cases, parenthesis were added and quantiefers made more succinct. For example: 
* `forall x forall y (phi(x) and phi(y) and rho(x,y) iff x = y)` was changed to `forall x,y((phi(x) and phi(y)) implies (rho(x,y) iff x = y))`
* `some xytt' Gamma(x,y,t,t')` as changed to `ome xytt'(Gamma(x,y,t,t'))`.  

In some cases, model operators were missing. For example, `some xP(x) and some x not P(x)` was changed to `possibly((some x(P(x))) and (some x(not P(x))))`.  

And somethimes the conversion was incorrect. For example, `forall xy (E(x,t) and phi(x,t) and E(y,t') and phi(y,t') and Gamma(x,y,t,t') implies x=y)` was changed to `(E(x,t) and phi(x,t) and E(y,t') and phi(y,t') and Gamma(x,y,t,t')) implies x=y`. `E` is Guarino's quantifer for "actual existence" (see page 2 of PDF).

This edited file was saved as [01-guarino00formal-converted-corrected.txt](guarino_text_files/01-guarino00formal-converted-corrected.txt).

## 3. Extract the Introduction   
Since the Introduction of the article contains important information, it was manually extracted form the corrected conversion and saved in the file [01-guarino00formal-introduction.txt](guarino_text_files/01-guarino00formal-introduction.txt).

## 4. Extract Contraints and Assumptions     
Since the information concerning constraints and assumptions made about the different metaproperites, this information was manually extracted from the corrected conversion and saved in the file [01-guarino00formal-constraints-assumptions.txt](guarino_text_files/01-guarino00formal-constraints-assumptions.txt)


## 5. Extract Metaproperty Sections   
Each of the metaproperty sections were extracted from the corrrect file. The Constraints section relevant to the metaproperty was included in the extracted metaproperty sections. In eachmetaproperty section, the Assumptions were included.  
This resulted in the files:
* [01-guarino00formal-rigidity.txt](guarino_text_files/01-guarino00formal-rigidity.txt)
* [01-guarino00formal-identity.txt](guarino_text_files/01-guarino00formal-identity.txt)
* [01-guarino00formal-unity.txt](guarino_text_files/01-guarino00formal-introduction-unity.txt)
* [01-guarino00formal-dependence.txt](guarino_text_files/01-guarino00formal-dependence.txt)

## 6. Combine Introduction and Metaproperty Files   
The Introduction file ([01-guarino00formal-introduction.txt](guarino_text_files/01-guarino00formal-introduction.txt)) was combined with each of the metaproperty section files (see step 5). Note, each of the metaproperty section files contains the relevant Constraints and Assumptions section. 

This resulted in the follwing files:
* [01-guarino00formal-introduction-rigidity.txt](guarino_text_files/01-guarino00formal-introduction-rigidity.txt)
* [01-guarino00formal-introduction-identity.txt](guarino_text_files/01-guarino00formal-introduction-identity.txt)
* [01-guarino00formal-introduction-unity.txt](guarino_text_files/01-guarino00formal-introduction-unity.txt)
* [01-guarino00formal-introduction-dependence.txt](guarino_text_files/01-guarino00formal-introduction-dependence.txt)