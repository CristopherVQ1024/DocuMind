# Resultados

| Tipo | Total | Test |
|---|---|---|
| literal | 120 | 98 |
| temporal | 120 | 98 |
| rastreo | 74 | 64 |
| multisalto | 84 | 67 |
| premisa_falsa | 56 | 43 |
| sin_respuesta | 76 | 61 |

## Recuperación (partición test, preguntas con evidencia)
| Sistema | n | Hit@1 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 | Todos@10 | s/consulta |
|---|---|---|---|---|---|---|---|---|
| recencia | 370 | 0.757 | 0.896 | 0.934 | 0.833 | 0.836 | 0.657 | 0.158 |
| hibrido_rr_trozos | 370 | 0.741 | 0.897 | 0.932 | 0.827 | 0.832 | 0.642 | 0.189 |
| hibrido_rr | 370 | 0.732 | 0.899 | 0.931 | 0.821 | 0.828 | 0.657 | 0.168 |
| propuesto | 370 | 0.732 | 0.899 | 0.931 | 0.821 | 0.828 | 0.657 | 0.160 |
| denso | 370 | 0.616 | 0.782 | 0.835 | 0.706 | 0.721 | 0.627 | 0.007 |
| hibrido | 370 | 0.597 | 0.780 | 0.847 | 0.695 | 0.714 | 0.612 | 0.008 |
| bm25 | 370 | 0.489 | 0.722 | 0.809 | 0.610 | 0.642 | 0.597 | 0.004 |
| denso_sin_cabecera | 370 | 0.532 | 0.716 | 0.754 | 0.630 | 0.641 | 0.522 | 0.008 |
| tacna_bge | 370 | 0.576 | 0.639 | 0.659 | 0.626 | 0.609 | 0.522 | 1.017 |
| ingenuo | 370 | 0.384 | 0.601 | 0.681 | 0.494 | 0.520 | 0.463 | 0.044 |
| tacna_minilm | 370 | 0.416 | 0.408 | 0.423 | 0.435 | 0.408 | 0.179 | 1.043 |

### Recall@5 por tipo de pregunta
| Sistema | literal | temporal | rastreo | multisalto | premisa_falsa |
|---|---|---|---|---|---|
| bm25 | 0.663 | 0.755 | 0.625 | 0.716 | 0.930 |
| denso | 0.908 | 0.949 | 0.359 | 0.709 | 0.860 |
| denso_sin_cabecera | 0.878 | 0.908 | 0.078 | 0.687 | 0.907 |
| hibrido | 0.827 | 0.867 | 0.500 | 0.724 | 0.977 |
| hibrido_rr | 0.969 | 0.918 | 0.844 | 0.754 | 1.000 |
| hibrido_rr_trozos | 0.959 | 0.929 | 0.859 | 0.746 | 0.977 |
| ingenuo | 0.806 | 0.755 | 0.078 | 0.560 | 0.628 |
| propuesto | 0.969 | 0.918 | 0.844 | 0.754 | 1.000 |
| recencia | 0.949 | 0.918 | 0.891 | 0.754 | 0.953 |
| tacna_bge | 0.888 | 0.061 | 0.875 | 0.694 | 0.953 |
| tacna_minilm | 0.510 | 0.031 | 0.828 | 0.388 | 0.442 |

### Diferencia de nDCG@10: hibrido_rr menos cada sistema (Wilcoxon, IC bootstrap 95 %, Holm)
| Sistema | Δ media | IC 95 % | p | p Holm |
|---|---|---|---|---|
| tacna_minilm | 0.420 | [0.370, 0.471] | 1.04e-35 | 1.04e-34 |
| ingenuo | 0.308 | [0.268, 0.348] | 2.52e-34 | 2.27e-33 |
| bm25 | 0.186 | [0.150, 0.223] | 8.22e-19 | 6.57e-18 |
| denso_sin_cabecera | 0.187 | [0.150, 0.226] | 2.56e-17 | 1.79e-16 |
| tacna_bge | 0.219 | [0.174, 0.266] | 2.68e-15 | 1.61e-14 |
| denso | 0.107 | [0.075, 0.140] | 2.62e-09 | 1.31e-08 |
| hibrido | 0.115 | [0.081, 0.149] | 3.85e-08 | 1.54e-07 |
| hibrido_rr_trozos | -0.004 | [-0.017, 0.008] | 1.73e-01 | 5.18e-01 |
| recencia | -0.008 | [-0.018, 0.002] | 4.34e-01 | 8.69e-01 |
| propuesto | 0.000 | [0.000, 0.000] | 1.00e+00 | 1.00e+00 |

