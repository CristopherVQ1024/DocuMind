# Resultados

| Tipo | Total | Test |
|---|---|---|
| literal | 120 | 98 |
| temporal | 120 | 98 |
| rastreo | 90 | 79 |
| multisalto | 86 | 69 |
| premisa_falsa | 90 | 70 |
| sin_respuesta | 90 | 73 |

## Recuperación (partición test, preguntas con evidencia)
| Sistema | n | Hit@1 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 | Todos@10 | s/consulta |
|---|---|---|---|---|---|---|---|---|
| recencia | 414 | 0.734 | 0.880 | 0.914 | 0.813 | 0.818 | 0.638 | 0.157 |
| hibrido_rr | 414 | 0.713 | 0.880 | 0.914 | 0.803 | 0.812 | 0.638 | 0.166 |
| propuesto | 414 | 0.713 | 0.880 | 0.914 | 0.803 | 0.812 | 0.638 | 0.159 |
| hibrido_rr_trozos | 414 | 0.710 | 0.877 | 0.913 | 0.801 | 0.809 | 0.623 | 0.188 |
| denso | 414 | 0.594 | 0.760 | 0.812 | 0.683 | 0.699 | 0.609 | 0.007 |
| hibrido | 414 | 0.585 | 0.755 | 0.822 | 0.676 | 0.695 | 0.594 | 0.008 |
| bm25 | 414 | 0.488 | 0.707 | 0.789 | 0.602 | 0.632 | 0.580 | 0.004 |
| tacna_bge | 414 | 0.577 | 0.646 | 0.664 | 0.628 | 0.614 | 0.507 | 0.999 |
| denso_sin_cabecera | 414 | 0.505 | 0.684 | 0.727 | 0.599 | 0.612 | 0.507 | 0.008 |
| ingenuo | 414 | 0.353 | 0.571 | 0.650 | 0.461 | 0.489 | 0.449 | 0.040 |
| tacna_minilm | 414 | 0.420 | 0.420 | 0.434 | 0.440 | 0.417 | 0.174 | 1.023 |

### Recall@5 por tipo de pregunta
| Sistema | literal | temporal | rastreo | multisalto | premisa_falsa |
|---|---|---|---|---|---|
| bm25 | 0.663 | 0.755 | 0.671 | 0.703 | 0.743 |
| denso | 0.908 | 0.949 | 0.405 | 0.703 | 0.743 |
| denso_sin_cabecera | 0.878 | 0.908 | 0.114 | 0.681 | 0.743 |
| hibrido | 0.827 | 0.867 | 0.532 | 0.717 | 0.786 |
| hibrido_rr | 0.969 | 0.918 | 0.873 | 0.746 | 0.843 |
| hibrido_rr_trozos | 0.959 | 0.929 | 0.886 | 0.739 | 0.814 |
| ingenuo | 0.806 | 0.755 | 0.101 | 0.558 | 0.529 |
| propuesto | 0.969 | 0.918 | 0.873 | 0.746 | 0.843 |
| recencia | 0.949 | 0.918 | 0.911 | 0.746 | 0.829 |
| tacna_bge | 0.888 | 0.061 | 0.886 | 0.688 | 0.814 |
| tacna_minilm | 0.510 | 0.031 | 0.835 | 0.377 | 0.414 |

### Diferencia de nDCG@10: hibrido_rr menos cada sistema (Wilcoxon, IC bootstrap 95 %, Holm)
| Sistema | Δ media | IC 95 % | p | p Holm |
|---|---|---|---|---|
| ingenuo | 0.323 | [0.285, 0.361] | 1.26e-40 | 1.26e-39 |
| tacna_minilm | 0.395 | [0.347, 0.442] | 3.96e-37 | 3.56e-36 |
| denso_sin_cabecera | 0.200 | [0.164, 0.237] | 1.37e-20 | 1.09e-19 |
| bm25 | 0.180 | [0.147, 0.214] | 3.67e-20 | 2.57e-19 |
| tacna_bge | 0.198 | [0.156, 0.242] | 6.70e-15 | 4.02e-14 |
| denso | 0.113 | [0.082, 0.144] | 1.33e-10 | 6.63e-10 |
| hibrido | 0.117 | [0.086, 0.150] | 3.81e-09 | 1.52e-08 |
| hibrido_rr_trozos | 0.002 | [-0.011, 0.015] | 2.30e-02 | 6.91e-02 |
| recencia | -0.006 | [-0.016, 0.003] | 5.54e-01 | 1.00e+00 |
| propuesto | 0.000 | [0.000, 0.000] | 1.00e+00 | 1.00e+00 |

