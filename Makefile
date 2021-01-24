VERSION = $(shell cat VERSION)

.PHONY: build
build:
	docker build -t inosion/prometheus-sunspec-exporter:$(VERSION) .

release:
	docker save inosion/prometheus-sunspec-exporter:$(VERSION) | gzip > inosion-prometheus-sunspec-exporter-$(VERSION).tgz