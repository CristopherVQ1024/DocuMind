# Resultados

| Tipo | Total | Test |
|---|---|---|
| literal | 120 | 98 |
| temporal | 118 | 96 |
| rastreo | 74 | 64 |
| multisalto | 66 | 52 |
| premisa_falsa | 56 | 43 |
| sin_respuesta | 76 | 61 |

## Recuperación (partición test, preguntas con evidencia)
| Sistema | n | Hit@1 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 | Todos@10 | s/consulta |
|---|---|---|---|---|---|---|---|---|
| recencia | 353 | 0.759 | 0.904 | 0.941 | 0.833 | 0.843 | 0.692 | 0.158 |
| hibrido_rr_trozos | 353 | 0.745 | 0.905 | 0.941 | 0.828 | 0.840 | 0.692 | 0.188 |
| hibrido_rr | 353 | 0.737 | 0.907 | 0.938 | 0.822 | 0.835 | 0.692 | 0.168 |
| propuesto | 353 | 0.737 | 0.907 | 0.938 | 0.822 | 0.835 | 0.692 | 0.160 |
| denso | 353 | 0.623 | 0.786 | 0.839 | 0.707 | 0.726 | 0.673 | 0.007 |
| hibrido | 353 | 0.601 | 0.782 | 0.848 | 0.693 | 0.715 | 0.615 | 0.008 |
| denso_sin_cabecera | 353 | 0.530 | 0.724 | 0.759 | 0.625 | 0.645 | 0.615 | 0.008 |
| bm25 | 353 | 0.490 | 0.721 | 0.807 | 0.607 | 0.641 | 0.577 | 0.004 |
| tacna_bge | 353 | 0.572 | 0.643 | 0.663 | 0.620 | 0.611 | 0.577 | 1.006 |
| ingenuo | 353 | 0.385 | 0.602 | 0.680 | 0.490 | 0.521 | 0.500 | 0.046 |
| tacna_minilm | 353 | 0.414 | 0.414 | 0.428 | 0.432 | 0.412 | 0.212 | 1.033 |

### Recall@5 por tipo de pregunta
| Sistema | literal | temporal | rastreo | multisalto | premisa_falsa |
|---|---|---|---|---|---|
| bm25 | 0.663 | 0.750 | 0.625 | 0.721 | 0.930 |
| denso | 0.908 | 0.948 | 0.359 | 0.721 | 0.860 |
| denso_sin_cabecera | 0.878 | 0.917 | 0.078 | 0.721 | 0.907 |
| hibrido | 0.827 | 0.865 | 0.500 | 0.731 | 0.977 |
| hibrido_rr | 0.969 | 0.917 | 0.844 | 0.769 | 1.000 |
| hibrido_rr_trozos | 0.959 | 0.927 | 0.859 | 0.760 | 0.977 |
| ingenuo | 0.806 | 0.750 | 0.078 | 0.567 | 0.628 |
| propuesto | 0.969 | 0.917 | 0.844 | 0.769 | 1.000 |
| recencia | 0.949 | 0.917 | 0.891 | 0.769 | 0.953 |
| tacna_bge | 0.888 | 0.062 | 0.875 | 0.712 | 0.953 |
| tacna_minilm | 0.510 | 0.031 | 0.828 | 0.404 | 0.442 |

### Diferencia de nDCG@10: hibrido_rr menos cada sistema (Wilcoxon, IC bootstrap 95 %, Holm)
| Sistema | Δ media | IC 95 % | p | p Holm |
|---|---|---|---|---|
| tacna_minilm | 0.424 | [0.371, 0.476] | 3.41e-34 | 3.41e-33 |
| ingenuo | 0.314 | [0.273, 0.357] | 3.22e-33 | 2.90e-32 |
| bm25 | 0.194 | [0.157, 0.232] | 2.92e-19 | 2.34e-18 |
| denso_sin_cabecera | 0.190 | [0.151, 0.231] | 6.77e-17 | 4.74e-16 |
| tacna_bge | 0.224 | [0.175, 0.273] | 7.95e-15 | 4.77e-14 |
| denso | 0.109 | [0.074, 0.144] | 4.08e-09 | 2.04e-08 |
| hibrido | 0.120 | [0.084, 0.157] | 4.22e-09 | 2.04e-08 |
| hibrido_rr_trozos | -0.005 | [-0.019, 0.008] | 2.04e-01 | 6.12e-01 |
| recencia | -0.008 | [-0.018, 0.003] | 4.21e-01 | 8.42e-01 |
| propuesto | 0.000 | [0.000, 0.000] | 1.00e+00 | 1.00e+00 |