## Generación (partición test)
| Corrida | n | Cita P | Cita R | Estado ok | Anacronismo | Rastreo ok | Abst P | Abst R | Abst F1 | JSON ok | s/resp | tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hibrido_rr__gemma3-12b | 431 | 0.675 | 0.709 | 0.298 | 0.881 | 0.125 | 0.565 | 0.574 | 0.569 | 1.000 | 6.912 | 1823.826 |
| hibrido_rr__llama3.1-8b | 431 | 0.653 | 0.689 | 0.340 | 0.901 | 0.125 | 0.600 | 0.246 | 0.349 | 1.000 | 1.836 | 1996.151 |
| ingenuo__gemma3-12b | 431 | 0.386 | 0.400 | 0.305 | 0.792 | 0.031 | 0.362 | 0.475 | 0.411 | 1.000 | 7.536 | 1638.348 |
| ingenuo__llama3.1-8b | 431 | 0.380 | 0.405 | 0.369 | 0.871 | 0.000 | 0.211 | 0.131 | 0.162 | 1.000 | 1.684 | 1795.012 |
| propuesto__gemma3-12b | 431 | 0.687 | 0.731 | 0.369 | 0.505 | 0.859 | 0.598 | 0.902 | 0.719 | 1.000 | 7.190 | 1699.770 |
| propuesto__llama3.1-8b | 431 | 0.689 | 0.718 | 0.312 | 0.723 | 0.828 | 0.659 | 0.885 | 0.755 | 1.000 | 1.626 | 1804.796 |
| propuesto_det__gemma3-12b | 431 | 0.687 | 0.731 | 0.525 | 0.307 | 0.859 | 0.598 | 0.902 | 0.719 | 1.000 | 7.190 | 1699.770 |
| propuesto_det__llama3.1-8b | 431 | 0.689 | 0.718 | 0.567 | 0.347 | 0.828 | 0.659 | 0.885 | 0.755 | 1.000 | 1.626 | 1804.796 |
| propuesto_sincompuerta__llama3.1-8b | 431 | 0.719 | 0.749 | 0.362 | 0.891 | 0.828 | 0.867 | 0.213 | 0.342 | 1.000 | 4.554 | 2194.000 |
| propuesto_sincompuerta_det__llama3.1-8b | 431 | 0.719 | 0.749 | 0.617 | 0.495 | 0.828 | 0.867 | 0.213 | 0.342 | 1.000 | 4.554 | 2194.000 |
| propuesto_sinvigencia__llama3.1-8b | 431 | 0.598 | 0.634 | 0.312 | 0.723 | 0.125 | 0.576 | 0.869 | 0.693 | 1.000 | 3.787 | 1641.462 |
| propuesto_sinvigencia_det__llama3.1-8b | 431 | 0.598 | 0.634 | 0.553 | 0.317 | 0.125 | 0.576 | 0.869 | 0.693 | 1.000 | 3.787 | 1641.462 |
| recencia__llama3.1-8b | 431 | 0.666 | 0.708 | 0.319 | 0.941 | 0.109 | 0.643 | 0.295 | 0.404 | 1.000 | 1.906 | 2118.067 |
| tacna_bge__gemma3-12b | 431 | 0.469 | 0.484 | 0.135 | 0.426 | 0.047 | 0.200 | 0.525 | 0.290 | 1.000 | 5.687 | 1199.944 |
| tacna_bge__llama3.1-8b | 431 | 0.506 | 0.518 | 0.326 | 0.525 | 0.047 | 0.250 | 0.164 | 0.198 | 1.000 | 1.452 | 1305.211 |
| tacna_minilm__llama3.1-8b | 431 | 0.371 | 0.353 | 0.220 | 0.505 | 0.047 | 0.321 | 0.410 | 0.360 | 1.000 | 1.307 | 1121.262 |

### Exactitud de estado temporal, propuesto contra cada corrida con gemma3-12b (McNemar exacto, Holm)
| Corrida | n | propuesto | corrida | p | p Holm |
|---|---|---|---|---|---|
| hibrido_rr__gemma3-12b | 141 | 0.369 | 0.298 | 6.39e-02 | 1.28e-01 |
| ingenuo__gemma3-12b | 141 | 0.369 | 0.305 | 1.08e-01 | 1.28e-01 |
| propuesto_det__gemma3-12b | 141 | 0.369 | 0.525 | 2.98e-06 | 1.19e-05 |
| tacna_bge__gemma3-12b | 141 | 0.369 | 0.135 | 3.39e-06 | 1.19e-05 |

