# Tabbed Out: Subverting the Android Custom Tab Security Model

## Abstract

Mobile operating systems provide developers with various mobile-to-Web bridges to display Web pages inside native applications. A recently introduced component called Custom Tab (CT) provides an outstanding feature to overcome the usability limitations of traditional WebViews: it shares the state with the underlying browser. Similar to traditional WebViews, it can also keep the host application informed about ongoing Web navigations. In this paper, we perform the first systematic security evaluation of the CT component and show how the design of its security model did not consider crosscontext state inference attacks when the feature was introduced. Additionally, we show how CTs can be exploited for fine-grained exfiltration of sensitive user browsing data, violation of Web session integrity by circumventing SameSite cookies, and how UI customization of the CT component can lead to phishing and information leakage. To assess the prevalence of CTs in the wild and the practicality of the mitigation strategies we propose, we carry out the first large-scale analysis of CT usage on over 50K Android applications. Our analysis reveals that their usage is widespread, with 83% of applications embedding CTs either directly or as part of a library.

We have responsibly disclosed all our findings to Google, which has already taken steps to apply targeted mitigations, assigned three CVEs for the discovered vulnerabilities, and awarded us $10,000 in bounties. Our interaction with Google led to clarifications of the CT security model in the new Chrome Custom Tabs Security FAQ document.

## Contact

- Philipp Beer (philipp.beer@tuwien.ac.at)
- Marco Squarcina (marco.squarcina@tuwien.ac.at)
- Lorenzo Veronese (lorenzo.veronese@tuwien.ac.at)
- Martina Lindorfer (mlindorfer@iseclab.org)

## Citation

Please cite the paper as:

```
@inproceedings{beer2024tabbed,
  title={Tabbed Out: Subverting the Android Custom Tab Security Model},
  author={Beer, Philipp and Squarcina, Marco and Veronese, Lorenzo and Lindorfer, Martina},
  booktitle={2024 IEEE Symposium on Security and Privacy (SP)},
  pages={105--105},
  year={2024},
  organization={IEEE Computer Society}
}
```

## Artifacts

This repository contains artifacts for the paper. We provide the source code and results of the Custom Tab analysis in the wild and Proof of Concepts for the proposed attacks.

### Folder Structure
- `analysis` contains code and results for the Custom Tab analysis.
- `pocs` contains Proof of Concepts for the proposed attacks.