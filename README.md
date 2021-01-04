# THIS IS A FORK - See https://framagit.org/etnadji/pyscribus

# PyScribus

**Branche principale, >= Python 3.8** | 
**Main branch, >= Python 3.8**

Une librairie Python pour manipuler (et documenter) 
le format de Scribus, le SLA.

## Obtenir PyScribus

```bash
pip3 install pyscribus
```

### Pré-requis

- [lxml](https://lxml.de/)
- [svg.path](https://pypi.org/project/svg.path/)
- [Pillow](https://python-pillow.org/), optionnel, pour le module ``extra.wireframe``

#### Debian / Ubuntu

```bash
sudo apt install python3 python3-lxml
sudo pip3 install svg.path
```

## Documentation

[La documentation](https://etnadji.fr/pyscribus) est générée 
via Sphinx, avec le thème *Read the Docs*.

```bash
make sphinxdoc
```

### Pré-requis

#### Debian / Ubuntu

```bash
sudo apt install python3-sphinx python3-sphinx-rtd-theme
```

## Documentation externe

### Le format SLA

[File Format Specification for Scribus 1.5](https://wiki.scribus.net/canvas/File_Format_Specification_for_Scribus_1.5)

- [Liste des elements/attributs documentables](source/articles/en/spec.rst) trouvés lors de l’écriture de cette librairie.

## Avancement

- [ ] **en cours** Analyse (*parsing*) totale
  - [ ] Objets Python cohérents
  - [ ] Import et export XML
- [ ] Fonctions de haut niveau