## Generación (partición test)
| Corrida | n | Cita P | Cita R | Estado ok | Anacronismo | Rastreo ok | Abst P | Abst R | Abst F1 | JSON ok | s/resp | tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hibrido_rr__gemma3-12b | 414 | 0.681 | 0.727 | 0.302 | 0.879 | 0.125 | 0.565 | 0.574 | 0.569 | 1.000 | 6.868 | 1811.324 |
| hibrido_rr__llama3.1-8b | 414 | 0.654 | 0.700 | 0.345 | 0.899 | 0.125 | 0.600 | 0.246 | 0.349 | 1.000 | 1.819 | 1982.191 |
| ingenuo__gemma3-12b | 414 | 0.381 | 0.402 | 0.309 | 0.798 | 0.031 | 0.367 | 0.475 | 0.414 | 1.000 | 7.538 | 1637.575 |
| ingenuo__llama3.1-8b | 414 | 0.383 | 0.412 | 0.367 | 0.879 | 0.000 | 0.211 | 0.131 | 0.162 | 1.000 | 1.673 | 1794.036 |
| propuesto__gemma3-12b | 414 | 0.692 | 0.745 | 0.374 | 0.495 | 0.859 | 0.598 | 0.902 | 0.719 | 1.000 | 6.966 | 1671.524 |
| propuesto__llama3.1-8b | 414 | 0.691 | 0.731 | 0.317 | 0.717 | 0.828 | 0.659 | 0.885 | 0.755 | 1.000 | 1.595 | 1774.809 |
| propuesto_det__gemma3-12b | 414 | 0.692 | 0.745 | 0.518 | 0.313 | 0.859 | 0.598 | 0.902 | 0.719 | 1.000 | 6.966 | 1671.524 |
| propuesto_det__llama3.1-8b | 414 | 0.691 | 0.731 | 0.561 | 0.354 | 0.828 | 0.659 | 0.885 | 0.755 | 1.000 | 1.595 | 1774.809 |
| propuesto_sincompuerta__llama3.1-8b | 414 | 0.720 | 0.762 | 0.367 | 0.889 | 0.828 | 0.867 | 0.213 | 0.342 | 1.000 | 4.523 | 2180.031 |
| propuesto_sincompuerta_det__llama3.1-8b | 414 | 0.720 | 0.762 | 0.612 | 0.505 | 0.828 | 0.867 | 0.213 | 0.342 | 1.000 | 4.523 | 2180.031 |
| propuesto_sinvigencia__llama3.1-8b | 414 | 0.597 | 0.642 | 0.317 | 0.717 | 0.125 | 0.576 | 0.869 | 0.693 | 1.000 | 3.685 | 1612.845 |
| propuesto_sinvigencia_det__llama3.1-8b | 414 | 0.597 | 0.642 | 0.554 | 0.323 | 0.125 | 0.576 | 0.869 | 0.693 | 1.000 | 3.685 | 1612.845 |
| recencia__llama3.1-8b | 414 | 0.669 | 0.715 | 0.324 | 0.939 | 0.109 | 0.643 | 0.295 | 0.404 | 1.000 | 1.885 | 2103.104 |
| tacna_bge__gemma3-12b | 414 | 0.467 | 0.487 | 0.137 | 0.434 | 0.047 | 0.203 | 0.525 | 0.292 | 1.000 | 5.635 | 1188.365 |
| tacna_bge__llama3.1-8b | 414 | 0.508 | 0.525 | 0.331 | 0.515 | 0.047 | 0.250 | 0.164 | 0.198 | 1.000 | 1.432 | 1292.121 |
| tacna_minilm__llama3.1-8b | 414 | 0.373 | 0.360 | 0.223 | 0.505 | 0.047 | 0.325 | 0.410 | 0.362 | 1.000 | 1.293 | 1112.048 |

### Exactitud de estado temporal, propuesto contra cada corrida con gemma3-12b (McNemar exacto, Holm)
| Corrida | n | propuesto | corrida | p | p Holm |
|---|---|---|---|---|---|
| hibrido_rr__gemma3-12b | 139 | 0.374 | 0.302 | 6.39e-02 | 1.28e-01 |
| ingenuo__gemma3-12b | 139 | 0.374 | 0.309 | 1.08e-01 | 1.28e-01 |
| propuesto_det__gemma3-12b | 139 | 0.374 | 0.518 | 1.10e-05 | 3.29e-05 |
| tacna_bge__gemma3-12b | 139 | 0.374 | 0.137 | 3.39e-06 | 1.36e-05 |

### Exactitud de estado temporal, propuesto contra cada corrida con llama3.1-8b (McNemar exacto, Holm)
| Corrida | n | propuesto | corrida | p | p Holm |
|---|---|---|---|---|---|
| hibrido_rr__llama3.1-8b | 139 | 0.317 | 0.345 | 3.44e-01 | 1.00e+00 |
| ingenuo__llama3.1-8b | 139 | 0.317 | 0.367 | 1.43e-01 | 7.17e-01 |
| propuesto_det__llama3.1-8b | 139 | 0.317 | 0.561 | 5.40e-09 | 4.86e-08 |
| propuesto_sincompuerta__llama3.1-8b | 139 | 0.317 | 0.367 | 1.56e-02 | 1.09e-01 |
| propuesto_sincompuerta_det__llama3.1-8b | 139 | 0.317 | 0.612 | 5.89e-11 | 5.89e-10 |
| propuesto_sinvigencia__llama3.1-8b | 139 | 0.317 | 0.317 | 1.00e+00 | 1.00e+00 |
| propuesto_sinvigencia_det__llama3.1-8b | 139 | 0.317 | 0.554 | 2.50e-07 | 2.00e-06 |
| recencia__llama3.1-8b | 139 | 0.317 | 0.324 | 1.00e+00 | 1.00e+00 |
| tacna_bge__llama3.1-8b | 139 | 0.317 | 0.331 | 8.83e-01 | 1.00e+00 |
| tacna_minilm__llama3.1-8b | 139 | 0.317 | 0.223 | 7.25e-02 | 4.35e-01 |