## Generación (partición test)
| Corrida | n | Cita P | Cita R | Estado ok | Anacronismo | Rastreo ok | Abst P | Abst R | Abst F1 | JSON ok | s/resp | tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hibrido_rr__gemma3-12b | 487 | 0.637 | 0.673 | 0.256 | 0.875 | 0.127 | 0.543 | 0.521 | 0.531 | 1.000 | 6.923 | 1819.628 |
| hibrido_rr__llama3.1-8b | 487 | 0.622 | 0.659 | 0.298 | 0.898 | 0.114 | 0.556 | 0.205 | 0.300 | 1.000 | 1.831 | 1990.398 |
| ingenuo__gemma3-12b | 487 | 0.360 | 0.374 | 0.268 | 0.781 | 0.038 | 0.344 | 0.425 | 0.380 | 1.000 | 7.376 | 1637.809 |
| ingenuo__llama3.1-8b | 487 | 0.353 | 0.377 | 0.333 | 0.852 | 0.013 | 0.186 | 0.110 | 0.138 | 1.000 | 1.673 | 1793.895 |
| propuesto__gemma3-12b | 487 | 0.668 | 0.715 | 0.333 | 0.516 | 0.823 | 0.587 | 0.877 | 0.703 | 1.000 | 7.189 | 1683.359 |
| propuesto__llama3.1-8b | 487 | 0.657 | 0.687 | 0.280 | 0.688 | 0.759 | 0.616 | 0.836 | 0.709 | 1.000 | 1.607 | 1786.665 |
| propuesto_det__gemma3-12b | 487 | 0.668 | 0.715 | 0.464 | 0.359 | 0.823 | 0.587 | 0.877 | 0.703 | 1.000 | 7.189 | 1683.359 |
| propuesto_det__llama3.1-8b | 487 | 0.657 | 0.687 | 0.506 | 0.375 | 0.759 | 0.616 | 0.836 | 0.709 | 1.000 | 1.607 | 1786.665 |
| propuesto_sincompuerta__llama3.1-8b | 487 | 0.685 | 0.715 | 0.333 | 0.875 | 0.759 | 0.778 | 0.192 | 0.308 | 1.000 | 4.541 | 2188.994 |
| propuesto_sincompuerta_det__llama3.1-8b | 487 | 0.685 | 0.715 | 0.560 | 0.547 | 0.759 | 0.778 | 0.192 | 0.308 | 1.000 | 4.541 | 2188.994 |
| propuesto_sinvigencia__llama3.1-8b | 487 | 0.564 | 0.600 | 0.274 | 0.703 | 0.114 | 0.561 | 0.822 | 0.667 | 1.000 | 3.832 | 1622.852 |
| propuesto_sinvigencia_det__llama3.1-8b | 487 | 0.564 | 0.600 | 0.506 | 0.352 | 0.114 | 0.561 | 0.822 | 0.667 | 1.000 | 3.832 | 1622.852 |
| recencia__llama3.1-8b | 487 | 0.632 | 0.671 | 0.286 | 0.930 | 0.089 | 0.613 | 0.260 | 0.365 | 1.000 | 1.899 | 2112.793 |
| tacna_bge__gemma3-12b | 487 | 0.464 | 0.478 | 0.125 | 0.477 | 0.038 | 0.196 | 0.479 | 0.278 | 1.000 | 5.670 | 1194.142 |
| tacna_bge__llama3.1-8b | 487 | 0.498 | 0.511 | 0.304 | 0.578 | 0.038 | 0.238 | 0.137 | 0.174 | 1.000 | 1.446 | 1299.197 |
| tacna_minilm__llama3.1-8b | 487 | 0.365 | 0.351 | 0.226 | 0.547 | 0.038 | 0.312 | 0.342 | 0.327 | 1.000 | 1.306 | 1122.517 |

### Exactitud de estado temporal, propuesto contra cada corrida con gemma3-12b (McNemar exacto, Holm)
| Corrida | n | propuesto | corrida | p | p Holm |
|---|---|---|---|---|---|
| hibrido_rr__gemma3-12b | 168 | 0.333 | 0.256 | 2.41e-02 | 4.82e-02 |
| ingenuo__gemma3-12b | 168 | 0.333 | 0.268 | 7.08e-02 | 7.08e-02 |
| propuesto_det__gemma3-12b | 168 | 0.333 | 0.464 | 2.98e-06 | 1.19e-05 |
| tacna_bge__gemma3-12b | 168 | 0.333 | 0.125 | 3.31e-06 | 1.19e-05 |