### Exactitud de estado temporal, propuesto contra cada corrida con llama3.1-8b (McNemar exacto, Holm)
| Corrida | n | propuesto | corrida | p | p Holm |
|---|---|---|---|---|---|
| hibrido_rr__llama3.1-8b | 141 | 0.312 | 0.340 | 3.44e-01 | 1.00e+00 |
| ingenuo__llama3.1-8b | 141 | 0.312 | 0.369 | 9.63e-02 | 4.81e-01 |
| propuesto_det__llama3.1-8b | 141 | 0.312 | 0.567 | 1.49e-09 | 1.34e-08 |
| propuesto_sincompuerta__llama3.1-8b | 141 | 0.312 | 0.362 | 1.56e-02 | 1.09e-01 |
| propuesto_sincompuerta_det__llama3.1-8b | 141 | 0.312 | 0.617 | 1.60e-11 | 1.60e-10 |
| propuesto_sinvigencia__llama3.1-8b | 141 | 0.312 | 0.312 | 1.00e+00 | 1.00e+00 |
| propuesto_sinvigencia_det__llama3.1-8b | 141 | 0.312 | 0.553 | 1.41e-07 | 1.12e-06 |
| recencia__llama3.1-8b | 141 | 0.312 | 0.319 | 1.00e+00 | 1.00e+00 |
| tacna_bge__llama3.1-8b | 141 | 0.312 | 0.326 | 8.83e-01 | 1.00e+00 |
| tacna_minilm__llama3.1-8b | 141 | 0.312 | 0.220 | 7.25e-02 | 4.35e-01 |

### Exactitud de estado temporal, propuesto_det contra cada corrida con gemma3-12b (McNemar exacto, Holm)
| Corrida | n | propuesto_det | corrida | p | p Holm |
|---|---|---|---|---|---|
| hibrido_rr__gemma3-12b | 141 | 0.525 | 0.298 | 9.43e-07 | 2.83e-06 |
| ingenuo__gemma3-12b | 141 | 0.525 | 0.305 | 3.12e-06 | 5.96e-06 |
| propuesto__gemma3-12b | 141 | 0.525 | 0.369 | 2.98e-06 | 5.96e-06 |
| tacna_bge__gemma3-12b | 141 | 0.525 | 0.135 | 2.38e-11 | 9.52e-11 |

### Exactitud de estado temporal, propuesto_det contra cada corrida con llama3.1-8b (McNemar exacto, Holm)
| Corrida | n | propuesto_det | corrida | p | p Holm |
|---|---|---|---|---|---|
| hibrido_rr__llama3.1-8b | 141 | 0.567 | 0.340 | 5.61e-06 | 3.37e-05 |
| ingenuo__llama3.1-8b | 141 | 0.567 | 0.369 | 2.34e-04 | 7.03e-04 |
| propuesto__llama3.1-8b | 141 | 0.567 | 0.312 | 1.49e-09 | 1.38e-08 |
| propuesto_sincompuerta__llama3.1-8b | 141 | 0.567 | 0.362 | 1.54e-05 | 7.69e-05 |
| propuesto_sincompuerta_det__llama3.1-8b | 141 | 0.567 | 0.617 | 1.18e-01 | 2.37e-01 |
| propuesto_sinvigencia__llama3.1-8b | 141 | 0.567 | 0.312 | 4.41e-08 | 3.52e-07 |
| propuesto_sinvigencia_det__llama3.1-8b | 141 | 0.567 | 0.553 | 7.91e-01 | 7.91e-01 |
| recencia__llama3.1-8b | 141 | 0.567 | 0.319 | 1.22e-06 | 8.55e-06 |
| tacna_bge__llama3.1-8b | 141 | 0.567 | 0.326 | 5.85e-05 | 2.34e-04 |
| tacna_minilm__llama3.1-8b | 141 | 0.567 | 0.220 | 1.38e-09 | 1.38e-08 |

### Matriz de confusión de estado, propuesto__gemma3-12b
| Estado oro | Estado predicho | n |
|---|---|---|
| vigente | vigente | 35 |
| premisa_falsa | vigente | 23 |
| sin_version | vigente | 19 |
| premisa_falsa | fuera_corpus | 15 |
| sin_version | fuera_corpus | 11 |
| sin_version | sin_version | 8 |
| no_existia | vigente | 8 |
| no_existia | no_existia | 5 |
| vigente | fuera_corpus | 5 |
| premisa_falsa | premisa_falsa | 4 |
| sin_version | no_existia | 3 |
| no_existia | fuera_corpus | 2 |

### Matriz de confusión de estado, propuesto__llama3.1-8b
| Estado oro | Estado predicho | n |
|---|---|---|
| vigente | vigente | 35 |
| sin_version | vigente | 31 |
| premisa_falsa | vigente | 27 |
| no_existia | vigente | 15 |
| premisa_falsa | fuera_corpus | 9 |
| sin_version | fuera_corpus | 8 |
| premisa_falsa | premisa_falsa | 6 |
| vigente | fuera_corpus | 5 |
| sin_version | sin_version | 2 |
| no_existia | fuera_corpus | 2 |
| derogado | derogado | 1 |

