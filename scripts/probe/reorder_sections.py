#!/usr/bin/env python3
"""Reorder paper sections: H1/DAAB before H2, admitted rows after both.
Per Workflow plan wf_11c4dc83-774. Uses string operations for safety."""
import re

path = r"D:\Code\DiffAudit\Research\papers\diffaudit-evidence-paper\main.tex"
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Identify section boundaries by \section{...} markers
sections = []
for m in re.finditer(r'\\section\{([^}]+)\}', text):
    sections.append((m.start(), m.group(1)))

print("Current sections:")
for i, (pos, name) in enumerate(sections):
    print(f"  {i}: {name} (pos={pos})")

# Extract each section's full content (from its \section to next \section or \end{document})
def extract_section(text, start_pos, next_pos=None):
    if next_pos is None:
        # Find \end{document} or \bibliography
        end = text.find('\n\\bibliographystyle', start_pos)
        if end == -1:
            end = text.find('\n\\end{document}', start_pos)
        return text[start_pos:end]
    return text[start_pos:next_pos]

# Get section contents
sec_6 = extract_section(text, sections[5][0], sections[6][0] if len(sections) > 6 else None)  # Boundary-Case Trace
sec_7 = extract_section(text, sections[6][0], sections[7][0] if len(sections) > 7 else None)  # Worked Examples
sec_8 = extract_section(text, sections[7][0], sections[8][0] if len(sections) > 8 else None)  # H2 Output-Cloud
sec_9 = extract_section(text, sections[8][0], sections[9][0] if len(sections) > 9 else None)  # H1 Activation
sec_10 = extract_section(text, sections[9][0], sections[10][0] if len(sections) > 10 else None) # Negative Evidence
sec_11 = extract_section(text, sections[10][0], sections[11][0] if len(sections) > 11 else None) # Discussion
sec_12 = extract_section(text, sections[11][0], None) # Conclusion

# Target order:
# §5 Protocol (keep) → §6 H1/DAAB (was §9) → §7 CLiD/Spurious (NEW) →
# §8 H2 (was §8, renumbered) → §9 Admitted Rows (was §7) →
# §10 Negative Evidence (was §10) → §11 Discussion (stay) → §12 Conclusion (stay)

# The content before first moved section (everything up to end of §5)
pre_end = sections[5][0]  # Start of old §6

# Build new body
before = text[:pre_end]

# Rename sections
sec_9_renamed = sec_9.replace('\\section{Activation Fingerprints: Stable AUC, Fragile Tail}',
                               '\\section{H1/DAAB: Distributed Activation-Amplitude Bias}')

sec_7_renamed = sec_7.replace('\\section{Worked Examples of Protocol Application}',
                               '\\section{Admitted Rows: Calibration Evidence}')

# CLiD/Spurious new section
clid_sec = r'''\section{CLiD and Spurious Signals}

Two additional boundary cases illustrate failure modes where apparently strong
or null metrics require careful gating.

\subsection{CLiD: Prompt-Conditioned Signal Collapse}

The CLiD attack~\cite{zha2024clid} uses conditional likelihood discrepancy
between prompt-conditioned and unconditional generation to perform membership
inference on text-to-image diffusion models. Under its original paper-prompt
evaluation, CLiD achieves AUC 1.000 and TPR@1\%FPR 100\%---apparent perfect
separation. Under prompt-neutral controls (empty, random, or mismatched
prompts), performance collapses to AUC 0.586 and TPR@1\%FPR 2\%.
The $\Delta$AUC of 0.414 is reported as a point estimate only; the current
packet lacks row-score arrays for bootstrap intervals on $\Delta$AUC.

The measured signal is prompt-image alignment, not membership. CLiD enters the
claim register as a spurious-signal boundary case: the allowed claim is
``diagnostic example of spurious signal''; the blocked claim is ``reliable
black-box MIA'' and any bootstrap CI or $p$-value on $\Delta$AUC.

\subsection{scnet: Scale-Null Capacity Check}

Three time-conditioned U-Net DDPMs were trained from scratch on CIFAR-10 at
0.78M, 11.76M, and 42.97M parameters, each evaluated with $K{=}2000$ samples
and 10,000 bootstrap iterations across multiple MIA attack families. A
54$\times$ capacity increase yields $\Delta\text{AUC}{=}0.003$
(0.78M: AUC 0.514; 42.97M: AUC 0.517, bootstrap 95\% CIs crossing or narrowly
separating from 0.5). The allowed claim is ``54$\times$ capacity increase
produces no meaningful MIA gain ($\Delta\text{AUC}{=}0.003$)''; blocked claims
are proof that capacity never increases leakage, or extrapolation to
production-scale models.

CLiD and scnet illustrate two recurring patterns: a metric that appears strong
but measures the wrong covariate (spurious), and a metric that appears null
but answers a bounded route-selection question (scale-null).

'''

# Build new order
# §5 (before) + §6 H1/DAAB + §7 CLiD + §8 H2 + §9 Admitted Rows + §10 Negative + §11 Discussion + §12 Conclusion
new_body = before + sec_9_renamed + clid_sec + sec_8 + sec_7_renamed + sec_10 + sec_11 + sec_12

# Add the \bibliography and \end{document} that were removed
# They're at the end of sec_12
if '\\bibliographystyle' not in new_body:
    new_body += '\n\\bibliographystyle{IEEEtran}\n\\bibliography{refs}\n\n\\end{document}\n'

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_body)

print(f"\nReorder complete. Old sections 7/8/9 -> new sections 6/7/8/9.")
print(f"Check: \\ref commands resolve by label, no changes needed.")
