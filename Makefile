.PHONY: help Makefile clean clean-tests reports clean-reports reporttodo reportfix

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean: clean-tests
	-rm source/*.pyc
	-rm source/__pycache__/*.pyc
	-rmdir source/__pycache__
	-rm source/pyscribus/*.pyc
	-rm source/pyscribus/__pycache__/*.pyc
	-rmdir source/pyscribus/__pycache__
	-rm source/pyscribus/common/*.pyc
	-rm source/pyscribus/common/__pycache__/*.pyc
	-rmdir source/pyscribus/common/__pycache__
	-rm source/pyscribus/papers/*.pyc
	-rm source/pyscribus/papers/__pycache__/*.pyc
	-rmdir source/pyscribus/papers/__pycache__

clean-tests:
	-rm source/tests-outputs/*

reports: reporttodo reportfix

clean-reports:
	-rm thingstodo.txt
	-rm thingstofix.txt

reporttodo:
	grep -n "TODO" source/pyscribus/*.py > thingstodo.txt

reportfix:
	grep -n "FIXME" source/pyscribus/*.py > thingstofix.txt

sphinxdoc:
	sphinx-build -b html source/ build/

pipinstall:
	pip3 uninstall --index-url https://test.pypi.org/simple/ --no-deps pyscribus

pipremove:
	pip3 uninstall pyscribus

package:
	./make-pypi.sh

pypupload:
	./upload-pypitesting.sh
