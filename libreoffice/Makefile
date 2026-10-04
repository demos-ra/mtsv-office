OXT = build/mtsv-office.oxt
PACKAGE = build/oxt
SOURCES = src/META-INF/manifest.xml src/description.xml src/Types.xcu \
	src/Filter.xcu src/filter.py src/extended_type_detection.py \
	src/pythonpath/mtsv_office.py README.md Makefile ../LICENSE
MTSV = 0.7.0

.PHONY: all check clean

all: $(OXT)

$(OXT): $(SOURCES)
	rm -rf $(PACKAGE) $(OXT) build/venv
	mkdir -p $(PACKAGE)/description
	cp -R src/META-INF src/description.xml src/Types.xcu src/Filter.xcu \
		src/filter.py src/extended_type_detection.py ../LICENSE $(PACKAGE)/
	python3 -m venv build/venv
	build/venv/bin/pip install --target $(PACKAGE)/pythonpath --no-deps \
		--no-compile mtsv==$(MTSV)
	rm -rf $(PACKAGE)/pythonpath/bin
	cp src/pythonpath/mtsv_office.py $(PACKAGE)/pythonpath/
	awk '/^#/ { next } NF { print; found = 1; next } found { exit }' \
		README.md > $(PACKAGE)/description/desc_en.txt
	cd $(PACKAGE) && python3 -m zipfile -c ../mtsv-office.oxt META-INF \
		description pythonpath description.xml Types.xcu Filter.xcu \
		filter.py extended_type_detection.py LICENSE

check: all build/mtsv
	PYTHONPATH=$(CURDIR)/$(PACKAGE)/pythonpath python3 -m unittest discover \
		-s tests

build/mtsv:
	git clone --depth 1 --branch v$(MTSV) https://github.com/demos-ra/mtsv \
		build/mtsv

clean:
	rm -rf build
