# PyScribus

Une librairie Python pour manipuler (et documenter) le format de Scribus, le SLA.

## Avancement

- [ ] **en cours** Analyse (*parsing*) totale
  - [ ] Objets Python cohérents
  - [ ] Import et export XML
- [ ] Fonctions de haut niveau

## Pré-requis

- [lxml](https://lxml.de/)
- [Pillow](https://python-pillow.org/), optionnel, pour le module ``extra.wireframe``

### Debian / Ubuntu

```python
sudo apt install python3 python3-lxml
```

## Documentation

La documentation est générée via Sphinx, avec le thème *Read the Docs*.

```bash
make sphinxdoc
```

### Pré-requis

#### Debian / Ubuntu

```python
sudo apt install python3-sphinx python3-sphinx-rtd-theme
```

## Documentation externe

### Le format SLA

[File Format Specification for Scribus 1.5](https://wiki.scribus.net/canvas/File_Format_Specification_for_Scribus_1.5)

- [Liste des elements/attributs documentables](source/articles/en/spec.rst) trouvés lors de l’écriture de cette librairie.