### Exactitud de estado temporal, propuesto_det contra cada corrida con gemma3-12b (McNemar exacto, Holm)
| Corrida | n | propuesto_det | corrida | p | p Holm |
|---|---|---|---|---|---|
| hibrido_rr__gemma3-12b | 139 | 0.518 | 0.302 | 2.83e-06 | 8.49e-06 |
| ingenuo__gemma3-12b | 139 | 0.518 | 0.309 | 8.96e-06 | 1.79e-05 |
| propuesto__gemma3-12b | 139 | 0.518 | 0.374 | 1.10e-05 | 1.79e-05 |
| tacna_bge__gemma3-12b | 139 | 0.518 | 0.137 | 7.34e-11 | 2.93e-10 |

### Exactitud de estado temporal, propuesto_det contra cada corrida con llama3.1-8b (McNemar exacto, Holm)
| Corrida | n | propuesto_det | corrida | p | p Holm |
|---|---|---|---|---|---|
| hibrido_rr__llama3.1-8b | 139 | 0.561 | 0.345 | 1.52e-05 | 9.13e-05 |
| ingenuo__llama3.1-8b | 139 | 0.561 | 0.367 | 3.55e-04 | 1.07e-03 |
| propuesto__llama3.1-8b | 139 | 0.561 | 0.317 | 5.40e-09 | 4.86e-08 |
| propuesto_sincompuerta__llama3.1-8b | 139 | 0.561 | 0.367 | 4.19e-05 | 2.10e-04 |
| propuesto_sincompuerta_det__llama3.1-8b | 139 | 0.561 | 0.612 | 1.18e-01 | 2.37e-01 |
| propuesto_sinvigencia__llama3.1-8b | 139 | 0.561 | 0.317 | 1.41e-07 | 1.12e-06 |
| propuesto_sinvigencia_det__llama3.1-8b | 139 | 0.561 | 0.554 | 1.00e+00 | 1.00e+00 |
| recencia__llama3.1-8b | 139 | 0.561 | 0.324 | 3.39e-06 | 2.37e-05 |
| tacna_bge__llama3.1-8b | 139 | 0.561 | 0.331 | 1.31e-04 | 5.23e-04 |
| tacna_minilm__llama3.1-8b | 139 | 0.561 | 0.223 | 4.04e-09 | 4.04e-08 |

### Matriz de confusión de estado, propuesto__gemma3-12b
| Estado oro | Estado predicho | n |
|---|---|---|
| vigente | vigente | 35 |
| premisa_falsa | vigente | 23 |
| sin_version | vigente | 17 |
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
| sin_version | vigente | 29 |
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
| sin_version | sin_version | 24 |
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
| premisa_falsa | vigente | 27 |
| sin_version | sin_version | 25 |
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
| sin_version | vigente | 36 |
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
| sin_version | sin_version | 27 |
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
| sin_version | vigente | 30 |
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
| sin_version | sin_version | 25 |
| premisa_falsa | vigente | 25 |
| no_existia | no_existia | 11 |
| premisa_falsa | fuera_corpus | 9 |
| sin_version | fuera_corpus | 8 |
| premisa_falsa | premisa_falsa | 8 |
| vigente | fuera_corpus | 5 |
| sin_version | vigente | 4 |
| no_existia | vigente | 3 |
| sin_version | no_existia | 2 |
| no_existia | fuera_corpus | 2 |

## Juez automático (muestra estratificada, partición test)
| Corrida | n | Corrección media | Totalmente correcta | Fidelidad |
|---|---|---|---|---|
| hibrido_rr__gemma3-12b | 95 | 0.558 | 0.547 | 0.599 |
| hibrido_rr__llama3.1-8b | 95 | 0.489 | 0.484 | 0.535 |
| ingenuo__gemma3-12b | 95 | 0.611 | 0.579 | 0.636 |
| ingenuo__llama3.1-8b | 92 | 0.495 | 0.467 | 0.523 |
| propuesto__gemma3-12b | 95 | 0.884 | 0.863 | 0.880 |
| propuesto__llama3.1-8b | 95 | 0.774 | 0.758 | 0.756 |
| recencia__llama3.1-8b | 95 | 0.500 | 0.474 | 0.595 |
| tacna_bge__gemma3-12b | 95 | 0.500 | 0.463 | 0.506 |
| tacna_bge__llama3.1-8b | 95 | 0.474 | 0.400 | 0.492 |
| tacna_minilm__llama3.1-8b | 95 | 0.474 | 0.421 | 0.458 |