### Exactitud de estado temporal, propuesto contra cada corrida con llama3.1-8b (McNemar exacto, Holm)
| Corrida | n | propuesto | corrida | p | p Holm |
|---|---|---|---|---|---|
| hibrido_rr__llama3.1-8b | 168 | 0.280 | 0.298 | 6.07e-01 | 1.00e+00 |
| ingenuo__llama3.1-8b | 168 | 0.280 | 0.333 | 1.08e-01 | 6.47e-01 |
| propuesto_det__llama3.1-8b | 168 | 0.280 | 0.506 | 4.11e-10 | 3.70e-09 |
| propuesto_sincompuerta__llama3.1-8b | 168 | 0.280 | 0.333 | 3.91e-03 | 2.73e-02 |
| propuesto_sincompuerta_det__llama3.1-8b | 168 | 0.280 | 0.560 | 1.18e-12 | 1.18e-11 |
| propuesto_sinvigencia__llama3.1-8b | 168 | 0.280 | 0.274 | 1.00e+00 | 1.00e+00 |
| propuesto_sinvigencia_det__llama3.1-8b | 168 | 0.280 | 0.506 | 1.37e-08 | 1.09e-07 |
| recencia__llama3.1-8b | 168 | 0.280 | 0.286 | 1.00e+00 | 1.00e+00 |
| tacna_bge__llama3.1-8b | 168 | 0.280 | 0.304 | 6.83e-01 | 1.00e+00 |
| tacna_minilm__llama3.1-8b | 168 | 0.280 | 0.226 | 2.81e-01 | 1.00e+00 |

### Exactitud de estado temporal, propuesto_det contra cada corrida con gemma3-12b (McNemar exacto, Holm)
| Corrida | n | propuesto_det | corrida | p | p Holm |
|---|---|---|---|---|---|
| hibrido_rr__gemma3-12b | 168 | 0.464 | 0.256 | 3.62e-07 | 1.09e-06 |
| ingenuo__gemma3-12b | 168 | 0.464 | 0.268 | 3.39e-06 | 5.96e-06 |
| propuesto__gemma3-12b | 168 | 0.464 | 0.333 | 2.98e-06 | 5.96e-06 |
| tacna_bge__gemma3-12b | 168 | 0.464 | 0.125 | 3.54e-11 | 1.42e-10 |

### Exactitud de estado temporal, propuesto_det contra cada corrida con llama3.1-8b (McNemar exacto, Holm)
| Corrida | n | propuesto_det | corrida | p | p Holm |
|---|---|---|---|---|---|
| hibrido_rr__llama3.1-8b | 168 | 0.506 | 0.298 | 3.31e-06 | 1.99e-05 |
| ingenuo__llama3.1-8b | 168 | 0.506 | 0.333 | 4.22e-04 | 1.27e-03 |
| propuesto__llama3.1-8b | 168 | 0.506 | 0.280 | 4.11e-10 | 4.11e-09 |
| propuesto_sincompuerta__llama3.1-8b | 168 | 0.506 | 0.333 | 3.85e-05 | 1.92e-04 |
| propuesto_sincompuerta_det__llama3.1-8b | 168 | 0.506 | 0.560 | 4.90e-02 | 9.81e-02 |
| propuesto_sinvigencia__llama3.1-8b | 168 | 0.506 | 0.274 | 4.00e-08 | 3.60e-07 |
| propuesto_sinvigencia_det__llama3.1-8b | 168 | 0.506 | 0.506 | 1.00e+00 | 1.00e+00 |
| recencia__llama3.1-8b | 168 | 0.506 | 0.286 | 1.97e-06 | 1.38e-05 |
| tacna_bge__llama3.1-8b | 168 | 0.506 | 0.304 | 1.83e-04 | 7.32e-04 |
| tacna_minilm__llama3.1-8b | 168 | 0.506 | 0.226 | 1.43e-07 | 1.14e-06 |

### Matriz de confusión de estado, propuesto__gemma3-12b
| Estado oro | Estado predicho | n |
|---|---|---|
| premisa_falsa | vigente | 37 |
| vigente | vigente | 35 |
| premisa_falsa | fuera_corpus | 23 |
| sin_version | vigente | 19 |
| sin_version | fuera_corpus | 11 |
| sin_version | sin_version | 8 |
| no_existia | vigente | 8 |
| no_existia | no_existia | 5 |
| vigente | fuera_corpus | 5 |
| derogado | derogado | 4 |
| premisa_falsa | premisa_falsa | 4 |
| sin_version | no_existia | 3 |

### Matriz de confusión de estado, propuesto__llama3.1-8b
| Estado oro | Estado predicho | n |
|---|---|---|
| premisa_falsa | vigente | 40 |
| vigente | vigente | 35 |
| sin_version | vigente | 31 |
| premisa_falsa | fuera_corpus | 18 |
| no_existia | vigente | 15 |
| sin_version | fuera_corpus | 8 |
| premisa_falsa | premisa_falsa | 6 |
| vigente | fuera_corpus | 5 |
| derogado | derogado | 4 |
| sin_version | sin_version | 2 |
| no_existia | fuera_corpus | 2 |
| derogado | vigente | 2 |