### Matriz de confusión de estado, propuesto_det__gemma3-12b
| Estado oro | Estado predicho | n |
|---|---|---|
| vigente | vigente | 35 |
| sin_version | sin_version | 26 |
| premisa_falsa | vigente | 23 |
| premisa_falsa | fuera_corpus | 15 |
| sin_version | fuera_corpus | 11 |
| no_existia | no_existia | 8 |
| vigente | fuera_corpus | 5 |
| sin_version | vigente | 4 |
| no_existia | vigente | 4 |
| premisa_falsa | premisa_falsa | 4 |
| no_existia | sin_version | 3 |
| no_existia | fuera_corpus | 2 |

### Matriz de confusión de estado, propuesto_det__llama3.1-8b
| Estado oro | Estado predicho | n |
|---|---|---|
| vigente | vigente | 33 |
| sin_version | sin_version | 27 |
| premisa_falsa | vigente | 27 |
| no_existia | no_existia | 13 |
| premisa_falsa | fuera_corpus | 9 |
| sin_version | fuera_corpus | 8 |
| sin_version | vigente | 6 |
| premisa_falsa | premisa_falsa | 6 |
| vigente | fuera_corpus | 5 |
| no_existia | fuera_corpus | 2 |
| no_existia | vigente | 2 |
| vigente | sin_version | 1 |

### Matriz de confusión de estado, propuesto_sincompuerta__llama3.1-8b
| Estado oro | Estado predicho | n |
|---|---|---|
| vigente | vigente | 40 |
| sin_version | vigente | 38 |
| premisa_falsa | vigente | 35 |
| no_existia | vigente | 17 |
| premisa_falsa | premisa_falsa | 7 |
| sin_version | sin_version | 3 |
| derogado | derogado | 1 |

### Matriz de confusión de estado, propuesto_sincompuerta_det__llama3.1-8b
| Estado oro | Estado predicho | n |
|---|---|---|
| vigente | vigente | 38 |
| premisa_falsa | vigente | 35 |
| sin_version | sin_version | 29 |
| no_existia | no_existia | 12 |
| sin_version | vigente | 11 |
| premisa_falsa | premisa_falsa | 7 |
| no_existia | vigente | 4 |
| sin_version | no_existia | 1 |
| no_existia | sin_version | 1 |
| vigente | sin_version | 1 |
| vigente | no_existia | 1 |
| derogado | derogado | 1 |

### Matriz de confusión de estado, propuesto_sinvigencia__llama3.1-8b
| Estado oro | Estado predicho | n |
|---|---|---|
| vigente | vigente | 35 |
| sin_version | vigente | 32 |
| premisa_falsa | vigente | 25 |
| no_existia | vigente | 15 |
| premisa_falsa | fuera_corpus | 9 |
| sin_version | fuera_corpus | 8 |
| premisa_falsa | premisa_falsa | 8 |
| vigente | fuera_corpus | 5 |
| no_existia | fuera_corpus | 2 |
| sin_version | sin_version | 1 |
| derogado | vigente | 1 |

### Matriz de confusión de estado, propuesto_sinvigencia_det__llama3.1-8b
| Estado oro | Estado predicho | n |
|---|---|---|
| vigente | vigente | 32 |
| sin_version | sin_version | 26 |
| premisa_falsa | vigente | 25 |
| no_existia | no_existia | 11 |
| premisa_falsa | fuera_corpus | 9 |
| sin_version | fuera_corpus | 8 |
| premisa_falsa | premisa_falsa | 8 |
| vigente | fuera_corpus | 5 |
| sin_version | vigente | 4 |
| sin_version | no_existia | 3 |
| no_existia | vigente | 3 |
| no_existia | fuera_corpus | 2 |

## Juez automático (muestra estratificada, partición test)
| Corrida | n | Corrección media | Totalmente correcta | Fidelidad |
|---|---|---|---|---|
| hibrido_rr__gemma3-12b | 101 | 0.569 | 0.545 | 0.613 |
| hibrido_rr__llama3.1-8b | 101 | 0.510 | 0.495 | 0.555 |
| ingenuo__gemma3-12b | 101 | 0.609 | 0.564 | 0.634 |
| ingenuo__llama3.1-8b | 98 | 0.515 | 0.480 | 0.539 |
| propuesto__gemma3-12b | 101 | 0.886 | 0.861 | 0.882 |
| propuesto__llama3.1-8b | 101 | 0.772 | 0.743 | 0.754 |
| recencia__llama3.1-8b | 101 | 0.520 | 0.485 | 0.609 |
| tacna_bge__gemma3-12b | 101 | 0.505 | 0.455 | 0.513 |
| tacna_bge__llama3.1-8b | 101 | 0.480 | 0.386 | 0.498 |
| tacna_minilm__llama3.1-8b | 101 | 0.490 | 0.426 | 0.479 |