### Matriz de confusión de estado, propuesto_det__gemma3-12b
| Estado oro | Estado predicho | n |
|---|---|---|
| premisa_falsa | vigente | 37 |
| vigente | vigente | 35 |
| sin_version | sin_version | 26 |
| premisa_falsa | fuera_corpus | 23 |
| sin_version | fuera_corpus | 11 |
| no_existia | no_existia | 8 |
| vigente | fuera_corpus | 5 |
| derogado | derogado | 5 |
| sin_version | vigente | 4 |
| no_existia | vigente | 4 |
| premisa_falsa | premisa_falsa | 4 |
| no_existia | sin_version | 3 |

### Matriz de confusión de estado, propuesto_det__llama3.1-8b
| Estado oro | Estado predicho | n |
|---|---|---|
| premisa_falsa | vigente | 40 |
| vigente | vigente | 33 |
| sin_version | sin_version | 27 |
| premisa_falsa | fuera_corpus | 18 |
| no_existia | no_existia | 13 |
| sin_version | fuera_corpus | 8 |
| sin_version | vigente | 6 |
| derogado | derogado | 6 |
| premisa_falsa | premisa_falsa | 6 |
| vigente | fuera_corpus | 5 |
| no_existia | fuera_corpus | 2 |
| no_existia | vigente | 2 |

### Matriz de confusión de estado, propuesto_sincompuerta__llama3.1-8b
| Estado oro | Estado predicho | n |
|---|---|---|
| premisa_falsa | vigente | 55 |
| vigente | vigente | 40 |
| sin_version | vigente | 38 |
| no_existia | vigente | 17 |
| premisa_falsa | premisa_falsa | 9 |
| derogado | derogado | 4 |
| sin_version | sin_version | 3 |
| derogado | vigente | 2 |

### Matriz de confusión de estado, propuesto_sincompuerta_det__llama3.1-8b
| Estado oro | Estado predicho | n |
|---|---|---|
| premisa_falsa | vigente | 55 |
| vigente | vigente | 38 |
| sin_version | sin_version | 29 |
| no_existia | no_existia | 12 |
| sin_version | vigente | 11 |
| premisa_falsa | premisa_falsa | 9 |
| derogado | derogado | 6 |
| no_existia | vigente | 4 |
| sin_version | no_existia | 1 |
| no_existia | sin_version | 1 |
| vigente | sin_version | 1 |
| vigente | no_existia | 1 |

### Matriz de confusión de estado, propuesto_sinvigencia__llama3.1-8b
| Estado oro | Estado predicho | n |
|---|---|---|
| premisa_falsa | vigente | 38 |
| vigente | vigente | 35 |
| sin_version | vigente | 32 |
| premisa_falsa | fuera_corpus | 16 |
| no_existia | vigente | 15 |
| premisa_falsa | premisa_falsa | 10 |
| sin_version | fuera_corpus | 8 |
| vigente | fuera_corpus | 5 |
| derogado | vigente | 5 |
| no_existia | fuera_corpus | 2 |
| sin_version | sin_version | 1 |
| derogado | sin_version | 1 |

### Matriz de confusión de estado, propuesto_sinvigencia_det__llama3.1-8b
| Estado oro | Estado predicho | n |
|---|---|---|
| premisa_falsa | vigente | 38 |
| vigente | vigente | 32 |
| sin_version | sin_version | 26 |
| premisa_falsa | fuera_corpus | 16 |
| no_existia | no_existia | 11 |
| premisa_falsa | premisa_falsa | 10 |
| sin_version | fuera_corpus | 8 |
| derogado | derogado | 6 |
| vigente | fuera_corpus | 5 |
| sin_version | vigente | 4 |
| sin_version | no_existia | 3 |
| no_existia | vigente | 3 |

## Juez automático (muestra estratificada, partición test)
| Corrida | n | Corrección media | Totalmente correcta | Fidelidad |
|---|---|---|---|---|
| hibrido_rr__gemma3-12b | 120 | 0.487 | 0.467 | 0.537 |
| hibrido_rr__llama3.1-8b | 120 | 0.442 | 0.425 | 0.476 |
| ingenuo__gemma3-12b | 120 | 0.533 | 0.492 | 0.559 |
| ingenuo__llama3.1-8b | 117 | 0.449 | 0.410 | 0.463 |
| propuesto__gemma3-12b | 120 | 0.829 | 0.808 | 0.826 |
| propuesto__llama3.1-8b | 120 | 0.696 | 0.667 | 0.681 |
| recencia__llama3.1-8b | 120 | 0.446 | 0.408 | 0.521 |
| tacna_bge__gemma3-12b | 120 | 0.467 | 0.425 | 0.476 |
| tacna_bge__llama3.1-8b | 120 | 0.412 | 0.333 | 0.427 |
| tacna_minilm__llama3.1-8b | 120 | 0.433 | 0.375 | 0.428 |
